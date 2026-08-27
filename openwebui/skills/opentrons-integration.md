---
name: opentrons-integration
description: Author, review, migrate, simulate, and troubleshoot official Opentrons Python Protocol API v2 protocols for Flex and OT-2 robots. Use for robot-specific liquid handling, deck and labware setup, pipettes, modules, runtime parameters, liquid classes, and Opentrons App analysis. Use pylabrobot instead when one workflow must support multiple robot vendors.
---

# Opentrons Integration

## Overview

Create production-minded Python Protocol API v2 protocols for Opentrons Flex and
OT-2. This skill covers protocol structure, hardware and deck configuration,
liquid handling, runtime customization, module control, simulation, and safe
deployment.

The verified baseline as of **2026-07-23** is:

- `opentrons==9.1.1` for reproducible Flex simulation.
- `opentrons==9.0.0` for local OT-2 API 2.28 compatibility simulation.
- Flex supports API levels 2.15 through 2.29 on current software.
- OT-2 supports API levels 2.0 through 2.28 on current software.
- API 2.29 is Flex-only at this baseline. Do not put `2.29` in an OT-2 protocol.

Read `references/sources.md` for the upstream documentation used for this
snapshot. Recheck the official versioning page before targeting newer robot
software.

## Safety Boundary

Opentrons protocols control physical equipment. Never treat successful Python
syntax or local simulation as permission to run on a robot.

Before live execution:

1. Simulate locally with the same pinned `opentrons` version used for authoring.
2. Import the protocol into the correct Opentrons App and require successful
   analysis.
3. Verify robot model, software, pipettes, mounts, modules, adapters, labware
   definitions, deck fixtures, tip count, source volumes, dead volumes, and
   destination capacity.
4. Review the run preview and deck map with the operator.
5. Perform a slow dry run with nonhazardous liquid when geometry, custom
   labware, partial tip pickup, or gripper moves are new.
6. Keep the emergency stop accessible and follow site-specific biosafety,
   chemical-safety, and contamination-control procedures.

Simulation cannot verify physical calibration, liquid properties, meniscus
behavior, labware manufacturing tolerances, cap or seal removal, tubing, or all
possible collisions.

## Choose the Right Interface

Use this skill for Python files imported into the Opentrons App and run through
the Protocol API.

- Use **Protocol Designer** for supported no-code workflows.
- Use **PyLabRobot** for a hardware-agnostic workflow spanning vendors.
- Treat the robot's HTTP API as a separate integration surface. If direct HTTP
  control is explicitly required, use the OpenAPI document served by the target
  robot and do not infer endpoints from Protocol API methods.

## Required Intake

Do not write final protocol code until these facts are known:

- Robot: Flex or OT-2, plus installed robot software.
- Pipette model, volume range, channel count, and mount.
- Modules and generations; Flex Gripper or Stacker availability.
- Exact labware API load names and custom definition files, if any.
- Deck fixtures: Flex trash bin, waste chute, staging slots, or Stackers.
- Source volumes, destination volumes, dead volume, mixing needs, and liquid
  characteristics.
- Tip policy: contamination boundaries, reuse policy, filters, partial pickup,
  and total tips.
- Operator interventions, incubation timing, runtime parameters, and output
  files.
- Acceptance criteria: tolerated volume error, required controls, and dry-run
  plan.

If any physical configuration is uncertain, produce a parameterized draft and
an explicit assumptions list rather than guessing.

## Install and Simulate

Flex:

```bash
uv run --with "opentrons==9.1.1" opentrons_simulate protocol.py
```

OT-2 API 2.28:

```bash
uv run --with "opentrons==9.0.0" opentrons_simulate protocol.py
```

The 9.1.1 package intentionally rejects OT-2 protocols after the Flex/OT-2
release-line split. Always complete OT-2 analysis in the current OT-2 App.

For a dedicated Flex environment:

```bash
uv venv --python 3.10
uv pip install --python .venv/bin/python -r skills/opentrons-integration/requirements-flex.txt
.venv/bin/opentrons_simulate protocol.py
```

Use `requirements-ot2.txt` instead for an OT-2 compatibility environment. On
Windows, invoke the executable from `.venv\Scripts\opentrons_simulate.exe`.
Local simulation is for Python protocols; import Protocol Designer JSON files
into the appropriate Opentrons App instead.

## Protocol Skeletons

### Flex, API 2.29

For Flex, `requirements` is mandatory. Put `apiLevel` only in `requirements`,
not in both `metadata` and `requirements`.

```python
from opentrons import protocol_api

metadata = {
    "protocolName": "Flex transfer",
    "author": "Your Name",
    "description": "Transfer buffer into a plate.",
}
requirements = {"robotType": "Flex", "apiLevel": "2.29"}


def run(protocol: protocol_api.ProtocolContext) -> None:
    tips = protocol.load_labware(
        "opentrons_flex_96_tiprack_200ul", "D1"
    )
    reservoir = protocol.load_labware("nest_12_reservoir_15ml", "D2")
    plate = protocol.load_labware("nest_96_wellplate_200ul_flat", "C2")
    protocol.load_trash_bin("A3")
    pipette = protocol.load_instrument(
        "flex_1channel_1000", "left", tip_racks=[tips]
    )

    pipette.transfer(
        100,
        reservoir["A1"],
        plate["A1"],
        new_tip="always",
    )
```

### OT-2, API 2.28

For OT-2 API 2.15 and later, a `requirements` block is recommended. OT-2 has a
fixed trash in slot 12; do not call `load_trash_bin()`.

```python
from opentrons import protocol_api

metadata = {
    "protocolName": "OT-2 transfer",
    "author": "Your Name",
}
requirements = {"robotType": "OT-2", "apiLevel": "2.28"}


def run(protocol: protocol_api.ProtocolContext) -> None:
    tips = protocol.load_labware("opentrons_96_tiprack_300ul", "1")
    reservoir = protocol.load_labware("nest_12_reservoir_15ml", "2")
    plate = protocol.load_labware("nest_96_wellplate_200ul_flat", "3")
    pipette = protocol.load_instrument(
        "p300_single_gen2", "left", tip_racks=[tips]
    )
    pipette.transfer(100, reservoir["A1"], plate["A1"])
```

Use the lowest API level that provides every required feature when a protocol
must run across a mixed software fleet. Use the current maximum only when the
workflow needs its behavior or capabilities.

## Authoring Workflow

### 1. Select robot and API level

Check the maximum supported API in the App under the robot's advanced settings.
Map every requested feature to its minimum API level using
`references/api_reference.md`.

Important gates:

- 2.20: CSV runtime parameters, liquid presence detection, expanded partial
  nozzle layouts.
- 2.21: Absorbance Plate Reader.
- 2.22: current labware-level liquid loading methods.
- 2.23: meniscus locations and labware lids.
- 2.24: liquid classes and liquid-class complex commands.
- 2.25: Flex Stacker and Flex 96-Channel 200 µL pipette.
- 2.27: dynamic pipetting and concurrent module actions.
- 2.28: 20 µL Flex tips, improved partial-tip return, and thermocycler ramp rate.
- 2.29: step grouping; Flex only at the verified baseline.

### 2. Build the deck explicitly

- Use exact load names from the official Labware Library.
- Load Flex trash bins or the waste chute explicitly.
- Account for module footprints, staging slots, Stacker shuttles, gripper paths,
  and tall-labware adjacency.
- Load labware on adapters or module contexts in the documented order.
- Never substitute a similarly named labware definition; geometry and offsets
  are part of the protocol's safety model.

See `references/modules_and_deck.md`.

### 3. Select pipettes and tips

Current load names are:

- Flex: `flex_1channel_50`, `flex_1channel_1000`,
  `flex_8channel_50`, `flex_8channel_1000`,
  `flex_96channel_200`, `flex_96channel_1000`.
- OT-2 GEN2: `p20_single_gen2`, `p20_multi_gen2`,
  `p300_single_gen2`, `p300_multi_gen2`, `p1000_single_gen2`.

Check that every requested volume is within the configured pipette and tip
range. A 100 nL operation is not an Opentrons pipetting task.

### 4. Choose a liquid-handling layer

- Use `aspirate()`, `dispense()`, `mix()`, `air_gap()`, `blow_out()`, and
  `touch_tip()` for explicit control.
- Use `transfer()`, `distribute()`, and `consolidate()` for standard movements.
- On Flex, consider `transfer_with_liquid_class()`,
  `distribute_with_liquid_class()`, or `consolidate_with_liquid_class()` for
  Opentrons-verified aqueous, volatile, or viscous behavior.
- Use dynamic start/end locations or `dynamic_mix()` only when API 2.27+ and the
  geometry has been reviewed.

Model contamination boundaries before optimizing tips. Never reuse a tip across
unrelated samples merely to reduce consumables. See
`references/liquid_handling.md`.

### 5. Add setup information and runtime controls

Use `define_liquid()` and labware-level `load_liquid()` or
`load_liquid_by_well()` to improve setup visualization. Do not use deprecated
`Well.load_liquid()` in new API 2.22+ protocols.

Define operator-controlled values in `add_parameters()` and read them from
`protocol.params`. Validate ranges and use defaults that produce a safe,
meaningful simulation. CSV parameters have no default and only one CSV
parameter can be selected per run.

### 6. Budget resources

Before simulation, calculate:

- Tips or tip sets required under every branch.
- Source volume = delivered volume + mixing loss + disposal volume + dead
  volume + a justified reserve.
- Maximum destination volume after every addition and mix.
- Number of module, adapter, trash, and staging positions.
- Incubation and module timing, including concurrent tasks.

### 7. Validate in layers

1. Compile: `python -m py_compile protocol.py`.
2. Simulate with the pinned package.
3. Inspect the run log for command count, tip changes, pauses, and unexpected
   locations.
4. Import into the appropriate App and require successful analysis.
5. Check protocol visualization, runtime parameter defaults, deck map, module
   setup, and labware offsets.
6. Perform an operator-reviewed dry run before first use.

See `references/validation_and_operations.md`.

## Common Failure Modes

- Using old names such as `p300_single_flex`; use current `flex_*` load names.
- Declaring `apiLevel` in both `metadata` and `requirements`.
- Using API 2.29 for OT-2.
- Forgetting a Flex trash bin or waste chute.
- Loading a Magnetic Module on Flex; use supported Flex magnetic hardware.
- Calling `read(wavelengths=...)` on the plate reader; call `initialize()` first,
  then `read()`.
- Using deprecated `Well.load_liquid()` instead of labware-level methods.
- Assuming simulation verifies calibration, liquid height, or physical
  clearances.
- Passing an unsafe well to a partial-nozzle pipette, which can place tips
  outside labware and cause a crash.
- Using `new_tip="once"` across samples with incompatible contamination
  requirements.

## Bundled Templates

| File | Purpose |
| --- | --- |
| `scripts/basic_protocol_template.py` | Minimal Flex 2.29 transfer with current names |
| `scripts/ot2_basic_protocol_template.py` | Minimal OT-2 2.28 transfer |
| `scripts/serial_dilution_template.py` | Full-plate 1:2 dilution with an 8-channel Flex pipette |
| `scripts/pcr_setup_template.py` | Flex PCR setup and Thermocycler cycling |
| `scripts/runtime_parameters_template.py` | Safe numeric and Boolean runtime parameters |
| `scripts/absorbance_reader_template.py` | Correct Flex plate-reader initialization and read workflow |

Templates are starting points, not validated assays. Replace volumes, labware,
liquids, timing, and tip policies only after checking hardware compatibility and
the wet-lab method.

## Reference Guide

| Reference | Use it for |
| --- | --- |
| `references/api_reference.md` | Current load names, version gates, and high-value methods |
| `references/protocol_authoring.md` | Requirements, labware, runtime parameters, and design workflow |
| `references/liquid_handling.md` | Command selection, liquid classes, sensing, and partial tips |
| `references/modules_and_deck.md` | Module compatibility, deck fixtures, gripper, and Stacker |
| `references/validation_and_operations.md` | Simulation, App analysis, dry runs, and troubleshooting |
| `references/migration-api-2-19-to-2-29.md` | Updating older protocols and this skill's former patterns |
| `references/sources.md` | Official documentation and release sources |

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/opentrons-integration/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/api_reference.md`

# Opentrons Protocol API v2 Quick Reference

Verified against `opentrons==9.1.1` and the official documentation on
2026-07-23. This is a curated authoring reference, not a replacement for the
[ProtocolContext API reference](https://docs.opentrons.com/python-api/reference/protocols/)
and its linked class references.

## Version Baseline

| Robot | Supported API range on current software | Recommended maximum for new robot-specific protocols |
| --- | --- | --- |
| Flex | 2.15–2.29 | 2.29 |
| OT-2 | 2.0–2.28 | 2.28 |

API versions are independent of the installed Python package and robot software.
Choose the lowest API level that includes every required feature. A protocol
specifying a higher level than the robot supports will fail analysis.

```python
metadata = {
    "protocolName": "Example",
    "author": "Your Name",
    "description": "Purpose and scope.",
}
requirements = {"robotType": "Flex", "apiLevel": "2.29"}
```

Rules:

- Flex always requires `requirements`.
- `requirements` is recommended for OT-2 protocols using API 2.15+.
- Put `apiLevel` in exactly one place. When using `requirements`, remove it from
  `metadata`.
- `run(protocol: protocol_api.ProtocolContext)` is the required entry point.

## Features Added After API 2.19

| API | High-value additions |
| --- | --- |
| 2.20 | CSV runtime parameters; liquid presence detection; row, single, and partial-column nozzle layouts |
| 2.21 | `AbsorbanceReaderContext` and `absorbanceReaderV1` |
| 2.22 | `Labware.load_liquid()`, `load_liquid_by_well()`, and `load_empty()`; robot motor control |
| 2.23 | `Well.meniscus()`; labware lids and lid moves |
| 2.24 | Liquid classes; advanced liquid-class complex commands; absolute flow-rate options |
| 2.25 | `FlexStackerContext`; `flexStackerModuleV1`; `flex_96channel_200` |
| 2.26 | Liquid-class support for `flex_96channel_200` |
| 2.27 | Concurrent module actions; dynamic aspirate, dispense, and mix; `capture_image()`; explicit liquid-class tips |
| 2.28 | Flex 20 µL tips; partial-tip return; thermocycler ramp rate; empty tip-rack tracking |
| 2.29 | Protocol step grouping |

See
[Versioning](https://docs.opentrons.com/python-api/versioning/) for complete
behavior changes and robot-software mappings.

## Pipette Load Names

### Flex

| Pipette | Nominal range | Load name |
| --- | ---: | --- |
| 1-Channel 50 µL | 1–50 µL | `flex_1channel_50` |
| 1-Channel 1000 µL | 5–1000 µL | `flex_1channel_1000` |
| 8-Channel 50 µL | 1–50 µL | `flex_8channel_50` |
| 8-Channel 1000 µL | 5–1000 µL | `flex_8channel_1000` |
| 96-Channel 200 µL | 1–200 µL | `flex_96channel_200` |
| 96-Channel 1000 µL | 5–1000 µL | `flex_96channel_1000` |

The 96-channel pipette occupies both mounts. From API 2.16 onward its `mount`
argument is optional.

### OT-2 GEN2

| Pipette | Nominal range | Load name |
| --- | ---: | --- |
| P20 single | 1–20 µL | `p20_single_gen2` |
| P20 multi | 1–20 µL | `p20_multi_gen2` |
| P300 single | 20–300 µL | `p300_single_gen2` |
| P300 multi | 20–300 µL | `p300_multi_gen2` |
| P1000 single | 100–1000 µL | `p1000_single_gen2` |

GEN1 OT-2 pipettes have different load names. Check
[Loading Pipettes](https://docs.opentrons.com/python-api/pipettes/loading/)
instead of guessing.

## Flex Tip Compatibility

| Pipette family | Compatible Flex tip-rack capacities |
| --- | --- |
| `flex_1channel_50`, `flex_8channel_50` | 20 µL, 50 µL |
| `flex_96channel_200` | 20 µL, 50 µL, 200 µL |
| `flex_1channel_1000`, `flex_8channel_1000`, `flex_96channel_1000` | 50 µL, 200 µL, 1000 µL |

Filter-tip load names insert `_filtertiprack_`, for example
`opentrons_flex_96_filtertiprack_200ul`.

Full-rack pickup by a Flex 96-channel pipette requires the Flex tip-rack
adapter. Partial pickup by that pipette must use a rack directly on the deck,
without the adapter.

## ProtocolContext

### Hardware and deck

```python
labware = protocol.load_labware(load_name, location, label=None)
adapter = protocol.load_adapter(load_name, location)
module = protocol.load_module(module_name, location=None)
pipette = protocol.load_instrument(
    instrument_name,
    mount,
    tip_racks=[tiprack],
)
trash = protocol.load_trash_bin("A3")  # Flex, API 2.16+
chute = protocol.load_waste_chute()     # Flex, fixed at D3
```

Useful methods:

- `load_labware_from_definition(definition, location, label=None)`
- `move_labware(labware, new_location, use_gripper=...)`
- `load_lid_stack(load_name, location, quantity)`
- `move_lid(source_location, new_location, use_gripper=...)`
- `define_liquid(name, description=None, display_color=None)`
- `get_liquid_class(name, version=None)` — API 2.24+
- `define_liquid_class(name, properties, display_name)` — API 2.24+

### Execution and organization

- `comment(msg)` — adds analysis-time text to the run log.
- `pause(msg=None)` — waits for the operator to resume in the App/touchscreen.
- `delay(seconds=0, minutes=0, msg=None)` — blocking delay.
- `home()` — homes robot axes.
- `is_simulating()` — identify local or App analysis.
- `group_steps(name, description=None)` — context manager, API 2.29.
- `create_and_start_step_group(name, description=None)` — returns a group whose
  `end_group()` method closes it, API 2.29.
- `capture_image()` — captures from the built-in camera, API 2.27.

Step groups only organize source and visualization; they do not change
execution.

## InstrumentContext

### Tips

```python
pipette.pick_up_tip()
pipette.drop_tip()
pipette.return_tip()
pipette.reset_tipracks()
```

In API 2.28+, `tiprack.set_empty()` can mark a rack empty so returned tips may be
tracked there. Only return tips when the protocol's contamination policy allows
it.

### Building-block commands

```python
pipette.aspirate(volume, source)
pipette.dispense(volume, destination, push_out=5)
pipette.air_gap(volume)
pipette.blow_out(destination.top())
pipette.touch_tip(destination)
pipette.mix(repetitions, volume, destination)
pipette.move_to(destination.top())
```

Use `rate=` as a multiplier of the pipette's configured flow rate, or supported
absolute flow-rate arguments when the API level provides them. Do not supply
both forms for the same action.

API 2.27 adds `end_location` and `movement_delay` to aspirate and dispense, plus
`dynamic_mix()` for start-to-end movement during repeated aspiration and
dispensing.

### Complex commands

```python
pipette.transfer(volume, source, destination, new_tip="always")
pipette.distribute(volume, source, destinations, new_tip="once")
pipette.consolidate(volume, sources, destination, new_tip="always")
```

Common options include:

- `new_tip`: `"always"`, `"once"`, or `"never"`; newer API levels add
  additional policies for some commands.
- `mix_before=(repetitions, volume)`
- `mix_after=(repetitions, volume)`
- `touch_tip=True`
- `blow_out=True`
- `blowout_location=...`
- `disposal_volume=...`
- `trash_location=...`

Supported options differ by command and API level. Check the exact signature in
the
[Instrument API reference](https://docs.opentrons.com/python-api/reference/instruments/)
before using uncommon options.

### Liquid-class commands, Flex only

```python
water = protocol.get_liquid_class("water")

pipette.transfer_with_liquid_class(
    liquid_class=water,
    volume=50,
    source=reservoir["A1"],
    dest=plate["A1"],
    new_tip="always",
    trash_location=trash,
)
```

Related methods are `distribute_with_liquid_class()` and
`consolidate_with_liquid_class()`. Opentrons-verified classes include water,
80% ethanol, and 50% glycerol. Compatibility depends on the exact Flex pipette
and tip combination.

## Labware and Wells

### Accessors

```python
plate["A1"]
plate.wells()
plate.wells_by_name()
plate.rows()
plate.rows_by_name()
plate.columns()
plate.columns_by_name()
```

Labware iteration is generally column-major. Use named wells or explicit lists
when order is safety-critical.

### Locations

```python
well.top(z=-1)
well.bottom(z=2)
well.center()
well.meniscus(z=0, target="start")  # API 2.23+
```

`meniscus()` depends on declared or measured liquid volume. Validate liquid
height behavior on hardware before relying on it for low-volume aspiration.

### Liquid setup visualization, API 2.22+

```python
buffer = protocol.define_liquid(
    name="Buffer",
    description="Assay buffer",
    display_color="#1F77B4",
)

reservoir.load_liquid(
    wells=["A1"],
    volume=10_000,
    liquid=buffer,
)

plate.load_liquid_by_well(
    volumes={"A1": 50, "B1": 50},
    liquid=buffer,
)

plate.load_empty(wells=["A2", "B2"])
```

`Well.load_liquid()` is deprecated for API 2.22+ protocols.

## Runtime Parameters

Define parameters outside `run()`:

```python
def add_parameters(parameters: protocol_api.ParameterContext) -> None:
    parameters.add_int(
        variable_name="sample_count",
        display_name="Sample count",
        default=8,
        minimum=1,
        maximum=96,
    )
    parameters.add_bool(
        variable_name="dry_run",
        display_name="Dry run",
        default=False,
    )
```

Read them during execution:

```python
sample_count = protocol.params.sample_count
dry_run = protocol.params.dry_run
```

Methods:

- `add_bool(...)`
- `add_int(...)`
- `add_float(...)`
- `add_str(...)`
- `add_csv_file(...)` — API 2.20+, no default, at most one CSV parameter per
  run.

Parameter display names are limited to 30 characters and descriptions to 100
characters. Numeric parameters require either a min/max range or fixed choices.

## Liquid Presence and Height

Flex pressure-sensing pipettes support:

- `detect_liquid_presence(well)`
- `require_liquid_presence(well)`
- `measure_liquid_height(well)`
- `liquid_presence_detection=True` in `load_instrument()`
- Runtime toggling with `pipette.liquid_presence_detection`

Detection requires a fresh, dry, empty tip. It can add substantial run time,
and not every channel on a multi-channel pipette contains a pressure sensor.

## Partial Nozzle Layouts

```python
from opentrons.protocol_api import ALL, COLUMN

pipette.configure_nozzle_layout(
    style=COLUMN,
    start="A12",
    tip_racks=[partial_tip_rack],
)

# Restore full-rack pickup later.
pipette.configure_nozzle_layout(
    style=ALL,
    tip_racks=[full_tip_rack],
)
```

Available constants include `ALL`, `COLUMN`, `ROW`, `SINGLE`, and
`PARTIAL_COLUMN`, subject to pipette and API support. An incorrect target well
can place nozzles outside the labware and cause a physical crash. Follow the
deck-edge and tip-rack-adapter rules in
[Partial Tip Pickup](https://docs.opentrons.com/python-api/pipettes/partial-tip-pickup/).

## Module Load Names

| Module | Load name | Minimum API |
| --- | --- | ---: |
| Temperature Module GEN1 | `temperature module` | 2.0 |
| Temperature Module GEN2 | `temperature module gen2` | 2.3 |
| Thermocycler GEN1 | `thermocycler module` | 2.0 |
| Thermocycler GEN2 | `thermocyclerModuleV2` | 2.13 |
| Heater-Shaker GEN1 | `heaterShakerModuleV1` | 2.13 |
| Magnetic Block GEN1 | `magneticBlockV1` | 2.15 |
| Absorbance Plate Reader | `absorbanceReaderV1` | 2.21 |
| Flex Stacker | `flexStackerModuleV1` | 2.25 |

Module availability also depends on robot model and physical generation. See
`modules_and_deck.md` before choosing a load name.

## Simulation Entrypoints

```bash
# Flex API 2.29
uv run --with "opentrons==9.1.1" opentrons_simulate protocol.py

# OT-2 API 2.28 compatibility simulation
uv run --with "opentrons==9.0.0" opentrons_simulate protocol.py
```

Python integrations may use `opentrons.simulate.simulate()` with an opened
protocol file. `opentrons==9.1.1` rejects OT-2 protocols after the release-line
split, so complete OT-2 validation in the current OT-2 App. Do not use
`opentrons_execute` from a workstation as a substitute for App analysis and
controlled robot operation.

### `references/liquid_handling.md`

# Liquid Handling Guide

Choose commands from the physical behavior the assay needs, not from which call
is shortest to write. Every command still depends on correct liquid volumes,
labware geometry, pipette range, tips, and contamination controls.

## Command Layers

### Building-block commands

Use when aspiration and dispensing need independent control:

```python
pipette.pick_up_tip()
pipette.aspirate(50, source.bottom(z=1), flow_rate=25)
protocol.delay(seconds=1)
pipette.dispense(50, destination.bottom(z=2), flow_rate=20, push_out=5)
pipette.blow_out(destination.top(z=-1))
pipette.drop_tip()
```

Advantages:

- Explicit position and order.
- Independent flow rates and delays.
- Fine control for viscous, volatile, foaming, low-volume, or bead workflows.

Costs:

- The author owns tip state and volume state.
- More opportunities to aspirate with no tip, overfill the pipette, or leave
  residual volume.

### Standard complex commands

Use for conventional source-to-destination mappings:

```python
pipette.transfer(
    volume=50,
    source=source_plate.wells()[:8],
    dest=destination_plate.wells()[:8],
    new_tip="always",
    mix_after=(3, 30),
)
```

- `transfer()`: one or more source-to-destination transfers.
- `distribute()`: one source to many destinations, normally with an excess
  disposal volume.
- `consolidate()`: many sources into one destination.

Inspect the simulation run log. Complex commands expand into many building
blocks, and their expansion changes with parameters and API level.

### Liquid-class complex commands, Flex API 2.24+

Use an Opentrons-verified class when the pipette/tip combination is supported
and the liquid resembles the verified model:

```python
viscous = protocol.get_liquid_class("glycerol_50")

pipette.transfer_with_liquid_class(
    liquid_class=viscous,
    volume=50,
    source=reservoir["A1"],
    dest=plate["A1"],
    new_tip="always",
    trash_location=trash,
)
```

Related methods:

- `distribute_with_liquid_class()`
- `consolidate_with_liquid_class()`

Verified classes include water, 80% ethanol, and 50% glycerol. A liquid class
controls multiple coupled properties such as flow rate, submerge and retract
behavior, delays, air gaps, positions, and push-out. Do not casually override
one property without testing the full result.

Opentrons-verified liquid classes are for supported Flex pipette and tip
combinations, not OT-2 pipettes.

## Source and Destination Mapping

Complex commands accept a single well or a sequence. Make the intended mapping
explicit:

- One source, one destination: one transfer.
- One source, many destinations: repeated transfers or a distribution.
- Many sources, one destination: repeated transfers or a consolidation.
- Equal-length source and destination lists: pairwise transfers.

Do not assume row-major ordering:

```python
# Explicit sample order is easier to audit.
sample_wells = [plate[name] for name in ("A1", "B1", "C1", "D1")]
```

For multi-channel pipettes, the referenced well anchors the pipette's primary
channel:

- A full 8-channel pipette normally targets an entire column by referencing its
  A-row well.
- A full 96-channel pipette addresses an entire 96-well rack or plate.
- A partial-column layout has a different primary channel; follow the layout
  documentation rather than reusing full-column assumptions.

## Tip Policy

`new_tip` is a contamination decision.

| Policy | Typical use | Primary risk |
| --- | --- | --- |
| `"always"` | Independent samples, controls, or source-destination pairs | Higher tip consumption |
| `"once"` | Reagent distribution within one contamination domain | Returning a contaminated tip to a shared source |
| `"never"` | Explicit surrounding `pick_up_tip()` and `drop_tip()` | Hidden or invalid tip state |

For a shared reagent:

- Aspirating repeatedly from the same source with one tip may be acceptable only
  if the tip never contacts incompatible destination liquid.
- A submerged dispense can wet the exterior or interior of the tip.
- Touch tip, mix, or bottom-contact dispense increases contamination risk.
- Controls and samples generally require separate tips.

Calculate tips for every conditional path. Multi-channel operations consume
sets, not individual command calls.

## Flow Rate, Position, and Delays

### Relative and absolute rates

`rate=` multiplies the configured flow rate:

```python
pipette.aspirate(50, source, rate=0.5)
```

Supported modern APIs also accept absolute flow-rate arguments:

```python
pipette.aspirate(50, source, flow_rate=25)
```

Use one form per action. Absolute units are µL/s. Establish values through
liquid-specific testing rather than copying another pipette's settings.

### Positions

```python
source.bottom(z=1)
source.top(z=-2)
destination.center()
```

- Bottom aspiration reduces residual volume but increases collision and pellet
  disturbance risk.
- Top or near-top dispensing can reduce contact contamination but may splash.
- Side offsets can reduce foaming but require known well geometry.
- `touch_tip()` can be unsafe in large wells and reservoirs; API 2.28+ rejects
  certain large-space uses.

### Air gaps and push out

Air gaps can reduce dripping but occupy pipette capacity:

```python
pipette.aspirate(80, source)
pipette.air_gap(10)
pipette.dispense(90, destination)
```

The total liquid plus air must fit the pipette. Use `push_out` to move the
plunger a small extra amount after dispensing:

```python
pipette.dispense(80, destination, push_out=5)
```

Use blowout for a larger purge. Avoid blowing into liquid when aerosols,
bubbles, or cross-contamination matter.

## Mixing

Standard mixing:

```python
pipette.mix(
    repetitions=5,
    volume=40,
    location=plate["A1"].bottom(z=1),
    aspirate_flow_rate=20,
    dispense_flow_rate=30,
    final_push_out=5,
)
```

Choose a mix volume below the available liquid volume and pipette maximum.
Account for pellets, beads, cells, foaming, and plate seals.

API 2.27 adds dynamic mixing:

```python
well = plate["A1"]
pipette.dynamic_mix(
    aspirate_start_location=well.bottom(z=1),
    aspirate_end_location=well.bottom(z=4),
    dispense_start_location=well.bottom(z=4),
    dispense_end_location=well.bottom(z=1),
    repetitions=3,
    volume=50,
)
```

Dynamic movement is geometry-sensitive. Simulate, inspect the path, and dry-run
with the exact labware before using it on samples.

## Dynamic Aspiration and Dispensing

API 2.27 can move between two locations during one plunger action:

```python
pipette.aspirate(
    volume=100,
    location=well.bottom(z=1),
    end_location=well.bottom(z=5),
    movement_delay=1,
)
```

This can follow a changing meniscus or sweep through a liquid column. It does
not automatically prove that the declared liquid volume or geometry is
correct.

## Liquid Definitions and Meniscus

Declare setup volumes with labware-level methods:

```python
buffer = protocol.define_liquid(
    name="Buffer",
    description="Assay buffer",
    display_color="#1F77B4",
)
reservoir.load_liquid(
    wells=["A1"],
    volume=12_000,
    liquid=buffer,
)
```

API 2.23 adds `well.meniscus()`:

```python
start_surface = reservoir["A1"].meniscus(z=-1, target="start")
end_surface = reservoir["A1"].meniscus(z=-1, target="end")
```

The calculated surface depends on liquid volume and labware geometry. With
dynamic aspiration or dispensing, `target="start"` and `target="end"` can
represent the expected surface at either end of the operation.

Do not rely on meniscus targeting until declared volumes, well geometry, and
liquid-level behavior have been checked on the robot.

## Liquid Presence Detection

Flex pressure sensors support three explicit operations:

```python
present = pipette.detect_liquid_presence(reservoir["A1"])
pipette.require_liquid_presence(reservoir["A1"])
height = pipette.measure_liquid_height(reservoir["A1"])
```

Or enable a check before every aspiration:

```python
pipette = protocol.load_instrument(
    "flex_1channel_1000",
    "left",
    tip_racks=[tips],
    liquid_presence_detection=True,
)
```

Operational constraints:

- Use a fresh, dry, empty tip.
- Detection can add 5–50 seconds per check depending on well depth and volume.
- An 8-channel pipette has pressure sensors only on channels 1 and 8.
- A 96-channel pipette has pressure sensors only on channels 1 and 96.
- A wet tip can defeat absence detection.
- Detection is not a substitute for source-volume planning.

Use explicit checks at critical sources when global detection would add too
much time.

## Partial Tip Pickup

Supported layouts:

| Pipette | Layout | Minimum API |
| --- | --- | ---: |
| Flex 96-channel | column | 2.16 |
| Flex 96-channel | row, single | 2.20 |
| Flex 8-channel | single, partial column | 2.20 |
| OT-2 multi-channel | single, partial column | 2.20 |

```python
from opentrons.protocol_api import ALL, COLUMN

pipette.configure_nozzle_layout(
    style=COLUMN,
    start="A12",
    tip_racks=[partial_rack],
)

# Partial-column operations...

pipette.configure_nozzle_layout(
    style=ALL,
    tip_racks=[full_rack],
)
```

Critical rules:

- `configure_nozzle_layout()` resets `pipette.tip_racks`.
- Use separate rack variables for full and partial pickup.
- Full-rack Flex 96-channel pickup requires an adapter.
- Partial Flex 96-channel pickup must not use the adapter.
- Never pass a pickup or well location that leaves active nozzles hanging
  outside the rack or labware.
- Deck-edge reach depends on layout and starting nozzle.
- Prefer the 96-channel pipette's column-12 nozzles for column pickup when deck
  reach allows.
- Simulate and perform a tip-only dry run before first physical use.

See the official
[Partial Tip Pickup guide](https://docs.opentrons.com/python-api/pipettes/partial-tip-pickup/)
for layout-specific target-well rules.

## Serial Dilution Pattern

For a full 96-well plate and an 8-channel pipette:

1. Preload stock in column 1.
2. Add diluent to columns 2–12.
3. Transfer from column 1 to 2, mix, then 2 to 3, and so on.
4. Use a fresh tip set at each dilution step unless the validated method says
   otherwise.
5. Remove one transfer volume from column 12 if equal final volumes are needed.

Referencing A-row wells addresses full columns:

```python
pipette.transfer(
    100,
    source=plate.rows()[0][0:11],
    dest=plate.rows()[0][1:12],
    mix_after=(3, 50),
    new_tip="always",
)
```

Verify that the tip budget covers 11 serial steps plus diluent addition and
final-volume removal.

## Final Liquid-Handling Review

- Every volume is within pipette and tip range.
- Air plus liquid never exceeds capacity.
- Sources include dead volume and disposal volume.
- Destinations remain below capacity at every intermediate step.
- Mix volume is physically available.
- Positions do not contact the well bottom or pellet.
- Tip policy matches contamination boundaries.
- Multi-channel well references match the active nozzle layout.
- Liquid sensing uses fresh, dry tips.
- Simulation expansion matches the intended command order.
- Liquid-specific behavior has been checked in a dry run.

### `references/migration-api-2-19-to-2-29.md`

# Migrating API 2.19 Protocols to the Current Baseline

This guide updates protocols written around robot software 7.3.1 and Protocol
API 2.19 to the 2026-07-23 baseline:

- Flex: Protocol API 2.29.
- OT-2: Protocol API 2.28.
- Flex local simulator: `opentrons==9.1.1`.
- OT-2 local compatibility simulator: `opentrons==9.0.0`, followed by analysis
  in the current OT-2 App.

Do not mechanically change only the API string. Newer levels can change command
validation and behavior.

## 1. Identify the Target Robot

API 2.29 is not supported on OT-2 at this baseline.

```python
# Flex
requirements = {"robotType": "Flex", "apiLevel": "2.29"}

# OT-2
requirements = {"robotType": "OT-2", "apiLevel": "2.28"}
```

Use one `apiLevel` declaration. Older files often put it in both `metadata` and
`requirements`; current analysis rejects that.

Before:

```python
metadata = {"apiLevel": "2.19", "protocolName": "Example"}
requirements = {"robotType": "Flex", "apiLevel": "2.19"}
```

After:

```python
metadata = {"protocolName": "Example"}
requirements = {"robotType": "Flex", "apiLevel": "2.29"}
```

If the protocol must remain compatible with older robot software, keep 2.19 and
apply only changes available at that level.

## 2. Replace Incorrect Flex Pipette Names

Current Flex load names describe channels and range:

| Old or incorrect pattern | Current choice |
| --- | --- |
| `p50_single_flex` | `flex_1channel_50` |
| `p50_multi_flex` | `flex_8channel_50` |
| `p1000_single_flex` | `flex_1channel_1000` |
| `p1000_multi_flex` | `flex_8channel_1000` |
| `p300_single_flex` | No direct equivalent; choose `flex_1channel_50` or `flex_1channel_1000` from validated volume needs |
| `p300_multi_flex` | No direct equivalent; choose `flex_8channel_50` or `flex_8channel_1000` |

Also available:

- `flex_96channel_200` — API 2.25+.
- `flex_96channel_1000`.

Do not choose solely by the largest transfer. Check every operation against the
pipette's lower and upper range and compatible tip capacities.

OT-2 GEN2 names remain `p20_*_gen2`, `p300_*_gen2`, and
`p1000_single_gen2`.

## 3. Make Flex Trash Explicit

Flex API 2.16+ protocols should load the fixture actually installed:

```python
trash = protocol.load_trash_bin("A3")
```

Or:

```python
chute = protocol.load_waste_chute()
```

OT-2 keeps its fixed trash in slot 12 and does not call `load_trash_bin()`.

If both a trash bin and waste chute exist, set the intended pipette trash
container or pass the documented `trash_location` to complex commands.

## 4. Update Liquid Loading, API 2.22+

`Well.load_liquid()` is deprecated, and `Well.load_empty()` does not exist in
the current package.

Before:

```python
reservoir["A1"].load_liquid(liquid=buffer, volume=10_000)
plate["A1"].load_empty()
```

After:

```python
reservoir.load_liquid(
    wells=["A1"],
    volume=10_000,
    liquid=buffer,
)
plate.load_empty(wells=["A1"])
```

For varying volumes:

```python
plate.load_liquid_by_well(
    volumes={"A1": 20, "B1": 30},
    liquid=sample,
)
```

## 5. Update Adapter Loading

`ProtocolContext.load_labware_on_adapter()` is not a current method.

Load the adapter, then call the adapter's method:

```python
adapter = protocol.load_adapter(
    "opentrons_96_well_aluminum_block",
    "D1",
)
plate = adapter.load_labware(
    "opentrons_96_wellplate_200ul_pcr_full_skirt"
)
```

Some `load_labware()` calls also accept an `adapter=` load name for supported
stacks. Use the pattern shown for the exact hardware in current documentation.

## 6. Fix Flex Magnetic Workflows

The powered Magnetic Module is OT-2-only.

Old Flex pattern:

```python
magnetic_module = protocol.load_module(
    "magnetic module gen2",
    "C2",
)
magnetic_module.engage(height_from_base=6.5)
```

Current Flex pattern:

```python
magnetic_block = protocol.load_module("magneticBlockV1", "C2")
protocol.move_labware(
    labware=plate,
    new_location=magnetic_block,
    use_gripper=True,
)
protocol.delay(minutes=5)
protocol.move_labware(
    labware=plate,
    new_location="B2",
    use_gripper=True,
)
```

The Magnetic Block is passive and has no `engage()` or `disengage()` method.

## 7. Fix Absorbance Plate Reader Calls

The reader was added in API 2.21 and is Flex-only. It does not accept
`read(wavelengths=[...])`.

Incorrect:

```python
result = plate_reader.read(wavelengths=[450, 650])
```

Correct sequence:

```python
reader = protocol.load_module("absorbanceReaderV1", "D3")

reader.close_lid()
reader.initialize(mode="multi", wavelengths=[450, 650])
reader.open_lid()
protocol.move_labware(
    labware=plate,
    new_location=reader,
    use_gripper=True,
)
reader.close_lid()
result = reader.read(export_filename="absorbance")
```

The plate reader returns zeros during simulation. Avoid divide-by-zero logic in
the simulation branch.

## 8. Remove Unsupported Complex-Command Options

Do not preserve options merely because an old reference listed them.

For example, `gradient=(start, end)` is not a supported generic `transfer()`
option in the current API. Build a validated volume list explicitly:

```python
volumes = [10, 20, 30, 40]
pipette.transfer(
    volume=volumes,
    source=reservoir["A1"],
    dest=plate.wells()[:4],
    new_tip="always",
)
```

Check uncommon options against the exact current method and API level. The
supported options for standard and liquid-class commands are not identical.

## 9. Revisit Behavior Changes

### API 2.20

- Liquid presence detection.
- CSV runtime parameters.
- Expanded partial-nozzle layouts.

### API 2.21

- Absorbance Plate Reader.
- Liquid presence checks only the first aspiration of a `mix()` cycle.

### API 2.22

- Labware-level liquid loading.
- `Well.load_liquid()` deprecated.
- Low-level robot motor control.

### API 2.23

- Meniscus locations.
- Labware lids and lid moves.
- Labware offset behavior aligned with newer App checks.

### API 2.24

- Verified and custom liquid classes.
- `transfer_with_liquid_class()`, `distribute_with_liquid_class()`, and
  `consolidate_with_liquid_class()`.
- Additional flow, delay, position, and push-out options.

### API 2.25

- Flex Stacker.
- Flex 96-Channel 200 µL pipette.

### API 2.26

- Liquid-class support for the 96-channel 200 µL pipette.

### API 2.27

- Concurrent module tasks.
- Dynamic aspirate, dispense, and mix paths.
- Built-in camera capture.
- Explicit tips for liquid-class transfers.

### API 2.28

- Flex 20 µL tips.
- Improved return of partially picked-up tips.
- Absolute blowout customization.
- Thermocycler ramp-rate control.
- `set_empty()` tip-rack state.
- Errors for unsafe `touch_tip()` use in large spaces.

### API 2.29

- Step grouping in source and protocol visualization.
- Flex-only at this migration baseline.

## 10. Revisit Module and Deck Assumptions

Check for:

- Flex trash or waste chute not represented in old code.
- Staging area and column-3 conflicts.
- New Gripper or lid moves.
- Heater-Shaker latch state.
- Thermocycler generation and footprint.
- Plate-reader caddy and lid travel.
- Stacker shuttle paths.
- Tip-rack adapter requirements for full versus partial 96-channel pickup.

API analysis has improved, so a newly raised deck-conflict error may reveal an
old protocol assumption that was never physically safe.

## 11. Revalidate Tip and Volume Policies

Do not assume newer pipetting behavior produces assay-equivalent results.

- Recalculate tip count.
- Recalculate source and dead volume.
- Confirm complex-command expansion in the run log.
- Requalify flow rates, mix behavior, bottom clearances, air gaps, and blowout.
- Recheck contamination policy.
- Recheck multi-channel and partial-nozzle well targeting.

## 12. Migration Test Plan

1. Preserve the original protocol and expected run log.
2. Update declarations and load names.
3. Replace deprecated or invalid calls.
4. Simulate with the robot-specific pin: `opentrons==9.1.1` for Flex or
   `opentrons==9.0.0` for OT-2.
5. Compare command order, tip use, source/destination mapping, and module states.
6. Test every runtime parameter branch.
7. Import into the correct App and target robot.
8. Resolve every analysis warning and error.
9. Perform a nonhazardous dry run.
10. Requalify assay performance before production use.

Do not claim a migration is equivalent solely from a successful simulation.

### `references/modules_and_deck.md`

# Modules and Deck Guide

Module compatibility is both an API question and a physical hardware question.
Confirm the robot model, module generation, caddy or adapter, firmware, deck
location, and labware before authoring commands.

## Robot Compatibility

| Hardware | Flex | OT-2 | Protocol API load name |
| --- | --- | --- | --- |
| Absorbance Plate Reader | Yes | No | `absorbanceReaderV1` |
| Flex Stacker | Yes | No | `flexStackerModuleV1` |
| Heater-Shaker GEN1 | Yes | Yes | `heaterShakerModuleV1` |
| Magnetic Block GEN1 | Yes | No | `magneticBlockV1` |
| Magnetic Module GEN1/GEN2 | No | Yes | `magnetic module` / `magnetic module gen2` |
| Temperature Module GEN2 | Yes | Yes | `temperature module gen2` |
| Thermocycler GEN2 | Yes | Yes | `thermocyclerModuleV2` |

Notes:

- Flex uses the passive Magnetic Block. The powered OT-2 Magnetic Module is not
  supported on Flex.
- Flex requires Thermocycler GEN2 for gripper-compatible operation.
- Older module generations may be supported only on OT-2. Match the load name
  to the exact hardware label.
- The HEPA/UV accessory is part of Flex operations but is not loaded and
  controlled as a Protocol API module.

See the current
[Flex module list](https://docs.opentrons.com/flex/modules/) and
[OT-2 module list](https://docs.opentrons.com/ot-2/modules/) before relying on
this snapshot.

## Deck Models

### Flex

- Working deck: A1–D3.
- Staging area: A4–D4; pipettes cannot reach it, but the Gripper can.
- Trash bins are loaded explicitly in supported column-1 or column-3 slots.
- The waste chute is loaded with `protocol.load_waste_chute()` and occupies D3.
- Powered module caddies and staging slots can conflict in the same row.
- Column-4 hardware can reserve or move through the corresponding column-3
  position.

```python
trash = protocol.load_trash_bin("A3")
chute = protocol.load_waste_chute()  # D3 only; do not load both into D3
```

Load only the fixtures physically installed for the run.

### OT-2

- User deck slots: 1–11.
- Fixed trash: slot 12.
- Do not call `load_trash_bin()` for the fixed trash.
- No Gripper or staging area.
- Labware moves are manual operator actions.

## Module Loading

```python
heater_shaker = protocol.load_module(
    module_name="heaterShakerModuleV1",
    location="D1",
)
```

Loading a powered module makes it a run requirement. The App will prevent the
run from starting unless the expected connected module is available.

Load labware through the module:

```python
plate = heater_shaker.load_labware(
    "corning_96_wellplate_360ul_flat",
    label="Mixing Plate",
)
```

For a separate adapter:

```python
temperature_module = protocol.load_module(
    "temperature module gen2",
    "D3",
)
adapter = temperature_module.load_adapter(
    "opentrons_96_well_aluminum_block"
)
plate = adapter.load_labware(
    "opentrons_96_wellplate_200ul_pcr_full_skirt"
)
```

The API generally cannot prove that every unusual module, adapter, and labware
combination is physically valid. Check the official compatibility list.

## Temperature Module

```python
temperature_module.set_temperature(celsius=4)
# Pipetting or incubation commands...
temperature_module.deactivate()
```

`set_temperature()` blocks until the target is reached. In API 2.27+,
`start_set_temperature()` can run concurrently and returns a task. Wait for the
task before relying on the target temperature.

Operational checks:

- Use the correct aluminum block or adapter.
- Include condensation and cold-surface effects in the wet-lab method.
- Deactivate when the method no longer requires control.
- Do not assume the liquid itself instantly reaches the module temperature.

## Heater-Shaker

Typical sequence:

```python
heater_shaker.close_labware_latch()
heater_shaker.set_and_wait_for_temperature(37)
heater_shaker.set_and_wait_for_shake_speed(1000)
protocol.delay(minutes=5)
heater_shaker.deactivate_shaker()
heater_shaker.deactivate_heater()
```

The exact temperature method name depends on API behavior. Current context
methods include `set_target_temperature()`,
`set_and_wait_for_temperature()`, `wait_for_temperature()`,
`set_and_wait_for_shake_speed()`, `deactivate_shaker()`, and
`deactivate_heater()`.

Always:

- Close the latch before shaking.
- Stop shaking before opening the latch or moving labware.
- Check maximum speed for the exact labware and fill volume.
- Account for clearance restrictions in neighboring slots.

API 2.27+ provides nonblocking shake and temperature operations for concurrent
work. Keep task handles and wait before a dependent step.

## Thermocycler

```python
thermocycler = protocol.load_module("thermocyclerModuleV2")
plate = thermocycler.load_labware(
    "opentrons_96_wellplate_200ul_pcr_full_skirt"
)

thermocycler.open_lid()
# Pipette into plate.
thermocycler.close_lid()
thermocycler.set_lid_temperature(temperature=105)
thermocycler.set_block_temperature(
    temperature=95,
    hold_time_seconds=180,
    block_max_volume=25,
)
thermocycler.execute_profile(
    steps=[
        {"temperature": 95, "hold_time_seconds": 15},
        {"temperature": 60, "hold_time_seconds": 30},
        {"temperature": 72, "hold_time_seconds": 30},
    ],
    repetitions=35,
    block_max_volume=25,
)
thermocycler.set_block_temperature(
    temperature=4,
    block_max_volume=25,
)
thermocycler.deactivate_lid()
```

API 2.28 adds an optional `ramp_rate` to block-temperature commands.

Checks:

- Correct plate and seal for the thermocycler.
- Lid closed before heating and cycling.
- `block_max_volume` matches the actual per-well reaction volume.
- Final hold behavior is intentional.
- Lid and block are deactivated or left active according to the method.
- No deck item conflicts with the thermocycler footprint.

## Magnetic Block, Flex

The Magnetic Block is passive. It has no engage or disengage methods.
Separation happens by moving compatible labware onto and off the block:

```python
magnetic_block = protocol.load_module("magneticBlockV1", "D1")

protocol.move_labware(
    labware=plate,
    new_location=magnetic_block,
    use_gripper=True,
)
protocol.delay(minutes=5)
protocol.move_labware(
    labware=plate,
    new_location="C1",
    use_gripper=True,
)
```

Confirm gripper compatibility and plate orientation. Avoid aspirating beads by
validating settle time, aspiration side, bottom clearance, and flow rate.

## Magnetic Module, OT-2

The powered Magnetic Module is OT-2-only:

```python
magnetic_module = protocol.load_module(
    "magnetic module gen2",
    "1",
)
plate = magnetic_module.load_labware(
    "nest_96_wellplate_2ml_deep"
)

magnetic_module.engage(height_from_base=6.5)
protocol.delay(minutes=5)
magnetic_module.disengage()
```

Engage height is labware- and assay-specific. Do not copy an arbitrary height
from another plate. The Magnetic Module is discontinued but remains supported
for existing OT-2 hardware.

## Absorbance Plate Reader, Flex API 2.21+

The reader is Flex-only and loads in A3–D3. Its caddy also uses the
corresponding column-4 location for lid travel.

Required workflow:

1. Load the module.
2. Close the lid with no plate inside.
3. Initialize the reader.
4. Open the lid.
5. Move a compatible plate onto the module with the Gripper.
6. Close the lid.
7. Read.

```python
reader = protocol.load_module(
    module_name="absorbanceReaderV1",
    location="D3",
)
plate = protocol.load_labware(
    "corning_96_wellplate_360ul_flat",
    "C2",
)

reader.close_lid()
reader.initialize(
    mode="multi",
    wavelengths=[450, 562, 600],
)
reader.open_lid()
protocol.move_labware(
    labware=plate,
    new_location=reader,
    use_gripper=True,
)
reader.close_lid()
data = reader.read(export_filename="plate_data")
```

Default hardware wavelengths are 450, 562, 600, and 650 nm.

`read()` returns:

```python
dict[int, dict[str, float]]
```

The first key is wavelength; the second is well name. In simulation every
measurement is zero, and no output file is written. Guard calculations that
would divide by a reading:

```python
if not protocol.is_simulating():
    normalized = data[450]["A1"] / data[450]["H12"]
```

Do not move the plate-reader lid manually.

## Flex Stacker, API 2.25+

Up to four Stackers attach to the right side of Flex. Each shuttle is addressed
as a column-4 location:

```python
stacker = protocol.load_module(
    module_name="flexStackerModuleV1",
    location="A4",
)
```

Configure one labware type per Stacker:

```python
stacker.set_stored_labware(
    load_name="opentrons_flex_96_tiprack_200ul",
    count=5,
    lid="opentrons_flex_tiprack_lid",
)
```

Retrieve and move:

```python
tip_rack = stacker.retrieve()
protocol.move_labware(
    labware=tip_rack,
    new_location="B2",
    use_gripper=True,
)
```

Store:

```python
protocol.move_labware(
    labware=plate,
    new_location=stacker,
    use_gripper=True,
)
stacker.store()
```

`fill()` and `empty()` pause for manual loading or unloading.

Constraints:

- Configure stored labware before `retrieve()` or `store()`.
- Only one labware type per Stacker at a time.
- Flex tip racks need compatible lids to stack.
- The Stacker does not identify what an operator physically loaded.
- Reserve the corresponding row's shuttle path and check column-3 conflicts.
- Use capacity helper methods for the exact labware height.

## Moving Labware and Lids

Flex automated move:

```python
protocol.move_labware(
    labware=plate,
    new_location="C2",
    use_gripper=True,
)
```

Manual move:

```python
protocol.move_labware(
    labware=plate,
    new_location="C2",
    use_gripper=False,
)
```

A manual move pauses for the operator. Make sure the message and run setup make
the source and destination unambiguous.

API 2.23+ supports lid stacks and `move_lid()`. Confirm lid and labware
compatibility, orientation, stack quantity, and disposal location.

## Concurrent Module Actions, API 2.27+

Concurrent methods can overlap long module actions with independent pipetting:

- Temperature: `start_set_temperature()`.
- Heater-Shaker: nonblocking temperature or shake-speed methods.
- Thermocycler: `start_set_block_temperature()`,
  `start_set_lid_temperature()`, and `start_execute_profile()`.

Pattern:

1. Start the operation and keep the returned task.
2. Perform only physically independent commands.
3. Wait for the task before any step that assumes completion.

Do not create concurrency merely to shorten runtime. Check deck access,
vibration, thermal dependencies, and collision risk.

## Module State Checklist

- Correct robot and module generation.
- Correct load name and API level.
- Valid deck slot and no footprint conflict.
- Correct caddy, adapter, and labware.
- Latch or lid state is safe before motion.
- Temperature, speed, and timing are validated for the method.
- Every started concurrent task is awaited.
- Gripper moves use compatible labware and clear paths.
- Modules are deactivated or intentionally held at protocol end.
- App analysis and a physical dry run cover the exact configuration.

### `references/protocol_authoring.md`

# Protocol Authoring Guide

Use this guide to turn a wet-lab method into a reviewable Opentrons Python
protocol. It targets Protocol API v2 and assumes the protocol will be imported
into the Opentrons App.

## 1. Convert the Method into Explicit Inputs

Create a protocol specification before writing code.

### Hardware

- Robot model and installed software.
- Pipette load name, mount, channels, and calibrated volume range.
- Required modules and generations.
- Flex Gripper, Stacker, waste chute, staging slot, and trash-bin requirements.
- Whether any operator action requires opening the door or moving labware.

### Labware and consumables

- Exact API load name, namespace, and definition version.
- Adapter or module beneath each item.
- Tip capacity, filter status, and number of racks.
- Lids, seals, caps, and manual removal steps.
- Custom labware JSON and how its dimensions were verified.

### Liquids and assay constraints

- Initial source volume and dead volume.
- Per-transfer volume, number of destinations, and destination capacity.
- Viscosity, volatility, foaming risk, cells or beads that settle, and
  temperature sensitivity.
- Required pre-wet, mix, air-gap, delay, touch-tip, blowout, or push-out
  behavior.
- Contamination boundaries and whether tip reuse is permitted.

### Operations

- Runtime-configurable values and safe defaults.
- Required user pauses and setup messages.
- Module temperatures, speeds, cycle profiles, and hold behavior.
- Data input and output files.
- Dry-run and acceptance criteria.

Record every assumption that has not been confirmed by the operator.

## 2. Choose the API Level Deliberately

The API level controls both available methods and behavior. It is not merely a
documentation label.

1. Check the robot's maximum supported level in the App.
2. Identify the minimum level for each required feature.
3. Use the highest of those minimums.
4. Raise the level further only for a specific fix or behavior that the method
   needs.

At the 2026-07-23 baseline:

- Flex maximum: 2.29.
- OT-2 maximum: 2.28.
- A shared Flex/OT-2 code generator must not assume API 2.29.

Do not declare an unsupported API level just because a newer local Python
package can simulate it.

## 3. Keep Top-Level Code Declarative

A protocol file normally contains imports, `metadata`, `requirements`, optional
parameter definitions, helper functions, and `run()`.

```python
from opentrons import protocol_api

metadata = {
    "protocolName": "Assay setup",
    "author": "Automation Team",
    "description": "Prepare an eight-sample assay plate.",
}
requirements = {"robotType": "Flex", "apiLevel": "2.29"}


def add_parameters(parameters: protocol_api.ParameterContext) -> None:
    parameters.add_int(
        variable_name="sample_count",
        display_name="Sample count",
        default=8,
        minimum=1,
        maximum=24,
    )


def run(protocol: protocol_api.ProtocolContext) -> None:
    sample_count = protocol.params.sample_count
    protocol.comment(f"Preparing {sample_count} samples")
```

Avoid top-level network calls, package installation, local machine paths, or
other side effects. Protocol analysis evaluates the protocol in a controlled
environment, and the robot may not have workstation packages or network
access.

Do not use `apiLevel` in both `metadata` and `requirements`.

## 4. Build a Deck Manifest

Create a simple manifest before calling load methods:

| Slot | Item | Adapter/module | Notes |
| --- | --- | --- | --- |
| A3 | Flex trash bin | — | Required for dropped tips |
| C1 | 50 µL tip rack | Flex tip-rack adapter if required | Left pipette |
| C2 | Sample rack | — | Tubes 1–8 |
| D1 | Temperature Module GEN2 | Aluminum block | Master mix |
| Thermocycler | PCR plate | Thermocycler Module GEN2 | Destination |

Then check:

- Module and adapter footprints.
- Flex column-4 staging slots and column-3 conflicts.
- Thermocycler occupied slots.
- Heater-Shaker clearance and latch state.
- Gripper approach paths and labware compatibility.
- Tall labware adjacent to partial-nozzle pickup.
- Sufficient room for lids and plate-reader lid travel.

Use named variables and labels:

```python
sample_rack = protocol.load_labware(
    "opentrons_24_tuberack_nest_1.5ml_snapcap",
    "C2",
    label="Samples 1-8",
)
```

Labels appear in setup and run views and are more useful than generic names
such as `plate1`.

## 5. Use Exact Labware Definitions

The API load name identifies geometry, not merely a product category.

- Copy load names from the
  [Labware Library](https://labware.opentrons.com/).
- Check definition version when a labware has multiple revisions.
- Do not replace a missing definition with a "close enough" plate or rack.
- Bundle the exact custom labware JSON with the protocol when needed.
- Verify custom labware dimensions, well coordinates, and stacking offsets.
- Run Labware Position Check or the current App equivalent before first use.

Loading on an adapter should reflect the physical stack:

```python
adapter = protocol.load_adapter(
    "opentrons_96_well_aluminum_block",
    "D1",
)
plate = adapter.load_labware(
    "opentrons_96_wellplate_200ul_pcr_full_skirt"
)
```

For modules, call the module or module adapter's `load_labware()` method. Do not
repeat a deck slot already supplied to `load_module()`.

## 6. Represent Initial Liquids

Liquid definitions improve setup visualization but do not move or measure
liquid.

```python
master_mix = protocol.define_liquid(
    name="Master mix",
    description="2x PCR master mix",
    display_color="#E377C2",
)

reagent_rack.load_liquid(
    wells=["A1"],
    volume=500,
    liquid=master_mix,
)
```

For varying volumes:

```python
sample_rack.load_liquid_by_well(
    volumes={"A1": 30, "A2": 40, "A3": 50},
    liquid=sample,
)
```

In API 2.22+ protocols, prefer labware-level methods over deprecated
`Well.load_liquid()`.

Declared volumes support visualization and meniscus calculations. They do not
replace physical setup checks or a source-volume budget.

## 7. Define Runtime Parameters

Use runtime parameters for values an operator should set without editing code:

- Sample count.
- Transfer volume within a validated range.
- Number of cycles.
- Incubation time.
- Dry-run mode.
- A fixed choice of pipette or workflow branch.
- A CSV plate map.

Keep hardware geometry and safety-critical invariants in code unless every
allowed choice is separately validated.

```python
def add_parameters(parameters: protocol_api.ParameterContext) -> None:
    parameters.add_float(
        variable_name="transfer_volume",
        display_name="Transfer volume",
        description="Volume delivered to each destination.",
        default=25.0,
        minimum=10.0,
        maximum=40.0,
        unit="µL",
    )
    parameters.add_bool(
        variable_name="dry_run",
        display_name="Dry run",
        description="Shorten delays and use test-safe behavior.",
        default=False,
    )
```

Constraints:

- Display name: at most 30 characters.
- Description: at most 100 characters.
- Numeric parameters need a min/max range or enumerated choices.
- A CSV parameter has no default.
- The App and touchscreen currently support one CSV parameter per run.
- CSV cells are initially strings; parse and validate every row, column, well
  name, and numeric value before issuing commands.

Use defaults that simulate successfully. Do not make a hazardous setting the
default.

## 8. Structure the Protocol

Separate configuration from repetitive actions:

```python
def transfer_samples(
    pipette: protocol_api.InstrumentContext,
    sources: list[protocol_api.Well],
    destinations: list[protocol_api.Well],
    volume: float,
) -> None:
    for source, destination in zip(sources, destinations, strict=True):
        pipette.transfer(
            volume,
            source,
            destination,
            new_tip="always",
            mix_after=(3, min(volume, 20)),
        )
```

Guidelines:

- Use explicit lists for safety-critical well order.
- Use `zip(..., strict=True)` only if the robot's Python version supports it;
  the current baseline uses Python 3.10 and does.
- Validate list lengths before command generation.
- Name physical quantities with units, for example `volume_ul` and
  `temperature_c`.
- Put all robot commands under `run()` or helpers called from `run()`.
- Let Protocol API errors stop analysis or execution. Do not broadly catch
  exceptions and continue physical motion.
- Use `protocol.pause()` for required operator intervention.

`protocol.comment()` text is computed during analysis. Do not rely on it to
report a live sensor value that only exists during physical execution.

## 9. Plan Tips and Contamination

Define a policy before choosing `new_tip`:

- `"always"`: isolate samples or source-destination pairs.
- `"once"`: one tip for an entire complex command; safe only when all contacts
  share a contamination domain.
- `"never"`: caller must already hold a tip and must handle disposal.

Examples of unsafe optimization:

- Dispensing into samples and returning to a shared reagent with the same tip.
- Reusing a tip across positive and negative controls.
- Returning a wet tip to a rack for later unrelated use.
- Reusing tips after liquid presence detection when the next detection expects
  a fresh, dry tip.

Count multi-channel tips as tip sets. A full 8-channel pickup consumes eight
tips, and a full 96-channel pickup consumes an entire rack.

## 10. Budget Volumes

For each source:

```text
required source volume =
    delivered volume
  + disposal volume
  + mixing and pre-wet loss
  + geometry-dependent dead volume
  + validated reserve
```

For each destination, calculate the maximum intermediate volume, not just the
final expected volume. Include mix strokes, carryover splits, and any material
left before a subsequent transfer.

Do not use a pipette below its supported range. For example, 100 nL is below
the range of every current Opentrons pipette and requires a different
dispensing technology or a redesigned dilution scheme.

## 11. Data and Dependencies

- Prefer runtime CSV parameters for operator-supplied tabular data.
- Bundle static data when the workflow requires a fixed resource.
- Validate file schema, required columns, allowed well names, volume ranges,
  duplicates, and total volume before generating robot commands.
- Do not download data or packages during a run.
- Do not embed credentials or make a protocol depend on broad environment
  variable access.
- Pin the local `opentrons` package used for simulation, but remember that the
  robot executes its installed software stack.

## 12. Review Checklist

- Correct robot and API level.
- Current pipette load names and compatible tips.
- Exact labware definitions and adapters.
- Explicit Flex trash or waste chute.
- No deck conflicts or unreachable partial-nozzle targets.
- Source and destination volume budgets pass.
- Tip count covers every branch and retry policy.
- Contamination policy is documented.
- Runtime parameter defaults are safe and simulation-ready.
- Module state transitions are complete.
- Every operator pause has an actionable message.
- Local simulation and App analysis both succeed.
- New geometry is covered by a nonhazardous dry run.

### `references/sources.md`

# Upstream Sources

This skill snapshot was verified on **2026-07-23**. Opentrons publishes robot
software, the desktop/touchscreen Apps, the Python package, and Protocol API
levels on related but distinct release cycles. Recheck time-sensitive facts
before generating a production protocol.

## Verified Baseline

- Stable PyPI package:
  [`opentrons==9.1.1`](https://pypi.org/project/opentrons/), released
  2026-07-13, requiring Python 3.10 or newer. This package targets the current
  Flex release line and implements Protocol API 2.29.
- Local OT-2 API 2.28 compatibility simulation uses `opentrons==9.0.0`, the
  last shared PyPI release that accepts OT-2 protocols at that API level.
- Current robot-software support documented by Opentrons:
  - Flex: API 2.15–2.29.
  - OT-2: API 2.0–2.28.
- API 2.29 and newer use separate Flex and OT-2 software/App release lines.

`opentrons==9.1.1` rejects OT-2 simulation and directs users to the separate
OT-2 App. The target robot's maximum API value and analysis result in the
appropriate App are authoritative for whether a specific protocol can run.

## Core Protocol API Documentation

- [Python Protocol API home](https://docs.opentrons.com/python-api/)
  — current Flex and OT-2 protocol overview and minimal examples.
- [Tutorial](https://docs.opentrons.com/python-api/tutorial/)
  — protocol structure, requirements, labware, trash, pipettes, simulation, and
  App import.
- [Versioning](https://docs.opentrons.com/python-api/versioning/)
  — supported API ranges, robot-software mapping, and changes by API level.
- [ProtocolContext API reference](https://docs.opentrons.com/python-api/reference/protocols/)
  and [InstrumentContext API reference](https://docs.opentrons.com/python-api/reference/instruments/)
  — exact current class and method signatures and navigation to other classes.
- [Protocol examples](https://docs.opentrons.com/python-api/examples/)
  — official ready-made Flex and OT-2 examples.
- [Adapting from OT-2 to Flex](https://docs.opentrons.com/python-api/adapting-ot2-flex/)
  — robot declaration, deck, trash, pipettes, and module migration.

## Pipettes and Liquid Handling

- [Loading Pipettes](https://docs.opentrons.com/python-api/pipettes/loading/)
  — current load names, tip compatibility, trash containers, and liquid
  presence detection.
- [Pipette Characteristics](https://docs.opentrons.com/python-api/pipettes/characteristics/)
  — channels, movement, and flow behavior.
- [Partial Tip Pickup](https://docs.opentrons.com/python-api/pipettes/partial-tip-pickup/)
  — nozzle layouts, target-well rules, adapters, deck reach, and collision
  warnings.
- [Liquid Control](https://docs.opentrons.com/python-api/building-block-commands/liquids/)
  — aspirate, dispense, push out, blowout, touch tip, mix, dynamic mix, and air
  gaps.
- [Complex Commands](https://docs.opentrons.com/python-api/complex-commands/)
  — transfer, distribute, consolidate, order, and parameters.
- [Using Liquid Classes](https://docs.opentrons.com/python-api/liquid-classes/using/)
  — verified class selection and liquid-class transfer methods.
- [Liquid Class Definitions](https://docs.opentrons.com/python-api/liquid-class-definitions/)
  — verified behavior definitions.

## Parameters, Labware, and Deck

- [Runtime Parameters](https://docs.opentrons.com/python-api/runtime-parameters/)
  — overview and use cases.
- [Defining Runtime Parameters](https://docs.opentrons.com/python-api/runtime-parameters/defining/)
  — exact Boolean, numeric, string, and CSV definitions.
- [Labware](https://docs.opentrons.com/python-api/labware/)
  — loading, well access, adapters, liquids, and lids.
- [Moving Labware](https://docs.opentrons.com/python-api/moving-labware/)
  — manual and Gripper moves.
- [Deck Slots](https://docs.opentrons.com/python-api/deck-slots/)
  — Flex and OT-2 labels, staging area, trash, waste chute, and conflicts.
- [Step Grouping](https://docs.opentrons.com/python-api/groups/)
  — API 2.29 grouping methods and protocol visualization.
- [Opentrons Labware Library](https://labware.opentrons.com/)
  — authoritative standard labware load names and definitions.

## Hardware Modules

- [Module Setup](https://docs.opentrons.com/python-api/modules/setup/)
  — load names, API introduction levels, adapters, and labware.
- [Absorbance Plate Reader API](https://docs.opentrons.com/python-api/modules/absorbance-plate-reader/)
  — initialization, lid operations, reading, and output data.
- [Flex Stacker API](https://docs.opentrons.com/python-api/modules/flex-stacker/)
  — storage configuration, retrieve/store, capacity, fill, and empty.
- [Heater-Shaker API](https://docs.opentrons.com/python-api/modules/heater-shaker/)
  — latch, temperature, and shake control.
- [Magnetic Block API](https://docs.opentrons.com/python-api/modules/magnetic-block/)
  — passive Flex separation workflow.
- [Magnetic Module API](https://docs.opentrons.com/python-api/modules/magnetic-module/)
  — powered OT-2 module control.
- [Temperature Module API](https://docs.opentrons.com/python-api/modules/temperature-module/)
  — blocking and concurrent temperature control.
- [Thermocycler API](https://docs.opentrons.com/python-api/modules/thermocycler/)
  — lid, block, profiles, ramp rate, and concurrent operations.
- [Concurrent Module Actions](https://docs.opentrons.com/python-api/modules/concurrent/)
  — API 2.27+ background tasks and waiting.

## Robot and App User Guides

- [Flex Instruction Manual](https://docs.opentrons.com/flex/)
  — installation, hardware, touchscreen, App, modules, calibration, and
  operations.
- [Flex Python API overview](https://docs.opentrons.com/flex/protocols/python-api/)
  — capabilities available to Flex protocol authors.
- [Flex supported modules](https://docs.opentrons.com/flex/modules/)
  — current physical module compatibility.
- [OT-2 Instruction Manual](https://docs.opentrons.com/ot-2/)
  — installation, hardware, App, calibration, and operations.
- [OT-2 supported modules](https://docs.opentrons.com/ot-2/modules/)
  — current physical module compatibility.
- [Opentrons App download](https://opentrons.com/app/)
  — current Flex and OT-2 App installers.

## Releases and Source

- [PyPI package](https://pypi.org/project/opentrons/)
  — stable package version, release date, Python requirement, and package
  license.
- [Robot software release notes](https://github.com/Opentrons/opentrons/blob/edge/api/release-notes.md)
  — user-facing robot software and API changes.
- [GitHub releases](https://github.com/Opentrons/opentrons/releases)
  — tagged robot software artifacts.
- [Opentrons monorepo](https://github.com/Opentrons/opentrons)
  — source for the Protocol API, robot stack, App, shared data, and docs.

## Separate HTTP API Surface

The Python Protocol API is the preferred surface for protocol files. Direct
robot-server integrations are separate:

- [HTTP API specification](https://docs.opentrons.com/http/api_reference.html)
  — published OpenAPI description.
- A target robot also serves its OpenAPI document on port 31950.

Use the specification served by the target robot when integrating directly.
Do not translate Protocol API methods into guessed HTTP endpoints.

## Source Precedence

When sources differ:

1. Target robot's maximum API and analysis result in the appropriate App.
2. Current official versioning and API reference.
3. Current robot/module instruction manual.
4. Stable PyPI metadata and tagged GitHub release.
5. Example protocols.

Examples can lag the versioning page or show a higher generic API level than a
particular robot currently supports. Apply the target robot's maximum.

### `references/validation_and_operations.md`

# Validation and Operations

Use layered validation. A protocol is not ready for live samples merely because
it compiles or simulates.

## Reproducible Local Environment

The skill pins separate compatibility environments:

- `requirements-flex.txt`: `opentrons==9.1.1`, Flex API 2.29.
- `requirements-ot2.txt`: `opentrons==9.0.0`, OT-2 API 2.28.

One-shot simulation:

```bash
# Flex
uv run --with "opentrons==9.1.1" opentrons_simulate protocol.py

# OT-2
uv run --with "opentrons==9.0.0" opentrons_simulate protocol.py
```

Dedicated Flex environment:

```bash
uv venv --python 3.10
uv pip install --python .venv/bin/python -r skills/opentrons-integration/requirements-flex.txt
.venv/bin/opentrons_simulate protocol.py
```

Use `requirements-ot2.txt` instead for the OT-2 compatibility environment.
`opentrons==9.1.1` intentionally rejects OT-2 protocols after the release-line
split; the current OT-2 App remains the authoritative OT-2 analyzer.

Check the package and maximum API implemented by the local library:

```bash
uv run --with "opentrons==9.1.1" python -c \
  "import opentrons; from opentrons import protocol_api; print(opentrons.__version__, protocol_api.MAX_SUPPORTED_VERSION)"
```

The local package does not update robot software. A protocol can simulate
locally and still request an API level unavailable on the target robot.

## Validation Ladder

### 1. Syntax and import

```bash
python -m py_compile protocol.py
```

This catches Python syntax errors only. It does not instantiate Protocol API
objects or validate deck geometry.

### 2. Local simulation

```bash
# Flex
uv run --with "opentrons==9.1.1" opentrons_simulate protocol.py

# OT-2
uv run --with "opentrons==9.0.0" opentrons_simulate protocol.py
```

Review:

- Robot type and API level.
- Every loaded labware, adapter, fixture, pipette, and module.
- Expanded command order.
- Tip pickup and disposal.
- Source and destination wells.
- Mix, air-gap, blowout, delay, and pause placement.
- Module state transitions.
- Gripper and labware moves.
- Unexpected warnings.

Useful simulator options:

```bash
# More diagnostic logs
opentrons_simulate -l info protocol.py

# Custom labware directory; repeat -L as needed
opentrons_simulate -L custom_labware protocol.py

# Add only named data files; repeat -d as needed
opentrons_simulate -d plate_map.csv protocol.py

# Experimental estimate
opentrons_simulate -e protocol.py
```

Prefer `-d` over `-D` for data because `-D` loads every file in a directory
into memory. Never point `-D` at a directory containing credentials, unrelated
data, or large files.

The current directory is searched for custom labware implicitly, but explicit
`-L` paths make validation more reproducible.

### 3. Resource audit

Independently calculate:

- Individual tips or multi-channel tip sets.
- Source volume, disposal volume, dead volume, mixing loss, and reserve.
- Maximum intermediate volume of every destination.
- Pipette capacity including air gaps.
- Module, adapter, staging, trash, and waste positions.
- Lids and Gripper paths.
- Runtime under worst-case parameters.

Simulation does not prove that the liquid budget is sufficient.

### 4. Opentrons App analysis

Use the App appropriate for the target robot. At API 2.29 and newer, Flex and
OT-2 use separate software and App release lines.

1. Connect to the intended robot.
2. Import the Python protocol and required custom labware or data.
3. Require successful protocol analysis.
4. Review analysis warnings and errors; do not bypass them.
5. Check the starting deck and module setup.
6. Set runtime parameters and inspect the resulting protocol.
7. Review protocol visualization and run preview.
8. Verify labware offsets or Labware Position Check results.
9. Confirm installed pipettes, mounts, modules, and firmware.

App analysis is closer to the target robot than local simulation, but it still
does not verify actual liquids, tips, caps, seals, or calibration.

### 5. Operator review

Use a second-person check for:

- Correct protocol revision.
- Correct robot.
- Deck map against physical deck.
- Labware identity and orientation.
- Tip type and sufficient count.
- Source identity and volume.
- Destination capacity.
- Runtime parameter values.
- Required manual steps.
- Waste capacity.
- Safety controls and emergency stop access.

### 6. Dry run

For a new or materially changed method:

- Use water or another validated nonhazardous surrogate.
- Remove valuable samples and hazardous reagents.
- Start with low-risk geometry and reduced speed where feasible.
- Check pickup, aspiration depth, dispense depth, mixing, and disposal.
- Observe every Gripper, lid, Stacker, and partial-nozzle move.
- Verify module transitions and operator prompts.
- Measure delivered volumes when accuracy matters.

A tip-only dry run is appropriate for new partial-nozzle layouts.

### 7. Controlled release

Keep:

- Protocol file hash or version.
- `opentrons` package version used in local simulation.
- Robot software and App versions.
- Custom labware definitions and versions.
- Runtime parameter record.
- Dry-run and qualification results.
- Operator and reviewer sign-off as required by the lab's quality system.

## What Simulation Does Not Validate

- Pipette calibration or mechanical wear.
- Labware manufacturing variation or placement error.
- Physical caps, seals, lids, warped plates, or obstructions.
- Actual liquid volume or identity.
- Viscosity, volatility, surface tension, foaming, or aerosols.
- Bead settling, pellet location, or cell sedimentation.
- Reliable liquid-level sensing with the chosen liquid.
- Gripper friction and every collision scenario.
- Module thermal equilibration inside the sample.
- Plate-reader optical performance; simulated readings are zeros.
- Operator compliance with a pause message.

## Runtime Parameter Testing

The default value should always produce a meaningful local simulation.

For each parameter:

- Test minimum, maximum, default, and every fixed choice.
- Test branch combinations that change tip count, deck use, timing, or modules.
- Reject invalid CSV rows before generating any commands.
- Confirm parameter labels and descriptions are understandable in the App.
- Recompute source volume and tips for the largest allowed run.

The command-line simulator primarily analyzes defaults. Use App analysis or
dedicated test variants to exercise alternate runtime values.

## Custom Labware

Before live use:

1. Validate the JSON schema with current Opentrons tooling.
2. Confirm dimensions against manufacturer drawings and physical measurement.
3. Check well depth, diameter or dimensions, and total capacity.
4. Check corner offset and well ordering.
5. Add stacking offsets for custom labware used on adapters.
6. Import the exact definition into the App.
7. Perform Labware Position Check.
8. Dry-run the highest-risk wells and edge positions.

Do not silently replace a missing custom definition with standard labware.

## Failure Triage

### Unsupported API version

Symptoms:

- Protocol imports locally but fails App analysis.
- Error states that requested API is above the robot maximum.

Actions:

1. Check the maximum in robot settings.
2. Update robot software and the appropriate App if approved.
3. Otherwise lower the API level and remove or replace unsupported features.

Do not edit the version string alone; audit every method and behavior gate.

### Invalid pipette or labware load name

Actions:

- Copy the current pipette name from the official loading guide.
- Copy labware names from the Labware Library.
- Confirm custom namespace and definition version.
- Replace obsolete Flex names such as `p300_single_flex` with current
  `flex_*` names only after matching volume and channel count.

### Deck conflict

Check:

- Thermocycler footprint.
- Module caddies.
- Heater-Shaker adjacent-slot restrictions.
- Flex staging area and corresponding column-3 slot.
- Plate-reader lid travel.
- Stacker shuttle row.
- Waste chute D3.
- Partial-nozzle reach and tall adjacent labware.

### Out of tips

Count:

- Every `new_tip="always"` pair.
- Tip sets for multi-channel pipettes.
- Branch-specific and retry operations.
- Tips used for liquid detection.
- Tips reserved for controls.

Add racks or redesign the validated tip policy. Do not reset tracking unless the
operator has physically replaced or correctly refilled racks.

### Insufficient source volume

Include distribution disposal volume, dead volume, pre-wet, mixing, carryover,
and reserve. Liquid setup visualization does not prevent a physical source from
running dry.

### Module not ready

Check:

- Correct generation and load name.
- USB connection and power.
- Module firmware.
- Lid or latch state.
- Returned concurrent task was awaited.
- Temperature or speed is physically reachable.

### Plate-reader calculation fails only in simulation

The reader returns zeros during simulation. Skip or substitute analysis-only
calculations under `protocol.is_simulating()` when a zero denominator is
possible. Keep the physical-run path unchanged.

### Physical pickup or positioning issue

Stop the run if collision or pickup failure is possible. Check calibration,
labware definition, offsets, tip compatibility, adapter use, nozzle layout, and
deck placement. Do not compensate with arbitrary offsets until the underlying
geometry is understood.

## Release Checklist

- [ ] Python compilation passes.
- [ ] Pinned local simulation passes.
- [ ] Run log reviewed.
- [ ] Resource audit completed.
- [ ] App analysis passes on the target robot.
- [ ] Deck map and parameters reviewed.
- [ ] Custom labware and offsets verified.
- [ ] Nonhazardous dry run completed for new geometry.
- [ ] Module and Gripper actions observed.
- [ ] Contamination and waste plan approved.
- [ ] Protocol revision and environment recorded.

### `scripts/absorbance_reader_template.py`

```python
"""Opentrons Flex Absorbance Plate Reader workflow template.

The module is Flex-only. Confirm plate compatibility, wavelengths, sample
volume, optical method, Gripper setup, and deck clearances. Simulated readings
are zeros and simulated runs do not write CSV output.
"""

from opentrons import protocol_api

metadata = {
    "protocolName": "Flex Absorbance Reader Template",
    "author": "Customize before use",
    "description": "Initialize the reader, move a plate, and export a read.",
}

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.29",
}


def run(protocol: protocol_api.ProtocolContext) -> None:
    """Read a compatible 96-well plate at 450 and 650 nm."""
    reader = protocol.load_module(
        module_name="absorbanceReaderV1",
        location="D3",
    )
    plate = protocol.load_labware(
        load_name="corning_96_wellplate_360ul_flat",
        location="C2",
        label="Assay Plate",
    )

    sample = protocol.define_liquid(
        name="Assay samples",
        description="Example plate-reader samples",
        display_color="#9467BD",
    )
    plate.load_liquid(
        wells=plate.wells(),
        volume=100,
        liquid=sample,
    )

    with protocol.group_steps(
        name="Initialize Reader",
        description="Close the empty reader and initialize two wavelengths.",
    ):
        # Required even if the physical lid begins in the closed position.
        reader.close_lid()
        reader.initialize(
            mode="multi",
            wavelengths=[450, 650],
        )

    with protocol.group_steps(
        name="Load and Read Plate",
        description="Move the plate onto the reader and export measurements.",
    ):
        reader.open_lid()
        protocol.move_labware(
            labware=plate,
            new_location=reader,
            use_gripper=True,
        )
        reader.close_lid()
        reader.read(export_filename="absorbance")

    with protocol.group_steps(
        name="Unload Plate",
        description="Return the assay plate to slot C2.",
    ):
        reader.open_lid()
        protocol.move_labware(
            labware=plate,
            new_location="C2",
            use_gripper=True,
        )

    protocol.comment(
        "Reader workflow complete. Retrieve CSV files from Recent Protocol Runs."
    )
```

### `scripts/basic_protocol_template.py`

```python
"""Minimal Opentrons Flex protocol template.

Simulate and analyze this protocol before any physical run. Replace the
labware, volumes, liquids, and deck layout with a validated wet-lab method.
"""

from opentrons import protocol_api

metadata = {
    "protocolName": "Flex Basic Transfer Template",
    "author": "Customize before use",
    "description": "Transfer buffer from a reservoir into one plate well.",
}

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.29",
}


def run(protocol: protocol_api.ProtocolContext) -> None:
    """Load a minimal Flex deck and perform one 100 µL transfer."""
    tips = protocol.load_labware(
        load_name="opentrons_flex_96_tiprack_200ul",
        location="D1",
        label="200 µL Tips",
    )
    reservoir = protocol.load_labware(
        load_name="nest_12_reservoir_15ml",
        location="D2",
        label="Buffer Reservoir",
    )
    destination_plate = protocol.load_labware(
        load_name="nest_96_wellplate_200ul_flat",
        location="C2",
        label="Destination Plate",
    )
    protocol.load_trash_bin(location="A3")

    pipette = protocol.load_instrument(
        instrument_name="flex_1channel_1000",
        mount="left",
        tip_racks=[tips],
    )

    buffer = protocol.define_liquid(
        name="Buffer",
        description="Nonhazardous example buffer",
        display_color="#1F77B4",
    )
    reservoir.load_liquid(
        wells=["A1"],
        volume=1_000,
        liquid=buffer,
    )

    with protocol.group_steps(
        name="Transfer Buffer",
        description="Move 100 µL from reservoir A1 to plate A1.",
    ):
        pipette.transfer(
            volume=100,
            source=reservoir["A1"],
            dest=destination_plate["A1"],
            new_tip="always",
        )

    protocol.comment("Transfer complete.")
```

### `scripts/ot2_basic_protocol_template.py`

```python
"""Minimal Opentrons OT-2 protocol template.

The OT-2 maximum at this skill's 2026-07-23 baseline is Protocol API 2.28.
Simulate and analyze this file in the OT-2 App before physical execution.
"""

from opentrons import protocol_api

metadata = {
    "protocolName": "OT-2 Basic Transfer Template",
    "author": "Customize before use",
    "description": "Transfer buffer from a reservoir into one plate well.",
}

requirements = {
    "robotType": "OT-2",
    "apiLevel": "2.28",
}


def run(protocol: protocol_api.ProtocolContext) -> None:
    """Load a minimal OT-2 deck and perform one 100 µL transfer."""
    tips = protocol.load_labware(
        load_name="opentrons_96_tiprack_300ul",
        location="1",
        label="300 µL Tips",
    )
    reservoir = protocol.load_labware(
        load_name="nest_12_reservoir_15ml",
        location="2",
        label="Buffer Reservoir",
    )
    destination_plate = protocol.load_labware(
        load_name="nest_96_wellplate_200ul_flat",
        location="3",
        label="Destination Plate",
    )

    # OT-2 has fixed trash in slot 12; do not call load_trash_bin().
    pipette = protocol.load_instrument(
        instrument_name="p300_single_gen2",
        mount="left",
        tip_racks=[tips],
    )

    buffer = protocol.define_liquid(
        name="Buffer",
        description="Nonhazardous example buffer",
        display_color="#1F77B4",
    )
    reservoir.load_liquid(
        wells=["A1"],
        volume=1_000,
        liquid=buffer,
    )

    pipette.transfer(
        volume=100,
        source=reservoir["A1"],
        dest=destination_plate["A1"],
        new_tip="always",
    )
    protocol.comment("Transfer complete.")
```

### `scripts/pcr_setup_template.py`

```python
"""Eight-reaction PCR setup and cycling template for Opentrons Flex.

This is an automation example, not a validated PCR method. Confirm reagent
volumes, dead volume, temperatures, cycle profile, plate, seal, and tip policy
for the assay. Simulate and complete a nonhazardous dry run before use.
"""

from opentrons import protocol_api

metadata = {
    "protocolName": "Flex PCR Setup and Cycling Template",
    "author": "Customize before use",
    "description": "Prepare eight 25 µL PCR reactions and run a cycle profile.",
}

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.29",
}


def run(protocol: protocol_api.ProtocolContext) -> None:
    """Prepare eight reactions and run an example PCR program."""
    thermocycler = protocol.load_module("thermocyclerModuleV2")
    pcr_plate = thermocycler.load_labware(
        "opentrons_96_wellplate_200ul_pcr_full_skirt",
        label="PCR Plate",
    )

    tips_50 = protocol.load_labware(
        "opentrons_flex_96_tiprack_50ul",
        "C1",
        label="50 µL Tips",
    )
    tips_200 = protocol.load_labware(
        "opentrons_flex_96_tiprack_200ul",
        "C2",
        label="200 µL Tips",
    )
    reagent_rack = protocol.load_labware(
        "opentrons_24_tuberack_nest_1.5ml_snapcap",
        "D1",
        label="PCR Reagents",
    )
    protocol.load_trash_bin("A3")

    small_pipette = protocol.load_instrument(
        "flex_1channel_50",
        "left",
        tip_racks=[tips_50],
    )
    large_pipette = protocol.load_instrument(
        "flex_1channel_1000",
        "right",
        tip_racks=[tips_200],
    )

    sample_count = 8
    master_mix_volume_ul = 20
    template_volume_ul = 5
    reaction_volume_ul = master_mix_volume_ul + template_volume_ul

    master_mix = protocol.define_liquid(
        name="PCR Master Mix",
        description="Assay-specific master mix",
        display_color="#E377C2",
    )
    template_dna = protocol.define_liquid(
        name="Template DNA",
        description="DNA samples 1-8",
        display_color="#2CA02C",
    )
    reagent_rack.load_liquid(
        wells=["A1"],
        volume=300,
        liquid=master_mix,
    )
    reagent_rack.load_liquid(
        wells=reagent_rack.wells()[1 : sample_count + 1],
        volume=20,
        liquid=template_dna,
    )
    pcr_plate.load_empty(wells=pcr_plate.wells()[:sample_count])

    thermocycler.open_lid()

    with protocol.group_steps(
        name="Distribute Master Mix",
        description="Add 20 µL master mix to reactions A1-H1.",
    ):
        large_pipette.distribute(
            volume=master_mix_volume_ul,
            source=reagent_rack["A1"],
            dest=pcr_plate.wells()[:sample_count],
            new_tip="once",
            disposal_volume=10,
        )

    with protocol.group_steps(
        name="Add Templates",
        description="Add one DNA template to each PCR reaction.",
    ):
        for index in range(sample_count):
            small_pipette.transfer(
                volume=template_volume_ul,
                source=reagent_rack.wells()[index + 1],
                dest=pcr_plate.wells()[index],
                mix_after=(3, 20),
                new_tip="always",
            )

    with protocol.group_steps(
        name="Run PCR",
        description="Close the lid and execute the example PCR profile.",
    ):
        thermocycler.close_lid()
        thermocycler.set_lid_temperature(temperature=105)
        thermocycler.set_block_temperature(
            temperature=95,
            hold_time_seconds=180,
            block_max_volume=reaction_volume_ul,
        )
        thermocycler.execute_profile(
            steps=[
                {"temperature": 95, "hold_time_seconds": 15},
                {"temperature": 60, "hold_time_seconds": 30},
                {"temperature": 72, "hold_time_seconds": 30},
            ],
            repetitions=35,
            block_max_volume=reaction_volume_ul,
        )
        thermocycler.set_block_temperature(
            temperature=72,
            hold_time_minutes=5,
            block_max_volume=reaction_volume_ul,
        )
        thermocycler.set_block_temperature(
            temperature=4,
            block_max_volume=reaction_volume_ul,
        )
        thermocycler.deactivate_lid()
        thermocycler.open_lid()

    protocol.comment(
        "PCR complete. The block remains at 4 °C until the run is stopped."
    )
```

### `scripts/runtime_parameters_template.py`

```python
"""Flex runtime-parameter template with simulation-safe defaults.

The operator can choose sample count, transfer volume, and dry-run mode in the
Opentrons App without editing source code. Validate the full allowed parameter
space and volume budget before adapting this template to an assay.
"""

from opentrons import protocol_api

metadata = {
    "protocolName": "Flex Runtime Parameters Template",
    "author": "Customize before use",
    "description": "Distribute buffer using operator-selected safe parameters.",
}

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.29",
}


def add_parameters(parameters: protocol_api.ParameterContext) -> None:
    """Define values that the operator may change during run setup."""
    parameters.add_int(
        variable_name="sample_count",
        display_name="Sample count",
        description="Number of destination wells to fill.",
        default=8,
        minimum=1,
        maximum=12,
    )
    parameters.add_float(
        variable_name="transfer_volume",
        display_name="Transfer volume",
        description="Buffer volume delivered to each well.",
        default=50.0,
        minimum=10.0,
        maximum=100.0,
        unit="µL",
    )
    parameters.add_bool(
        variable_name="dry_run",
        display_name="Dry run",
        description="Use a short example incubation.",
        default=True,
    )


def run(protocol: protocol_api.ProtocolContext) -> None:
    """Distribute buffer according to validated runtime values."""
    sample_count = protocol.params.sample_count
    transfer_volume_ul = protocol.params.transfer_volume
    dry_run = protocol.params.dry_run

    tips = protocol.load_labware(
        "opentrons_flex_96_tiprack_200ul",
        "D1",
        label="200 µL Tips",
    )
    reservoir = protocol.load_labware(
        "nest_12_reservoir_15ml",
        "D2",
        label="Buffer Reservoir",
    )
    plate = protocol.load_labware(
        "nest_96_wellplate_200ul_flat",
        "C2",
        label="Destination Plate",
    )
    protocol.load_trash_bin("A3")
    pipette = protocol.load_instrument(
        "flex_1channel_1000",
        "left",
        tip_racks=[tips],
    )

    buffer = protocol.define_liquid(
        name="Buffer",
        description="Example distribution buffer",
        display_color="#1F77B4",
    )
    reservoir.load_liquid(
        wells=["A1"],
        volume=2_000,
        liquid=buffer,
    )
    destinations = plate.wells()[:sample_count]
    plate.load_empty(wells=destinations)

    protocol.comment(
        f"Filling {sample_count} wells with {transfer_volume_ul:.1f} µL each."
    )

    with protocol.group_steps(
        name="Distribute Buffer",
        description="Fill the selected number of destination wells.",
    ):
        pipette.distribute(
            volume=transfer_volume_ul,
            source=reservoir["A1"],
            dest=destinations,
            new_tip="once",
            disposal_volume=20,
        )

    protocol.delay(
        seconds=1 if dry_run else 60,
        msg="Example incubation; replace with an assay-specific duration.",
    )
    protocol.comment("Parameterized distribution complete.")
```

### `scripts/serial_dilution_template.py`

```python
"""Full-plate 1:2 serial dilution on Opentrons Flex.

Physical setup:
- Put at least 12 mL diluent in reservoir A1.
- Put 200 µL stock in every well of plate column 1.
- Leave plate columns 2-12 empty.

The protocol fills columns 2-12 with 100 µL diluent, serially transfers
100 µL across the plate, and removes 100 µL from column 12 so every well
finishes at 100 µL. Simulate, dry-run, and validate the assay before use.
"""

from opentrons import protocol_api

metadata = {
    "protocolName": "Flex 8-Channel Serial Dilution Template",
    "author": "Customize before use",
    "description": "Create eleven 1:2 dilution steps across a 96-well plate.",
}

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.29",
}


def run(protocol: protocol_api.ProtocolContext) -> None:
    """Perform the same serial dilution across all eight plate rows."""
    tips_1 = protocol.load_labware(
        "opentrons_flex_96_tiprack_200ul",
        "D1",
        label="Tips 1",
    )
    tips_2 = protocol.load_labware(
        "opentrons_flex_96_tiprack_200ul",
        "C1",
        label="Tips 2",
    )
    reservoir = protocol.load_labware(
        "nest_12_reservoir_15ml",
        "D2",
        label="Diluent Reservoir",
    )
    plate = protocol.load_labware(
        "corning_96_wellplate_360ul_flat",
        "C2",
        label="Dilution Plate",
    )
    trash = protocol.load_trash_bin("A3")

    pipette = protocol.load_instrument(
        instrument_name="flex_8channel_1000",
        mount="left",
        tip_racks=[tips_1, tips_2],
    )

    diluent = protocol.define_liquid(
        name="Diluent",
        description="Buffer or media used for the dilution series",
        display_color="#9ECAE1",
    )
    stock = protocol.define_liquid(
        name="Stock",
        description="Starting material at the highest concentration",
        display_color="#DE2D26",
    )
    reservoir.load_liquid(
        wells=["A1"],
        volume=12_000,
        liquid=diluent,
    )
    plate.load_liquid(
        wells=plate.columns()[0],
        volume=200,
        liquid=stock,
    )

    # With a full 8-channel pipette, A-row wells address entire columns.
    column_anchors = plate.rows()[0]

    with protocol.group_steps(
        name="Add Diluent",
        description="Fill columns 2-12 with 100 µL diluent.",
    ):
        pipette.transfer(
            volume=100,
            source=reservoir["A1"],
            dest=column_anchors[1:],
            new_tip="once",
        )

    with protocol.group_steps(
        name="Serial Dilution",
        description="Transfer and mix through eleven 1:2 dilution steps.",
    ):
        pipette.transfer(
            volume=100,
            source=column_anchors[:11],
            dest=column_anchors[1:],
            mix_after=(3, 50),
            new_tip="always",
        )

    with protocol.group_steps(
        name="Equalize Final Volume",
        description="Remove 100 µL from every well in column 12.",
    ):
        pipette.pick_up_tip()
        pipette.aspirate(100, column_anchors[11])
        pipette.dispense(100, trash)
        pipette.drop_tip()

    protocol.comment("Serial dilution complete: columns 1-12 contain 100 µL per well.")
```

### `requirements-flex.txt`

```text
opentrons==9.1.1
```

### `requirements-ot2.txt`

```text
opentrons==9.0.0
```
