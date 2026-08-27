---
name: lab-hardware-cad
description: Design custom laboratory hardware as parametric build123d models and export fabrication-ready STEP, STL, and DXF files - microfluidic chips and molds, optomechanical mounts and breadboard adapters, cuvette and microplate holders, tube racks, animal-behavior rigs, and 3D-printed instrument fixtures. Use when a research task needs a physical part that must mate with standardized labware, an optical table, a cage system, or a printer, CNC, or laser process.
---

# Lab Hardware CAD

Design physical research hardware as **parametric Python source**, export STEP as the
authoritative artifact, and verify the result both numerically and visually before anything
is fabricated.

The hard part of lab hardware is almost never the geometry. It is that the part must mate with
equipment whose dimensions are fixed by a published standard or a vendor drawing. A holder that
is 0.5 mm too wide does not fit the plate reader; a channel with the wrong aspect ratio collapses
during bonding; a mount whose bolt pattern is 25.4 mm instead of 25.0 mm will not reach the
optical table. This skill exists to keep those numbers correct and checked.

## When to use

Use for any request to design, model, or fabricate a physical part for a lab: chip, mold, mount,
adapter, holder, rack, bracket, enclosure, jig, fixture, arena, or maze. Also use to inspect or
modify an existing STEP file.

Do **not** use for finite-element analysis, computational fluid dynamics, molecular structure,
or scientific plotting. Those are different skills.

## Setup

```bash
uv venv --python 3.12 .venv-labcad
uv pip install --python .venv-labcad/bin/python "build123d==0.11.1" "matplotlib>=3.8"
```

build123d 0.11.1 requires Python >=3.10,<3.15 and pulls in the OpenCascade kernel through
`cadquery-ocp-novtk`. The wheel is large; install once per project and reuse it.

All bundled scripts take `--help`. `check.py standards` runs without build123d installed.

**Model files are executed, not parsed.** `gen.py`, `check.py`, and `snapshot.py` import a
`*_model.py` and call its `build()`, which runs arbitrary Python in the current environment. That
is inherent to parametric CAD — the source is the design. Only run model files authored in this
session or supplied by the user from a trusted location. If a model came from the internet, a
shared drive, or an untrusted colleague, read it before running it and say that you did.

## Required workflow

Follow these steps in order. Steps 5 and 6 are not optional, and step 6 is not waived by step 5
passing.

### 1. Route to a device family

Read the request, classify it, and load **exactly one** family reference. Do not load all four —
they are long, and mixing conventions between families is a common source of error.

| If the part is | Load |
| --- | --- |
| A chip, mold, channel network, flow cell, gasket, or anything with fluid ports | `references/microfluidics.md` |
| A mount, post, breadboard adapter, cage-system part, filter or sample holder in a beam path | `references/optomechanics.md` |
| An adapter, insert, rack, or holder for plates, cuvettes, tubes, slides, or dishes | `references/labware-adapters.md` |
| An arena, maze, head-fixation part, spout, tether, or extrusion-mounted enclosure for animal work | `references/behavior-rigs.md` |

If the part genuinely spans two families — a microfluidic chip that bolts to an optical table —
load the family that owns the **critical interface**, then read only the interface section of the
second. State in your response which family you routed to.

### 2. Establish the interface dimensions before any geometry

Every part has at least one mating interface. Before writing code, write down for each interface:

- the **source** of the dimension: a published standard, a vendor drawing, or a user measurement;
- the **nominal value and tolerance**;
- the **clearance or interference** you intend, and why.

Look the number up in `assets/standards.json` or the family reference. **Never write an interface
dimension from memory.** If the number is not in the standards file or the reference, ask the user
for the vendor drawing or the measurement rather than guessing. A guessed interface dimension is
the single most expensive failure mode in this skill.

A feature that must *receive* a standardised component is sized against that component's
**maximum material condition** — nominal plus its plus-tolerance — and only then given clearance.
Sized from nominal instead, it fits only the smaller half of conforming parts.

```bash
python scripts/check.py standards --list
python scripts/check.py standards --show slas-microplate-footprint
```

The bundled standard IDs (exact strings; do not guess variants): `slas-microplate-footprint`,
`slas-microplate-height`, `slas-microplate-flange`, `slas-well-positions-96`,
`slas-well-positions-384`, `slas-well-positions-1536`, `cuvette-standard-10mm`,
`optical-breadboard-metric`, `optical-breadboard-imperial`, `cage-system-30mm`,
`sm1-lens-tube-thread`.

If the part mates with nothing in this list, that is common and fine: declare no interfaces,
and name every interface dimension with its source (user spec, vendor drawing, measurement) as
**unchecked** in the report. Never declare against an unrelated standard to fill the gap — a
fabricated declaration is worse than an honest "nobody checked this".

### 3. Choose the process before choosing the geometry

Read `references/fabrication-limits.md`. Process determines minimum wall, minimum feature,
achievable tolerance, and whether the part survives autoclaving or contact with your solvent.
FDM cannot hold ±0.05 mm; SLA resin is generally not safe for cell contact without post-cure and
testing. Record the process and material in the model docstring.

### 4. Author a parametric model

Write `<part>_model.py`. The source is the authoritative artifact — **never hand-edit an exported
STEP file**, and never regenerate from a mesh.

Requirements:

- Every dimension that a user might change is a **module-level named constant** with units in the
  name: `bore_d_mm`, `wall_t_mm`, `post_h_mm`. No bare numbers in the body except 0, 1, and 2.
- Expose `build() -> Part`. `gen.py` calls it.
- Group parameters into an `INTERFACE` block (dimensions fixed by a standard, annotated with the
  standard ID) and a `DESIGN` block (dimensions you are free to choose).
- **Derive every computed dimension inside a function**, never at module level, so `--param`
  overrides actually reach it.
- Declare an `interfaces()` function returning the dimensions the part must fit, each with its
  standard ID and intent. This is what makes the interface machine-checkable in step 5.
  `intent` is `"envelope"` when the feature must **accept** any conforming part (a pocket, bore,
  or slot — checked one-sided at maximum material condition plus your clearance) and `"match"`
  when this part must itself conform (symmetric band). `clearance` is the total intended
  clearance in mm and must be non-negative. Declare only dimensions that constrain *this part's
  mating features* — a property of the mating equipment (a table's edge border, a typical plate
  thickness) is not an interface of yours. If no bundled standard applies, return `[]`.
- Declare a `checks()` function of **go/no-go gauges measured from the built solid**: a `clear`
  region for everything that must pass through or fit in (screw shafts, beam corridors, the
  mating part at maximum material condition dropping into its pocket), a `material` region for
  everything that must remain (a ridge, a ledge, a screw seat), and a `bbox_*` bound for every
  size limit the user stated. Map **every geometric requirement in the request** to one entry;
  these catch the errors that `is_valid`, the bounding box, and declared numbers cannot see.
  `gen.py` runs them on every generation and fails the build when one fails. Schema and worked
  examples: `references/build123d-patterns.md`.
- Put the process, material, and every interface source in the module docstring.

```python
"""SLAS microplate carrier for a custom stage insert.

Process: FDM, PETG, 0.2 mm layer.  Tolerance budget +/-0.3 mm.
Interfaces:
  - Plate pocket: ANSI/SLAS 1-2004 (R2012) footprint 127.76 x 85.48 mm, +/-0.25.
  - Stage bolts: user-measured, 40.0 mm centres (drawing in docs/stage.pdf).
"""
from build123d import *

# --- INTERFACE (fixed by standard; do not tune) ---
plate_l_mm = 127.76   # ANSI/SLAS 1-2004 nominal
plate_w_mm = 85.48    # ANSI/SLAS 1-2004 nominal
plate_tol_mm = 0.25   # ANSI/SLAS 1-2004; the pocket is sized to nominal + this
# --- DESIGN (free) ---
pocket_clearance_mm = 0.40   # per-side; FDM, see fabrication-limits.md
wall_t_mm = 3.0
floor_t_mm = 2.5
body_h_mm = 12.0


def pocket_mm() -> tuple[float, float]:
    """Pocket at the plate's maximum material condition plus clearance per side.

    A pocket sized from nominal jams on roughly half of conforming plates.
    """
    growth = plate_tol_mm + 2 * pocket_clearance_mm
    return plate_l_mm + growth, plate_w_mm + growth


def interfaces() -> list[dict]:
    """What this part must fit. `check.py interfaces` verifies every entry."""
    pocket_l, pocket_w = pocket_mm()
    return [
        {"feature": "plate pocket length", "standard": "slas-microplate-footprint",
         "dimension": "footprint_length", "value": pocket_l,
         "intent": "envelope", "clearance": 2 * pocket_clearance_mm},
        {"feature": "plate pocket width", "standard": "slas-microplate-footprint",
         "dimension": "footprint_width", "value": pocket_w,
         "intent": "envelope", "clearance": 2 * pocket_clearance_mm},
    ]


def checks() -> list[dict]:
    """Gauges measured from the built solid. Sized from the REQUIREMENT's numbers
    (plate MMC, the user's height limit), not from the pocket parameters, so a
    wrong parameter cannot shrink the gauge to match the wrong geometry."""
    depth = body_h_mm - floor_t_mm
    return [
        {"feature": "plate at MMC drops into the pocket",
         "clear": {"box": (plate_l_mm + plate_tol_mm, plate_w_mm + plate_tol_mm, depth),
                   "at": [(0.0, 0.0, floor_t_mm + depth / 2)]}},
        {"feature": "under 15 mm for the stage", "bbox_z": {"max": 15.0}},
    ]


def build() -> Part:
    pocket_l, pocket_w = pocket_mm()
    with BuildPart() as carrier:
        Box(pocket_l + 2 * wall_t_mm, pocket_w + 2 * wall_t_mm, body_h_mm,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, 0, floor_t_mm)):
            Box(pocket_l, pocket_w, body_h_mm, mode=Mode.SUBTRACT,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
    return carrier.part
```

See `references/build123d-patterns.md` for the builder-vs-algebra choice, the `interfaces()`
contract, sketching, selectors, fillets, and threaded-insert bores.

### 5. Generate and run the checks

```bash
python scripts/gen.py carrier_model.py --outdir out/
python scripts/check.py facts out/carrier.step
python scripts/check.py interfaces out/carrier.manifest.json
python scripts/check.py geometry out/carrier.step --model carrier_model.py
```

`gen.py` also evaluates the model's `checks()` gauges against the solid it just built, prints
each PASS/FAIL, records them in the manifest, and exits non-zero on a failure — so a part that
violates its own declared geometry never silently becomes an artifact. `check.py geometry`
re-runs the same gauges against the exported STEP, which is the authoritative artifact.

`out/` is a scratch convention, not a requirement. When the user asked for deliverables in a
specific place, generate there (`--outdir .`) or copy the STEP, manifest, and DXF to it before
finishing — a deliverable that exists only inside `out/` has not been delivered.

`gen.py` writes `carrier.step` (authoritative), `carrier.stl` (mesh preview and printing), and
`carrier.manifest.json` recording the source hash, resolved parameters, declared interfaces,
library versions, and measured bounding box, volume, and validity. The manifest is the provenance
record — keep it with the artifact.

`check.py facts` reports `is_valid`, bounding box, volume, surface area, centre of mass, and
solid count. A part that reports `is_valid: false` is broken geometry; fix the source before going
further.

`check.py interfaces` evaluates every entry the model declared against the standards database
and exits non-zero on failure. **Be clear about what it does and does not verify:** it checks the
*declared numbers* — catching a transcribed dimension, the wrong standard, and
nominal-instead-of-MMC sizing — but it never measures the built geometry, and a value computed
from the same constants it is checked against passes with zero headroom by construction. Do not
cite it as evidence the geometry is right; `facts` and the snapshot are the geometry checks.
An empty declaration list passes: a part that mates with nothing in the bundled database has
nothing to declare, and its interface dimensions are instead named as unchecked in the report.

Use `interfaces` rather than `check.py fit` for anything internal — a pocket, bore, or slot does
not appear in the part's outer bounding box, which is what `fit` measures. Reach for `fit` only
to check one number by hand (`--value footprint_length=128.81`), or when the part's own outline
is the interface, such as a gasket cut to a plate footprint.

For assemblies, check that parts do not interfere:

```bash
python scripts/check.py clearance out/carrier.step out/lid.step --min 0.3
```

### 6. Snapshot and actually look at it

```bash
python scripts/snapshot.py out/carrier.step --out out/carrier.png
```

Then **read the PNG**. This step is mandatory after every generation and every modification.
Deterministic checks passing is not a reason to skip it: `is_valid` and a correct bounding box are
both fully consistent with a pocket cut on the wrong face, a boss placed outside the body, or a
fillet that ate a feature. Those errors are obvious in a picture and invisible in the numbers.

Know the render's limits too. A feature much smaller than the frame — a 0.3 mm mold ridge on a
40 mm part, a counterbore step on a plate — may not be decidable from the views at all. Do not
report seeing something the image cannot resolve; that is worse than not looking. For such
features the skill has instruments: `check.py bores` prints every cylindrical face (diameter,
axis, position, span, sweep) so you can reconcile the drilling against the model's intent, and
`check.py probe` answers a one-off "is this region clear / is material present here" without
editing the model. Cite the measured numbers; report from the picture only what the picture
actually shows.

The six views are true orthographic projections, and the outlines are the model's real edges drawn
**without hidden-line removal**. So a circle visible "through" material is a bore on the far side,
not a window — the part is not transparent. Read it that way rather than reporting a hole that
is not there.

State in your response what you saw in the snapshot, not merely that you generated one.

### 7. Repair through the source

If any check fails, edit the parameters or the model code, rerun `gen.py`, and rerun **both**
step 5 and step 6. Never patch the STEP.

### 8. Report before fabrication

Work through `references/validation.md` and give the user: the process and material, every
interface dimension with its source and tolerance, the clearances chosen, what the snapshot showed,
and any check that did not pass.

Flag explicitly every interface the automatic check could not cover — a vendor drawing, a user
measurement, a standard not in the bundled database. `check.py interfaces` reports only what the
model declared against a known standard, so silence there is not confirmation; a dimension nobody
could check has to be named as such.

## Units

build123d is unitless internally and everything in this skill is **millimetres and degrees**.
`export_step` is called with `Unit.MM`. Imperial hardware appears throughout optomechanics
(1/4-20 screws, 1 inch grids, SM1 threads); convert to millimetres in a single named constant at
the point of definition and never mix systems inside an expression. 1 inch is exactly 25.4 mm, and
a 25 mm metric optical grid is **not** interchangeable with a 1 inch imperial grid — the error
accumulates to 1.6 mm over four holes.

## Tolerances and fits

A nominal dimension is not a fit. Every mating dimension needs a deliberate clearance chosen from
the process tolerance in `references/fabrication-limits.md`. Common defaults, per side:

| Fit | FDM | SLA | CNC |
| --- | --- | --- | --- |
| Free-sliding (plate in a pocket) | 0.40 mm | 0.20 mm | 0.10 mm |
| Located but removable | 0.25 mm | 0.10 mm | 0.05 mm |
| Press / interference | -0.05 mm | -0.03 mm | -0.02 mm |

These are starting points for a first article, not guarantees. Say so when you report them, and
recommend printing a test coupon of the critical interface before committing to a full part.

## Scientific caveats

- **Material compatibility governs.** A geometrically perfect part in the wrong polymer fails in
  service: autoclave cycles distort PLA, many solvents craze acrylic, and uncured SLA resin is
  cytotoxic. Check `references/fabrication-limits.md` before recommending a material for anything
  contacting cells, tissue, solvents, or heat.
- **Optical parts have non-geometric requirements.** Autofluorescence, surface roughness, and
  stray-light scatter are not visible in a STEP file. Black resin is not automatically low-scatter.
- **Vendor labware varies.** The SLAS standards fix the plate footprint but not well geometry,
  skirt profile, or lid fit, and consumable tubes differ between suppliers. Design to the standard
  where one exists; otherwise require a measurement.
- **A passing bounding box is not a passing part.** `fit` checks the dimensions it is given. It
  cannot see a missing feature, and it does not replace the snapshot.

## References

| File | Contents |
| --- | --- |
| `references/microfluidics.md` | Channel cross-sections and aspect ratios, mold vs chip polarity, minimum features by process, port and tubing interfaces, bonding lands, dead volume |
| `references/optomechanics.md` | Breadboard grids and screw clearances, post and pedestal heights, 30 mm cage geometry, SM lens-tube threads, beam height |
| `references/labware-adapters.md` | ANSI/SLAS 1-4 microplate dimensions, cuvettes, tubes, slides, dishes, deck and stage constraints |
| `references/behavior-rigs.md` | Arena and maze geometry, head-fixation interfaces, spouts and ports, T-slot extrusion, cleaning and durability |
| `references/fabrication-limits.md` | Process tolerances, minimum walls and features, clearance and thread inserts, materials, autoclave and solvent and biocompatibility |
| `references/validation.md` | Pre-fabrication checklist and the failure modes each item catches |
| `references/build123d-patterns.md` | build123d 0.11.1 API cookbook: builder vs algebra, sketches, selectors, joints, exports |

## Scripts

| Command | Purpose |
| --- | --- |
| `gen.py <model.py> --outdir DIR` | Run `build()`, export STEP and STL, write the provenance manifest |
| `gen.py <model.py> --dxf [--dxf-z MM]` | Also slice a 2D DXF profile for laser cutting (default plane: mid-height) |
| `check.py facts <step>` | Validity, bounding box, volume, area, centre of mass, solid count |
| `check.py interfaces <manifest\|model.py>` | Check every declared interface number against its standard; non-zero exit on failure |
| `check.py geometry <model.py\|step --model M>` | Evaluate the model's `checks()` gauges against the built solid — measured, not declared |
| `check.py probe <step> --cyl D\|--box X,Y,Z --at ...` | One ad-hoc gauge: is this region clear of material, or filled with it |
| `check.py bores <step>` | Census of every cylindrical face: diameter, axis, position, span, sweep |
| `check.py fit --standard ID --value DIM=MM` | Check one dimension by hand, or a part whose outer envelope is the interface |
| `check.py clearance <a> <b> --min MM` | Minimum distance between two solids; detects interference |
| `check.py standards [--list\|--show ID]` | Browse the bundled standards data (standard library only) |
| `snapshot.py <step> --out PNG` | Six-view orthographic and isometric render for visual review |

All commands accept `--json` for machine-readable output and write progress to stderr.
`check.py standards`, and `check.py interfaces` on a manifest, run without build123d installed.

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/lab-hardware-cad/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/behavior-rigs.md`

# Animal-behavior rigs and enclosures

Arenas, mazes, head-fixation hardware, spouts and ports, and the extrusion frames that carry them.

## Dimensions come from the protocol, not from this file

Behavioral apparatus dimensions are **not standardised**. They are set by the published protocol
the experiment replicates, and they differ between species, strains, ages, and labs. An
elevated plus maze sized for rats is wrong for mice; an open field sized from one paper will not
reproduce another paper's results.

**Ask which protocol or paper the rig replicates, and take the dimensions from it.** If the user
does not have one, say plainly that the geometry is a design choice affecting comparability, and
get their sign-off on the numbers before modelling. Do not supply "standard" maze dimensions from
memory — there is no such standard, and a plausible-looking wrong number is worse here than an
admitted gap, because it silently breaks comparison with prior work.

What this file does cover is the engineering that is common across rigs.

## Regulatory and welfare context

Any apparatus that contacts animals falls under the institution's approved protocol. Before
fabrication:

- The design must be consistent with the **approved IACUC (or local equivalent) protocol**. A
  geometry change — a narrower arm, a different head-plate, a new restraint — may require an
  amendment. Flag this; it is not the modeller's call to make.
- **Materials must be non-toxic and non-irritant**, including after repeated cleaning.
- No **entrapment or pinch geometry**: no gaps that can catch a limb, tail, or head; no wedge-
  shaped gaps that narrow into a trap. Break sharp edges everywhere an animal can reach.
- Anything load-bearing over an animal needs a real margin, not a printed part at minimum wall.

Raise these actively rather than waiting to be asked.

## Materials and cleaning

This dominates material choice, and it eliminates most of the obvious options:

- **Cleaning agents** are the constraint. Ethanol (70%) crazes many plastics; quaternary ammonium
  and chlorine dioxide disinfectants attack others; autoclaving distorts anything with a low glass
  transition temperature. PLA in particular softens well below autoclave temperature and should be
  treated as single-use.
- **Porosity carries odour.** FDM parts are porous by construction, hold odour cues between
  animals, and cannot be reliably disinfected. Odour is a genuine confound in behavior work. Prefer
  a non-porous process, or seal the surface, or treat FDM parts as consumable and per-cohort.
- **Chew resistance.** Rodents will chew anything reachable. Printed polymer at an exposed edge
  will be destroyed and, worse, ingested. Put metal, glass, or a hard sacrificial edge wherever an
  animal can bite, and keep printed material out of reach where possible.
- **Uncured resin is cytotoxic and an irritant.** SLA parts that contact animals need full post-
  cure and thorough washing. See `references/fabrication-limits.md`.

## Video tracking and optics

Most rigs are recorded, and the geometry either helps or fights the tracking:

- **Contrast**: match the surface to the animal's coat so the tracker can segment it. Matte white
  or light grey floors for dark animals, matte dark for albino. **Matte, not gloss** — specular
  highlights are tracked as objects.
- **Avoid shadow-casting geometry** near the floor. Deep walls at low camera angles create shadow
  bands that trackers segment as the animal.
- **Infrared**: if illumination is IR, remember that many "opaque" black plastics transmit IR, and
  that IR-transparent floors change the apparent image. Verify with the actual camera, not by
  assumption.
- Leave a clear, unobstructed camera line to the whole arena, and model the camera mount as part
  of the rig so the field of view is checked before fabrication, not after.

## T-slot extrusion frames

Most rigs are built on aluminium extrusion. The critical fact: **slot width is not implied by
profile size.**

| Profile | Common slot widths | Typical fastener |
| --- | --- | --- |
| 20 x 20 mm | 5 mm or 6 mm depending on series | M4 or M5 T-nut |
| 30 x 30 mm | 8 mm typical | M6 T-nut |
| 40 x 40 mm | 8 mm or 10 mm depending on series | M6 or M8 T-nut |

A 20 mm profile from one supplier takes a 6 mm slot nut; from another, 5 mm. **Measure the slot,
or get the part number.** A bracket modelled for the wrong slot is scrap.

Design notes:

- Slot the bracket's mounting features along the extrusion axis. That is the whole point of
  extrusion — position is continuously adjustable, and a fixed hole throws that away.
- Extrusion faces are the datum. Design brackets to register flat against a face and, where
  possible, into the slot, so the part cannot rotate under load.
- Printed brackets carrying a camera or a heavy component should be treated as prototypes. Polymer
  creeps under sustained load and the camera will slowly droop out of alignment.

## Head fixation

The highest-consequence geometry in this file, and entirely lab-specific.

- The head-plate or head-post interface must come from the **actual implant** the lab uses, as a
  drawing or a measurement. There is no standard. Get the part.
- The kinematic requirement is to constrain the implant **repeatably and without play**, with
  clamping force that does not deflect the plate. Play translates directly into imaging or
  recording motion artefact.
- Fixation hardware must be **quick to release**, both for routine handling and in an emergency.
- Printed clamps flex. For any part carrying head-fixation load, recommend machined metal and
  present the printed version as a fit-check prototype only. Say this explicitly — it is a welfare
  issue as well as a data-quality one.

## Spouts, ports, and reward delivery

- Spout material must be non-toxic and cleanable; stainless steel tubing is the usual choice, held
  by a printed carrier that never itself contacts the animal's mouth.
- Position is a calibrated experimental variable. Make spout position **adjustable and readable**,
  and record it in the manifest, so it can be reproduced across sessions and animals.
- Model the reward line's dead volume — the delay between valve and spout is an experimental
  parameter. See the dead-volume formula in `references/microfluidics.md`.
- If lick detection is capacitive, keep conductive material away from the sensing element and give
  the wire a defined, strain-relieved route in the model.

## Checks to run

```bash
python scripts/gen.py arena_model.py --outdir out/
python scripts/check.py facts out/arena.step
python scripts/check.py clearance out/arena.step out/camera_mount.step --min 1.0
python scripts/snapshot.py out/arena.step --out out/arena.png
```

Confirm in the snapshot:

1. No gap an animal can get a limb, tail, or head into.
2. All animal-reachable edges broken; no sharp corners.
3. Camera has an unobstructed view of the whole floor.
4. Extrusion mounting features are slotted, and on the faces you can actually reach with a tool.
5. Nothing printed sits where it will be chewed.

## Sources

Deliberately none for dimensions. Arena, maze, and head-fixation geometry must come from the
protocol being replicated or from the physical implant, not from a general reference. The
material, cleaning, tracking, and extrusion guidance above is general engineering practice.

### `references/build123d-patterns.md`

# build123d 0.11.1 patterns

An API cookbook for the geometry this skill actually needs. Every snippet here was run against
build123d 0.11.1 on Python 3.12.

## Builder mode or algebra mode

build123d offers two equivalent APIs.

```python
# Builder mode: a context manager collects operations. mode= controls the boolean.
with BuildPart() as ex:
    Box(80.0, 60.0, 10.0)
    Cylinder(radius=11.0, height=10.0, mode=Mode.SUBTRACT)
part = ex.part

# Algebra mode: plain objects and operators.
part = Box(80.0, 60.0, 10.0) - Cylinder(radius=11.0, height=10.0)
```

**Use builder mode for parts in this skill.** Selectors (`ex.edges()`, `ex.faces()`) read naturally
from the builder, which is what you need for fillets and for placing features on found faces.
Algebra mode is a good fit for short, purely constructive shapes.

Do not mix the two styles inside one `build()`.

## The model file contract

`gen.py` imports the module, calls `build()`, and then reads `interfaces()`. Parameters must be
module-level so they can be overridden with `--param`.

```python
"""One-line description of the part.

Process: SLA, tough resin.  Orientation: bore axis vertical.
Interfaces:
  - Rod bores: 30 mm cage system, Thorlabs ER series (cage-system-30mm).
"""
from build123d import *

# --- INTERFACE (fixed; do not tune) ---
rod_spacing_mm = 30.0     # cage-system-30mm
rod_bore_d_mm = 6.4       # rod_diameter 6.0 + 2 x 0.20 SLA free-sliding (fabrication-limits.md)
# --- DESIGN (free) ---
plate_t_mm = 8.9
aperture_d_mm = 25.4


def interfaces() -> list[dict]:
    return [
        {"feature": "cage rod bore spacing", "standard": "cage-system-30mm",
         "dimension": "rod_spacing", "value": rod_spacing_mm, "intent": "match"},
        {"feature": "cage rod bore diameter", "standard": "cage-system-30mm",
         "dimension": "rod_diameter", "value": rod_bore_d_mm,
         "intent": "envelope", "clearance": 0.4},
    ]


def build() -> Part:
    half = rod_spacing_mm / 2
    with BuildPart() as plate:
        Box(rod_spacing_mm + 12.0, rod_spacing_mm + 12.0, plate_t_mm)
        with Locations((half, half), (-half, half), (half, -half), (-half, -half)):
            Hole(radius=rod_bore_d_mm / 2)
        Hole(radius=aperture_d_mm / 2)
    return plate.part
```

## Declaring interfaces

Most lab-hardware interfaces are **internal features** — a pocket, a bore, a slot — and none of
them appear in the part's outer bounding box. So `check.py fit` cannot find them by measuring the
STEP, and hand-copying the number into `--value` reintroduces exactly the transcription error the
skill exists to prevent. Declaring them closes the loop: `gen.py` records the declaration in the
manifest, and `check.py interfaces` verifies every entry.

Each entry needs `standard`, `dimension`, and `value`; `feature`, `intent`, and `clearance` are
optional:

| Key | Meaning |
| --- | --- |
| `standard` | ID from `check.py standards --list` |
| `dimension` | a dimension name inside that standard |
| `value` | the number **this model computed**, in mm |
| `feature` | human label for the check output (default: the dimension name) |
| `intent` | `match` if this part must itself conform; `envelope` if the feature must accept any conforming part (default: `match`) |
| `clearance` | total intended clearance in mm, both sides (default: 0) |

**Write `interfaces()` as a function, and compute derived dimensions inside functions.** A
module-level `INTERFACES = [...]` list is also accepted, but it is evaluated at import — before
`--param` is applied — so any value derived from an overridden parameter is recorded wrong. The same
applies to the geometry: derive inside `build()` or a helper, never at module level.

```python
# Wrong: --param plate_tol_mm=0 silently leaves pocket_l_mm at the old value
pocket_l_mm = plate_l_mm + plate_tol_mm + 2 * pocket_clearance_mm

# Right: recomputed on every call, so overrides land
def pocket_l_mm() -> float:
    return plate_l_mm + plate_tol_mm + 2 * pocket_clearance_mm
```

`gen.py` warns when it sees a static `INTERFACES` list together with `--param`.

## Declaring geometry checks

`interfaces()` compares declared numbers against the standards database; it never touches the
solid. `checks()` is its measured counterpart: a list of **go/no-go gauges** evaluated by boolean
intersection against the part `build()` actually produced. `gen.py` runs them on every
generation and fails the build if one fails; `check.py geometry` re-runs them against an
exported STEP.

The principle: **every geometric requirement in the request maps to one entry.** Something must
pass through (a screw, a beam, a probe) → a `clear` region. Something must fit into a void (a
plate into a pocket) → a `clear` box the size of the mating part at maximum material condition.
Something must remain (a ridge, a ledge, a screw seat) → a `material` region. A stated size
limit → a `bbox_*` bound. These are exactly the errors `is_valid`, the bounding box, and a
declared-number check cannot see.

```python
def checks() -> list[dict]:
    top = plate_t_mm / 2
    return [
        # a clear region: no material may intrude (screw shafts, through the part)
        {"feature": "M6 screws pass all four bores",
         "clear": {"cylinder": 6.0, "axis": "z", "at": bolt_xy()}},
        # a keep-out with an explicit span (a beam corridor along x at height z)
        {"feature": "beam clear at 15 mm above the bench",
         "clear": {"cylinder": 5.0, "axis": "x", "at": [(0.0, 15.0)]}},
        # a gauge part that must drop into a pocket: the mating part at MMC
        {"feature": "SLAS plate at MMC drops into the pocket",
         "clear": {"box": (128.01, 85.73, pocket_depth_mm()),
                   "at": [(0.0, 0.0, floor_t_mm + pocket_depth_mm() / 2)]}},
        # a counterbore that really is a counterbore: recess open, seat present.
        # The second entry is what catches a recess that punched through.
        {"feature": "counterbore recess open at the top",
         "clear": {"cylinder": cbore_d_mm - 0.2, "axis": "z", "at": bolt_xy(),
                   "span": (top - cbore_depth_mm + 0.1, top + 0.1)}},
        {"feature": "screw seat present below the recess",
         "material": {"cylinder": cbore_d_mm - 0.2, "axis": "z", "at": bolt_xy(),
                      "span": (-top + 0.1, top - cbore_depth_mm - 0.1)},
         "min_mm3": 50.0},
        # a user-stated hard limit, measured from the solid
        {"feature": "clears the objective turret", "bbox_z": {"max": 15.0}},
    ]
```

Semantics:

| Key | Meaning |
| --- | --- |
| `clear` / `material` | region that must contain no material / must contain material |
| `{"cylinder": DIA, "axis": "x"\|"y"\|"z", "at": [(a, b), ...], "span": (lo, hi)}` | `at` is 2D in the plane perpendicular to the axis — axis `z`: (x, y); axis `x`: (y, z); axis `y`: (x, z). Omit `span` to run through the whole part |
| `{"box": (dx, dy, dz), "at": [(x, y, z), ...]}` | axis-aligned box gauges centred at each position |
| `tol_mm3` / `min_mm3` | pass thresholds per position (both default 0.01) |
| `bbox_x`…`bbox_z`, `bbox_min/mid/max` | `{"min": mm, "max": mm}` bounds on the measured bounding box |

Size the gauges from the same named constants as the geometry **only when the requirement is
relational** (the recess sits above the seat). When the requirement is absolute — a mating part's
MMC, a user's height limit, a beam position — write the gauge from the requirement's own numbers,
so a wrong parameter cannot shrink the gauge to match the wrong geometry.

For a one-off question without editing the model, `check.py probe` runs a single gauge from the
command line, and `check.py bores` prints a census of every cylindrical face (diameter, axis,
position, span, sweep) to reconcile against the model's intent.

## Positioning

`Locations` places the objects created inside it. It is the workhorse for bolt patterns.

```python
with Locations((10.0, 0.0), (-10.0, 0.0)):        # two positions on the current plane
    Hole(radius=3.3)

with Locations((0.0, 0.0, floor_t_mm)):           # offset in z
    Box(10.0, 10.0, 5.0, mode=Mode.SUBTRACT)

with GridLocations(9.0, 9.0, 12, 8):              # x spacing, y spacing, x count, y count
    Hole(radius=1.5)
```

`GridLocations` centres the grid on the origin. A microplate well grid is dimensioned from the
plate corner instead, so compute absolute positions and pass them to `Locations`:

```python
a1_x_mm, a1_y_mm, pitch_mm = 14.38, 11.24, 9.0    # slas-well-positions-96
origin_x = -plate_l_mm / 2
origin_y = plate_w_mm / 2
wells = [
    (origin_x + a1_x_mm + pitch_mm * col, origin_y - a1_y_mm - pitch_mm * row)
    for row in range(8) for col in range(12)
]
with Locations(*wells):
    Hole(radius=well_clear_d_mm / 2)
```

## Alignment

By default objects are centred on the origin. `align` moves the datum, which is usually what you
want for a pocket that starts at a floor:

```python
Box(x, y, z, align=(Align.CENTER, Align.CENTER, Align.MIN))   # sits on z = 0
Box(x, y, z, align=(Align.MIN, Align.MIN, Align.MIN))         # corner at the origin
```

Getting this wrong is the classic "pocket cut through the floor" bug, and it is exactly what the
snapshot catches.

## Holes

`Hole` cuts through the whole part; `CounterBoreHole` and `CounterSinkHole` add a head recess.

**`CounterBoreHole` cuts downward from the workplane it is placed on, with the recess at that
plane.** On a centred `Box` the default workplane is the mid-height of the part, so a 2-tuple
location buries the screw seat inside the plate — or, on a thin plate, lets the recess swallow the
top entirely, leaving a straight bore the screw head falls through. Place it on the **top face**
(or give the location an explicit z at the top):

```python
with BuildPart() as plate:
    Box(60.0, 60.0, 10.0)                              # spans z = -5 .. +5
    top = plate.faces().sort_by(Axis.Z)[-1]
    with Locations(top):
        with Locations((20.0, 20.0)):
            CounterBoreHole(radius=6.6 / 2, counter_bore_radius=11.0 / 2,
                            counter_bore_depth=6.5)
```

Size `counter_bore_depth` from the **screw head height**, not from habit: an M6 socket head cap
screw head is 6.0 mm tall, a 1/4-20 head 6.35 mm (`screw_head_height` in the breadboard
standards). A 4 mm counterbore leaves either head 2 mm proud — do not call that flush. After
generating, confirm in the snapshot (or a section) that the recess is at the top face and the
seat ledge exists; both failure modes here pass `is_valid` and the bounding box untouched.

Remember that printed holes come out undersize — see `references/fabrication-limits.md`.

## Selectors

Selectors find edges and faces to fillet, chamfer, or build on. The three you need:

```python
part.edges().filter_by(Axis.Z)              # keep edges parallel to Z (the vertical corners)
part.edges().group_by(Axis.Z)[-1]           # the group with the highest Z (the top edges)
part.faces().sort_by(Axis.Z)[-1]            # the single highest face
part.edges().filter_by(GeomType.CIRCLE)     # only circular edges
```

`filter_by` keeps everything matching. `group_by` partitions into lists ordered by the key, so
`[-1]` is the last group and `[0]` the first. `sort_by` orders individual items.

```python
with BuildPart() as ex:
    Box(80.0, 60.0, 10.0)
    chamfer(ex.edges().group_by(Axis.Z)[-1], length=4.0)   # chamfer the top face edges
    fillet(ex.edges().filter_by(Axis.Z), radius=5.0)       # round the vertical corners
```

**These broad selectors are only safe on a part that is still a plain box.** Once the part has
pockets, bores, notches, or micro-relief, `filter_by(Axis.Z)` and `group_by(Axis.Z)[-1]` also
select the edges of those features, and the fillet either throws a kernel error
(`Failed creating a fillet`, `BRep_API: command not done`) or — worse — succeeds and silently eats
a wall or a 0.3 mm ridge. Both happen in practice. So:

- Fillet or chamfer the **outer body before adding internal features**, or filter the selection
  down deliberately (by position, length, or `GeomType`) so only the intended edges remain.
- Bound the radius with `part.max_fillet(edges)` when the nearby geometry is tight — it returns
  the largest radius the kernel can actually build on that edge set.
- Make every fillet/chamfer radius a named parameter, and on a kernel failure back the value off
  rather than fighting the selector.
- Then check the snapshot: a consumed feature is obvious in the picture and invisible in
  `is_valid`.

## Sketch then extrude

For a profile that is not a primitive, sketch it and extrude:

```python
with BuildPart() as bracket:
    with BuildSketch() as profile:
        Rectangle(40.0, 20.0)
        with Locations((15.0, 0.0)):
            Circle(radius=4.0, mode=Mode.SUBTRACT)
    extrude(amount=6.0)
```

This is also the route to a laser-cut DXF: the sketch is the cut profile.

## Exports

`gen.py` handles these, but for reference:

```python
export_step(part, "part.step", unit=Unit.MM)                 # authoritative
export_stl(part, "part.stl", tolerance=1e-3, angular_tolerance=0.1)

# 2D profile for laser cutting. section() is a module-level operation, NOT a
# method on the shape -- part.section(...) raises AttributeError.
from build123d.exporters import ColorIndex   # NOT exported by `from build123d import *`

profile = section(part, Plane.XY.offset(z_mm), mode=Mode.PRIVATE)
profile = profile.moved(Location((0, 0, -z_mm)))   # back to z = 0, or the DXF writer
                                                   # warns about a non-planar shape
exporter = ExportDXF(unit=Unit.MM)
exporter.add_layer("CUT", color=ColorIndex.RED)    # laser shops key power/speed to layers
exporter.add_shape(profile, layer="CUT")
exporter.write("part.dxf")
```

Cut the section through material, not at `z = 0`: a part modelled sitting on the build plate has
only a degenerate face there. `gen.py --dxf` defaults to the part's mid-height and takes `--dxf-z`
to override.

STEP preserves exact BREP geometry; STL is a triangulated approximation. **Always keep STEP as the
source of truth** and regenerate meshes from it, never the reverse.

## Measuring in code

Useful for asserting an interface inside the model itself:

```python
bbox = part.bounding_box()
print(bbox.size.X, bbox.size.Y, bbox.size.Z)
print(part.volume, part.area)
print(part.is_valid)          # a property in 0.11.1, not a method
print(part.center(CenterOf.MASS))
```

`is_valid` being a property rather than a method is a real difference from older releases and from
some documentation. Access it without parentheses.

## Things that bite

- **`is_valid` is a property.** `part.is_valid()` raises `TypeError: 'bool' object is not callable`.
- **`section()` is a module-level operation, not a method.** `part.section(Plane.XY)` raises
  `AttributeError`. Call `section(part, plane, mode=Mode.PRIVATE)`.
- **`intersect()` returns a `ShapeList`** with no `.volume`; the `&` operator returns a `Solid` that
  has one. `check.py clearance` handles both.
- **Never name a script `inspect.py`** in a directory that lands on `sys.path`. It shadows the
  standard library `inspect` module, which breaks `typing_extensions` and therefore build123d
  itself. This is why the bundled script is `check.py`.
- **Builder objects are not parts.** Return `builder.part`, not the builder.
- **`Mode.SUBTRACT` needs an existing body.** Subtracting from an empty context does nothing
  silently.
- **A swept or extruded profile is centred on its path/plane unless you align it.** Sweeping a
  `Rectangle(w, h)` along a path on a surface leaves half the profile below the surface — a
  "0.3 mm ridge" that is really 0.15 mm proud. Pass `align=` (and an explicit `x_dir` on the
  profile plane) so the profile sits where you think it does, then measure the result.
- **`Curve` has no `.length`.** Sum the edges instead: `sum(e.length for e in curve.edges())`.
- **The boolean of touching or disjoint solids is empty, not an error.** Depending on the path you
  get `None`, an empty `Compound`, or a `ShapeList` with no `.volume` — guard before reading
  `.volume` in any interference check.
- **`ColorIndex` and `LineType` live in `build123d.exporters`**, not in the top-level namespace;
  `from build123d import *` does not bring them in, and `add_layer(color=1)` fails.
- The OpenCascade kernel raises assorted exception types. Catch broadly around boolean operations
  and report the failure rather than letting a traceback escape.

## Sources

- build123d documentation — <https://build123d.readthedocs.io/en/latest/>
- Introductory examples (builder vs algebra, selectors, fillets) —
  <https://build123d.readthedocs.io/en/latest/introductory_examples.html>
- Import/export reference — <https://build123d.readthedocs.io/en/latest/import_export.html>

### `references/fabrication-limits.md`

# Fabrication limits, tolerances, and materials

Read this before finalising any geometry. Process determines what geometry is possible; material
determines whether the part survives the lab.

## Process tolerances

Achievable tolerance and minimum feature size, as planning figures. **Every number here depends on
the specific machine, material, and operator.** Use them to choose a process and to size a first
article, then verify with a test coupon.

| Process | Typical tolerance | Min wall | Min feature | Notes |
| --- | --- | --- | --- | --- |
| FDM | ±0.3 mm (often worse over 100 mm) | 1.2 mm (3 x 0.4 mm nozzle) | ~0.8 mm | Anisotropic: much weaker across layers. Porous. |
| SLA / DLP | ±0.1 mm | 0.8 mm | ~0.3 mm | Better surface and detail. Resin choice dominates properties. |
| SLS (nylon) | ±0.2 mm | 0.8 mm | ~0.5 mm | Isotropic, no supports, slightly porous surface. |
| CNC milling | ±0.05 mm or better | 0.8 mm in metal | Set by tool diameter | Internal corners carry the tool radius — you cannot mill a sharp internal corner. |
| Laser cutting | ±0.1 mm | n/a | Kerf ~0.1-0.3 mm | 2D only. Edge taper on thick stock. Kerf offset must be applied. |

Two consequences that catch people:

- **Holes print undersize** on both FDM and SLA. A 6.0 mm modelled hole typically measures under
  6.0 mm. Oversize functional bores, or plan to ream them.
- **Internal corners cannot be sharp in milling.** If a milled pocket must accept a square part,
  add corner relief cuts. (For a part with *rounded* corners the tool radius is harmless as long
  as it stays at or below the part's minimum corner radius — see the corner-radius rule in
  `references/labware-adapters.md`.)

### Laser cutting

- **Kerf direction is fixed by the physics, so get it right in the handover.** The beam removes a
  strip of width k (~0.1–0.3 mm) centred on the drawn line. Cutting on the line therefore makes
  **holes and internal cutouts come out oversize by ~k, and the part's outer outline undersize by
  ~k**. Say which convention the DXF uses (on-the-line is the default assumption) and let the shop
  offset, or offset the geometry yourself and say so — never both.
- **Put cut geometry on a named layer** (one layer per operation: `CUT`, `ENGRAVE`). Shops key
  power and speed to layer or colour; geometry on layer 0 forces them to guess.
- **Cut order matters:** internal features before the outer outline, or the part shifts once it is
  freed from the sheet.
- **Sheet stock is not its nominal thickness.** "3 mm" acrylic commonly runs ~2.8–3.2 mm; slots
  sized for nominal will be loose or tight. For solvent-welded joints prefer **cast** acrylic over
  extruded — cleaner cut edge, less vapour crazing — and remember alcohols craze acrylic either
  way (see Chemical, below).
- Laser-cut edges are sharp and slightly tapered; call out deburring or flame-polishing for
  anything handled or animal-facing.

## Fits and clearances

Nominal dimensions do not produce fits. Choose a clearance deliberately, per side:

| Fit | FDM | SLA | CNC |
| --- | --- | --- | --- |
| Free-sliding (a plate dropping into a pocket) | 0.40 mm | 0.20 mm | 0.10 mm |
| Located but removable by hand | 0.25 mm | 0.10 mm | 0.05 mm |
| Press / interference | -0.05 mm | -0.03 mm | -0.02 mm |

Then remember the **other** part has tolerance too. When mating to a standardised component,
design the receiving feature against the component's **maximum material condition**, not its
nominal — a pocket sized from nominal fits only the smaller half of conforming parts. This is what
`intent: "envelope"` enforces. Declare it in the model and check the manifest:

```bash
python scripts/check.py interfaces out/part.manifest.json
```

Or check a single number by hand:

```bash
python scripts/check.py fit --standard slas-microplate-footprint \
  --intent envelope --clearance 0.8 --value footprint_length=128.81
```

## Threads and inserts

**Printed threads are usually a mistake.** Layer resolution is comparable to the thread pitch, so
printed threads are weak, dimensionally unreliable, and shed particles.

In descending order of preference:

1. **Heat-set threaded inserts** — the standard solution for printed parts. Model a straight bore
   to the insert manufacturer's specified diameter (it varies by insert; get the datasheet) and
   provide enough surrounding wall, typically at least 2 mm.
2. **Clearance hole plus a captive nut** in a hex pocket. Reliable and cheap.
3. **Tapping the printed material directly** — acceptable for light, infrequently-assembled joints.
4. **Printing the thread** — only for coarse threads (roughly M6 and above), never for fine
   threads like the 0.635 mm pitch SM1 (see `references/optomechanics.md`).

## Orientation and anisotropy

For FDM especially, orientation is a design decision, not a printing detail:

- Parts are substantially weaker **across** layers than along them. Orient so that load runs
  along layers, and state the intended orientation in the model docstring.
- Overhangs beyond roughly 45 degrees need support, and supported surfaces come out rough and
  dimensionally poor. If a surface is a sealing or mating face, orient it so it is not supported.
- Holes printed with their axis vertical are round; printed horizontally they come out with a
  drooped top. Teardrop or chamfer horizontal holes that must stay round.
- **Every enclosed cavity needs a drain path** in resin printing. See
  `references/microfluidics.md`.

## Materials

### Thermal

| Material | Approximate service limit | Autoclave (121 °C)? |
| --- | --- | --- |
| PLA | ~50-60 °C | **No** — distorts well below autoclave temperature |
| PETG | ~70-80 °C | No |
| ABS / ASA | ~90-100 °C | Marginal, generally no |
| Polypropylene | ~100 °C | Marginal |
| Nylon (SLS) | ~120-160 °C | Sometimes; verify per grade |
| PEEK | >250 °C | Yes |
| Stainless steel, aluminium, glass | High | Yes |

**Assume a printed part is not autoclavable unless it is a verified high-temperature material.**
Offer chemical or gas sterilisation as the alternative, and check that against the solvent notes
below.

### Chemical

- **Acrylic (PMMA)** crazes on contact with alcohols, including 70% ethanol — a serious problem in
  a lab that disinfects everything with ethanol.
- **Polycarbonate** is attacked by many solvents and by some alkaline cleaners.
- **PLA** hydrolyses; it degrades in warm, wet, or repeatedly-cleaned service.
- **PP, PTFE, PEEK** have broad chemical resistance and are the safe choices for solvent contact.

Always ask what the part will be cleaned with, not just what it will contain. Cleaning agent
compatibility is more often the failure than the sample.

### Biocompatibility

- **Uncured SLA resin is cytotoxic.** Even nominally biocompatible resins require the
  manufacturer's full post-cure and wash protocol, and leachables can still affect sensitive cell
  assays.
- For anything contacting cells, tissue, or animals: prefer glass, medical-grade polymer, or PTFE
  for the contact surface, and use the printed part as a holder that does not touch the sample.
- "Biocompatible" on a resin datasheet refers to a specific certified process and application. It
  does not transfer to your printer, your cure schedule, or your assay. Say this rather than
  implying a printed part is cell-safe.

### Optical

- Printed and milled surfaces scatter; they are not optical surfaces.
- Most printed resins **autofluoresce**, often strongly, which contaminates fluorescence readouts.
- Black is not automatically non-reflective.
- Where an optical surface is needed, use glass or a bonded film and model the holder around it.

## Cost and lead-time reality

Mention these when recommending a process: FDM is hours and pennies; SLA is hours and modest cost;
SLS and CNC are typically outsourced with days of lead time and much higher cost. A design that
needs ±0.05 mm has committed the user to CNC — flag that trade before they discover it at quoting.

## Before fabrication

Work through `references/validation.md`.

### `references/labware-adapters.md`

# Labware adapters, holders, and racks

Parts that receive standard consumables: microplates, cuvettes, tubes, slides, dishes.

The governing principle: **where a published standard exists, design to the standard; where it
does not, require a measurement.** Microplate footprints are standardised. Well geometry, skirt
profiles, tube dimensions, and lid fits are not.

Verified dimensions live in `assets/standards.json`. Query them rather than copying numbers:

```bash
python scripts/check.py standards --show slas-microplate-footprint
```

## Microplates (ANSI/SLAS 1-4)

Four documents split the plate geometry. All are ANSI-approved and were reaffirmed in 2012.

| Document | Governs | Key numbers |
| --- | --- | --- |
| ANSI/SLAS 1-2004 | Footprint | 127.76 x 85.48 mm ±0.25; corner radius 3.18 ±1.6 mm |
| ANSI/SLAS 2-2004 | Height | 14.35 ±0.25 mm, resting plane to top of perimeter wells |
| ANSI/SLAS 3-2004 | Bottom outside flange | Short 2.41, medium 6.10, tall 7.62 mm, each ±0.38 |
| ANSI/SLAS 4-2004 | Well positions | 96-well: 9.0 mm pitch, A1 at 14.38 mm from left, 11.24 mm from top |

### Designing a plate pocket

Three traps, in the order people fall into them.

**1. Design to maximum material, not to nominal.** A plate at the top of tolerance is
127.76 + 0.25 = 128.01 mm. A pocket cut at 127.76 + clearance will jam on roughly half the plates
you try. Compute:

```python
plate_l_mm = 127.76      # ANSI/SLAS 1-2004 nominal
plate_tol_mm = 0.25      # ANSI/SLAS 1-2004
fit_clearance_mm = 0.40  # per side; FDM, see fabrication-limits.md
pocket_l_mm = plate_l_mm + plate_tol_mm + 2 * fit_clearance_mm   # 128.81
```

**2. The corner radius tolerance is enormous — and it bounds the pocket radius from above,
not below.** 3.18 ±1.6 mm means a real plate corner is anywhere from 1.58 to 4.78 mm. Get the
direction right: a plate corner is **convex**, a pocket fillet is **concave material bulging
inward**, so a *sharp* internal pocket corner always clears a rounded plate — the unused corner is
empty space. It is a pocket fillet *larger* than the plate's corner radius that binds: the bulge
occupies space the plate needs. Sizing the fillet to the plate's maximum corner radius is
therefore exactly backwards — it binds every plate except those at the top of the corner
tolerance.

The safe options, best first:

- **Corner relief** (a small slot or bore cut past each corner) — always clears, prints and mills
  cleanly, and is the standard fix.
- **Fillet no larger than the plate's minimum corner radius** (1.58 mm for SLAS plates) — clears
  every conforming plate in every position.
- A larger fillet only if `R ≤ r_min + ~3.4 × per-side clearance` — the geometry only recovers the
  intrusion when the plate stays roughly centred, so treat this as a last resort and say so.

```python
with BuildPart() as pocket:
    # ... pocket geometry ...
    # relief bores just outside each pocket corner: clears any conforming corner radius
    with Locations(*corner_relief_centres()):
        Hole(radius=2.0)
```

**3. Height depends on the flange, not just the plate.** ANSI/SLAS 3 standardises three flange
heights. A carrier that grips the flange must be told which one. Ask; do not assume medium.

### Well grid

For a part that must reach individual wells — a magnet block, a lid with access holes, a light
guide — lay out from the plate's outline corner, not from the plate centre:

```python
a1_x_mm, a1_y_mm, pitch_mm = 14.38, 11.24, 9.0   # ANSI/SLAS 4-2004, 96-well
locations = [
    (a1_x_mm + pitch_mm * col, a1_y_mm + pitch_mm * row)
    for row in range(8) for col in range(12)
]
```

The standard's positional tolerance is a **0.70 mm diameter zone** around each nominal centre, not
a ±0.70 mm band. A feature that must clear every well needs at least 0.35 mm of radial margin on
top of your own process tolerance.

384-well pitch is 4.5 mm and 1536-well pitch is 2.25 mm. **The A1 offsets for those formats in
`standards.json` are marked unverified** — they were derived, not read from the document. Read
ANSI/SLAS 4-2004 before relying on them.

### What the standards do not fix

Well diameter, well depth, well bottom shape (flat, round, conical), skirt height, lid geometry,
optical bottom thickness, and deep-well plate height. All vary by manufacturer and product line.
If the part touches any of these, get the vendor drawing or measure it.

## Cuvettes

The standard macro cuvette is a convention rather than a published standard, but it is close to
universal: **12.5 x 12.5 mm external, 45 mm tall, 1.25 mm wall, 10 mm optical path**.

Design notes:

- Holders should be generous or compliant. Because no document fixes the tolerance, a 0.1 mm
  interference fit designed against nominal will fail on some suppliers' cuvettes.
- Semi-micro and micro cuvettes keep the 12.5 mm external footprint but change internal geometry
  and often height. A holder designed for the external footprint accommodates all of them; one
  designed around the sample volume does not.
- Cuvettes are usually held with a spring or leaf on one face so the two optical faces register
  against fixed datums. Copy that: locate on two adjacent faces, preload from the opposite corner.
  A four-sided pocket with clearance lets the cuvette rotate and shifts the path length.
- **Never print the optical path.** Printed surfaces scatter. The cuvette provides the optical
  faces; the holder provides position only, and must not obstruct the beam window.

## Tubes

Tube dimensions are **not standardised** and differ measurably between suppliers, and often
between product lines from the same supplier. Approximate outside diameters near the tube rim:

| Tube | Approximate OD | Note |
| --- | --- | --- |
| 0.2 mL PCR | 6 mm | Often supplied in strips or as a 96-format plate |
| 1.5 mL microcentrifuge | 11 mm | Rim is wider than the body; the body tapers |
| 2.0 mL microcentrifuge | 11 mm | Same rim as 1.5 mL, taller body |
| 15 mL conical | 17 mm | Cap is wider than the tube |
| 50 mL conical | 30 mm | Cap is wider than the tube |

**Treat every number in this table as a starting point for a first article, not a design input.**
Ask the user for the supplier and catalogue number, or ask them to measure with calipers. Then
design a rack that holds the tube by the **rim or the cap**, which is dimensionally stable, rather
than by the tapered body, which is not.

For a rack, the useful pattern is a through-hole sized to the body plus clearance and a counterbore
that catches the rim, so the tube hangs rather than bottoms out.

## Microscope slides and coverslips

Standard slide: **75 x 25 mm, 1.0 mm thick** (ISO 8037-1 covers slide dimensions; thickness classes
vary, and 1.0-1.2 mm is typical). Coverslips are specified by thickness number, not dimension:
#1 is roughly 0.13-0.17 mm and #1.5 roughly 0.16-0.19 mm.

Objective working distance is unforgiving. A holder that adds even 0.2 mm under the slide can put
the sample outside a high-NA objective's working distance. Design slide holders so the slide
registers directly against the stage datum, with the holder clamping from above.

## Petri dishes and stage inserts

Standard dish outside diameters are approximately 35, 60, 90, and 100 mm, but the flange profile
and lid fit vary. Dishes are also slightly out of round. Locate on three points rather than a
continuous circular pocket: a three-point nest is insensitive to ovality, a close-fitting bore is
not.

For stage inserts, the interface that matters is the **microscope stage opening**, which is
instrument-specific and must be measured. Many stages accept a standard SLAS-footprint insert;
confirm before assuming it.

## Checks to run

Declare the pocket in the model's `interfaces()` and let the check read it:

```bash
python scripts/gen.py carrier_model.py --outdir out/
python scripts/check.py interfaces out/carrier.manifest.json
```

**Do not point `check.py fit` at the carrier's STEP.** `fit` measures the outer bounding box, which
for a carrier is the outside of its walls — 6 mm larger than the pocket here — so it fails against
the plate footprint no matter how correct the pocket is. The dimension that matters is internal, so
it has to be declared, not measured from the envelope.

To check the number by hand instead:

```bash
python scripts/check.py fit --standard slas-microplate-footprint \
  --intent envelope --clearance 0.8 --value footprint_length=128.81
```

`--intent envelope` checks one-sided against maximum material condition, and `--clearance` is the
total intended clearance: 0.40 mm per side is 0.80 mm. Passing means the pocket is the size you
intended, not that the plate fits — only a test print shows that.

Then always run `snapshot.py` and confirm the pocket is on the face you meant.

## Sources

- ANSI/SLAS 1-2004 (R2012) Footprint Dimensions — <https://www.slas.org/SLAS/assets/File/public/standards/ANSI_SLAS_1-2004_FootprintDimensions.pdf>
- ANSI/SLAS 2-2004 (R2012) Height Dimensions — <https://www.slas.org/SLAS/assets/File/public/standards/ANSI_SLAS_2-2004_HeightDimensions.pdf>
- ANSI/SLAS 3-2004 (R2012) Bottom Outside Flange Dimensions — <https://www.slas.org/SLAS/assets/File/public/standards/ANSI_SLAS_3-2004_BottomOutsideFlangeDimensions.pdf>
- ANSI/SLAS 4-2004 (R2012) Well Positions — <https://www.slas.org/SLAS/assets/File/public/standards/ANSI_SLAS_4-2004_WellPositions.pdf>
- SLAS microplate standards overview — <https://www.slas.org/education/ansi-slas-microplate-standards/>

### `references/microfluidics.md`

# Microfluidic chips, molds, and flow cells

Channel networks, soft-lithography molds, printed chips, gaskets, and manifolds.

## First: decide what you are actually modelling

This is the error that wastes the most time in microfluidic CAD. Three different objects get
called "the chip":

| Object | Channels are | Made by |
| --- | --- | --- |
| **Mold / master** | **Raised ridges** (positive relief) | Photolithography on a wafer, SLA print, or micromilling |
| **Cast chip** | **Recessed grooves** (negative of the mold) | PDMS cast against the mold, then bonded to a substrate |
| **Directly-fabricated chip** | **Recessed grooves or enclosed lumens** | Printed, milled, or laser-cut directly |

A model that is correct as a chip is exactly wrong as a mold. Put the polarity in the module
docstring and in a named parameter, and **verify it numerically, not by eye**: inverted polarity
is invisible in the bounding box, the volume, and the validity check — and at typical channel
scale (a 0.3 mm ridge on a 40+ mm part) it is invisible in an outline render too, because raised
and recessed features draw the same edges. Declare it as geometry checks instead
(`references/build123d-patterns.md`): a `material` region where the ridge must stand above the
casting surface, and a `clear` region over the rest of that layer — a groove fails the first,
an inverted full-area layer fails the second. For a one-off question,
`check.py probe <step> --box ... --expect material` answers it without editing the model. State
the measured relief height in the report. Use the snapshot for layout and connectivity, which
it does show well.

```python
polarity = "mold"   # "mold" = raised ridges; "chip" = recessed grooves
```

If casting PDMS, the mold also needs a **surrounding wall or a casting frame** to contain the
uncured polymer, and enough flat land around the features for the cast part to release.

## Channel cross-section and aspect ratio

Channels are usually rectangular because that is what planar fabrication produces. Two failure
modes bound the aspect ratio, and both are geometric:

- **Roof sag / collapse** — a channel much wider than it is tall has an unsupported ceiling. In
  PDMS the roof bows down and can stick to the floor. Commonly cited guidance keeps
  **width : height below roughly 10 : 1**; wide channels need support pillars.
- **Sidewall collapse** — a mold ridge much taller than it is wide falls over or fails to release.
  Keep **height : width below roughly 10 : 1** on the mold.

Treat both as rules of thumb, not guarantees: the real limits depend on PDMS mixing ratio, cure
schedule, and applied pressure. For anything load-bearing or high-pressure, prototype.

Also keep **channel-to-channel spacing at least the channel height**, so the wall between two
channels does not deflect or leak, and leave a flat **bonding land** — typically 1 mm or more of
uninterrupted flat surface around the network perimeter — for plasma or adhesive bonding.

## Minimum features by process

Achievable feature size drives the entire design, and the range across processes is three orders
of magnitude. Confirm against your specific tool before committing.

| Process | Practical minimum channel | Notes |
| --- | --- | --- |
| SU-8 photolithography | ~1-10 µm wide, 1-200+ µm tall | The reference process for soft lithography. Feature height is set by spin speed and resist grade. |
| Two-photon / µSLA | ~10-50 µm | Small build volume, slow, expensive. |
| Desktop SLA / DLP | ~200-500 µm | Uncured resin is very hard to clear from smaller lumens. Enclosed channels below ~0.5 mm frequently print blocked. |
| Micromilling | ~100 µm | Set by end-mill diameter; depth limited by tool aspect ratio. Leaves tool marks that scatter light. |
| FDM | Not suitable for sealed channels | Layer porosity leaks. Use only for holders and manifolds. |
| Laser-cut film / gasket | ~200 µm | Excellent for stacked-layer devices and gaskets. |

**Design enclosed printed channels for drainage.** Every lumen needs a path for uncured resin to
escape, and orientation on the build plate determines whether it drains. If the user is printing,
say which way up.

## Ports and tubing

The port is where most chips leak. Options, roughly in order of how common they are in a research
lab:

- **Direct tubing insertion** — a bore slightly *under* the tubing OD so the tubing seals by
  interference. For 1/16 inch OD tubing (1.5875 mm), a bore around 1.5 mm in PDMS is typical. This
  works in elastomer and fails in rigid printed parts, which crack instead of gripping.
- **Luer taper** — the standard syringe interface, a **6% taper** (ISO 80369-7 supersedes the
  legacy ISO 594 series for medical use). Convenient, low pressure only. If you model a Luer taper,
  get the profile from the standard, not from memory.
- **Threaded fittings** — flat-bottom **1/4-28 UNF** is the common lab standard for low-pressure
  fluidics; **10-32 coned** is used at higher pressures. These need a tapped or heat-set-insert
  port and a matching flat sealing face.
- **Barbs** — reliable with soft tubing and a clamp, bulky.

Whichever you choose, the sealing surface must be **flat and normal to the port axis**. A port
face left at a printed layer angle will not seal.

## Dead volume

Dead volume dominates the response time of any perfusion or gradient device, and it is trivially
computable, so compute it rather than estimating:

```
V = pi * r^2 * L                # round tubing / bore
V = w * h * L                   # rectangular channel
```

Report the volume of every connecting bore alongside the channel network volume. A 20 mm long
1 mm bore holds ~15.7 µL, which is often larger than the entire channel network it feeds.

## Flow regime sanity check

Microfluidic flow is almost always laminar, but state it rather than assuming:

```
Re = rho * v * D_h / mu
D_h = 2 * w * h / (w + h)       # hydraulic diameter, rectangular channel
```

For water in a 100 µm channel at 1 mm/s, Re is of order 0.1 — deeply laminar, so mixing is
diffusive only. If the design depends on mixing, it needs a mixer geometry (serpentine,
herringbone, or split-and-recombine); relying on turbulence will not work at these scales.

Pressure drop for a rectangular channel scales steeply with the smaller dimension. **Halving
channel height raises pressure drop by roughly an order of magnitude.** Check that the intended
pump or syringe can actually deliver it before finalising the cross-section.

## Material and optical constraints

- **PDMS** absorbs small hydrophobic molecules and is gas-permeable. Both are sometimes features
  (oxygenation in organ-on-chip) and sometimes fatal to an assay (drug studies).
- **SLA resins** are frequently cytotoxic uncured and often still after a nominal cure. For cell
  work, require post-cure plus a documented biocompatibility check, or use a different process.
  See `references/fabrication-limits.md`.
- **Autofluorescence** matters for any fluorescence readout. Most printed resins autofluoresce
  strongly. Image through glass or a thin COC/COP film, not through printed material.
- **Optical path**: printed and milled surfaces scatter. Any imaging window should be a bonded
  coverslip or film, and the model must specify its thickness so the objective working distance
  works out.

## Checks to run

```bash
python scripts/gen.py chip_model.py --outdir out/
python scripts/check.py facts out/chip.step
python scripts/snapshot.py out/chip.step --out out/chip.png
```

`facts` gives the volume; compare it against your hand-computed channel volume as an independent
check that the network is actually open and connected. A network modelled as a solid rather than a
cavity shows up immediately as a volume far larger than expected.

Then read the snapshot and confirm, explicitly:

1. **Polarity** — ridges for a mold, grooves for a chip.
2. Every port lands on the channel it should, and passes fully through to the surface.
3. The bonding land is continuous around the network.
4. No channel has been closed off or consumed by a fillet.

## Sources

- ISO 80369-7 (Luer connectors for intravascular applications) supersedes the ISO 594 series.
  Obtain the taper profile from the standard itself.
- Aspect-ratio and spacing guidance here is standard soft-lithography practice; the numerical
  limits are rules of thumb and depend on material and process. Prototype before committing.

### `references/optomechanics.md`

# Optomechanical mounts and breadboard hardware

Parts that bolt to an optical table, join a cage system, hold an optic or a sample in a beam path,
or carry a camera or objective.

Verified dimensions are in `assets/standards.json`:

```bash
python scripts/check.py standards --show optical-breadboard-metric
python scripts/check.py standards --show cage-system-30mm
python scripts/check.py standards --show sm1-lens-tube-thread
```

## Ask which system before you model anything

**Metric and imperial optical hardware are not interchangeable, and the difference is small enough
to look like a rounding error and large enough to prevent assembly.**

| | Metric | Imperial |
| --- | --- | --- |
| Grid pitch | 25.0 mm | 25.4 mm (1 inch) |
| Tapped hole | M6 x 1.0 | 1/4-20 UNC |
| Typical border | 12.5 mm | 12.7 mm |

Over a four-hole span the grids differ by **1.6 mm** — far more than any clearance hole absorbs.
There is no way to infer which the user has from the request. Ask. If the answer is unavailable,
model the mounting features as **slots along the bolt line** rather than round holes, which
tolerates both, and say that is what you did and why.

## Mounting to the table

- Use **clearance holes, not tapped holes**, in the part. The table is tapped; the part is
  clearanced. For M6 use 6.6 mm (normal fit) in a printed part rather than 6.4 mm — printed holes
  come out undersize.
- **Counterbore for the screw head** if the part surface must stay clear: roughly 11 mm diameter
  for an M6 socket head cap screw, 11.2 mm for 1/4-20.
- **Never rely on more than two holes to locate a part.** Grid tolerance plus print tolerance means
  a rigid four-hole pattern will bind. Round hole + slot is the standard fix: one hole locates, the
  slot takes up the error.
- Printed parts are compliant. For anything where pointing stability matters, a printed mount is a
  prototyping aid, not a final part — thermal drift and creep in polymer are large compared with
  optical alignment tolerances. Say so when recommending one.

## Posts and pedestals

Common conventions, which vary by vendor — **confirm against the catalogue before use**:

- Imperial posts are Ø1/2 inch (12.7 mm), typically tapped 8-32 at one end with a 1/4-20 stud or
  clearance at the other.
- Metric posts are Ø12 mm, typically tapped M4 with an M6 interface to the table.
- A post-holder plus post is height-adjustable but adds a compliant joint; a pedestal or a
  solid machined riser is stiffer.

**Beam height** is a project-wide constant, not a per-part choice. Every mount on the table must
put its optic at the same height. Common conventions are 3 inches (76.2 mm) or 100 mm, but this is
a lab-by-lab choice. Ask for the number, define it once as `beam_height_mm`, and derive every
mount's optic centre from it.

## 30 mm cage system

The dominant convention for small free-space assemblies:

- **Rod spacing 30.0 mm** on a square, centred on the optical axis.
- **Rods Ø6 mm** (ER series).
- Standard cage plates are 0.35 inch (8.9 mm) thick.

For a custom cage plate: place four bores on a 30 mm square, put the aperture at the **centroid**
of those four bores, and bore them for a free-sliding fit **at your process's clearance**
(fabrication-limits.md): about 6.2 mm CNC, 6.4 mm SLA, 6.8 mm FDM. 6.1 mm is a reamed-metal
number — printed bores come out undersize, and four bores on a common square over-constrain each
other, so tighter is not better here. A cage plate that binds on the rods is worse than useless
because it transmits stress into the whole assembly.

Cage plates stack along the rods, so a custom plate's thickness directly consumes optical path
length. Budget it.

## Lens tube threads (SM series)

**SM1 is a 1.035 inch-40 thread**, which holds Ø1 inch (25.4 mm) optics. That is a **0.635 mm
pitch**.

**Do not print SM threads.** A 0.635 mm pitch is at or below the practical resolution of FDM and
marginal on desktop SLA; a printed SM1 thread will either not engage or will gall and shed
particles into the beam path. Instead:

- bore a clearance hole and use a purchased SM1 adapter or retaining ring, or
- design for a threaded metal insert, or
- clamp the optic directly with a retaining flange and screws.

If the design truly requires a printed thread, say explicitly that it needs test printing and is
likely to fail.

## Holding an optic

- **Never clamp an optic on its clear aperture.** Contact only the outer annulus of the face or the
  edge. Define `clear_aperture_mm` as a named parameter and confirm in the snapshot that nothing
  intrudes on it.
- Three-point contact is kinematically correct and does not deform the optic. A continuous
  circular seat over-constrains it and induces stress birefringence, which matters for
  polarisation work.
- Leave clearance for thermal expansion. A metal-in-polymer mount that is a press fit at 20 °C can
  crack or bind across a temperature swing.
- Retaining forces should be light and distributed. A single set screw pressing on glass is a way
  to chip glass.

## Stray light and scatter

Geometry is not the whole design here, and a STEP file cannot show any of this:

- Printed surfaces scatter strongly. Any surface that sees the beam should be baffled, angled away
  from the optical axis, or treated.
- **Black does not mean non-reflective.** Black resin and black filament are often quite specular.
  Specify a genuinely absorbing surface treatment where it matters.
- Thread and layer lines act as diffraction structures near a focus.
- For fluorescence work, printed material near the sample can autofluoresce into the detection
  path.

Flag these to the user; do not silently assume a printed enclosure is light-tight.

## Checks to run

```bash
python scripts/gen.py mount_model.py --outdir out/
python scripts/check.py facts out/mount.step
python scripts/check.py interfaces out/mount.manifest.json
python scripts/snapshot.py out/mount.step --out out/mount.png
```

Declare the grid pitch, rod spacing, and bore diameters in the model's `interfaces()` against
`optical-breadboard-metric`, `optical-breadboard-imperial`, or `cage-system-30mm`, so the check
catches a 25.0-for-25.4 substitution rather than leaving it to a reader.

There is still **no automatic bolt-pattern check** — the interface check compares dimensions, not
hole positions. Compute the pattern in the model from a named `grid_pitch_mm` constant, and confirm
in the snapshot that:

1. All mounting holes are present and pass fully through.
2. The optic aperture is centred where you intended, and unobstructed.
3. Counterbores are on the accessible face.
4. Nothing intrudes into the clear aperture or the beam path.

## Sources

- Thorlabs imperial and metric threading — <https://www.thorlabs.com/imperial-and-metric-threading>
- Thorlabs standard 30 mm cage plates — <https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_ID=2273>
- Thorlabs SM1 lens tube compatible cage plates — <https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=4114>
- Post dimensions, beam heights, and vendor-specific thread conventions in this file are common
  conventions rather than published standards. Confirm against the catalogue.

### `references/validation.md`

# Pre-fabrication validation checklist

Work through this before telling a user a part is ready to fabricate. Each item names the failure
it catches, because a checklist without consequences gets skipped.

## 1. Provenance

- [ ] The STEP was produced by `gen.py` from the current model source.
      *Catches: a stale artifact that no longer matches the code you just edited.*
- [ ] A `*.manifest.json` exists alongside it, and its `source.sha256` matches the model file.
      *Catches: silently editing an exported STEP, which makes the design unreproducible.*
- [ ] The manifest's `interfaces` block lists every dimension a bundled standard covers, and its
      values are the ones the model computed after any `--param` override. Empty is correct only
      when nothing on the part mates with a bundled standard — and then every interface dimension
      is named as unchecked in the report instead.
      *Catches: a static `INTERFACES` list frozen at import, recording pre-override numbers; and
      an interface that silently escaped checking.*
- [ ] Every parameter in the model is named with units.
      *Catches: the bare `12.7` nobody can later identify as half an inch.*

```bash
python scripts/gen.py part_model.py --outdir out/
```

## 2. Geometry is sound

- [ ] `is_valid` is true.
      *Catches: self-intersecting or non-manifold solids that slicers and CAM silently mangle.*
- [ ] `solid_count` is what you expect — usually 1.
      *Catches: a boolean that failed and left two disjoint lumps, or a feature floating free of
      the body.*
- [ ] Volume is plausible for the part's size and wall thickness.
      *Catches: a cavity modelled solid, or a subtract that did nothing.*
- [ ] Every geometric requirement in the request is declared in `checks()` and passes — clear
      regions for what must pass through or fit in, material regions for what must remain,
      bbox bounds for stated size limits.
      *Catches: a recess that swallowed its screw seat, a pocket the mating part cannot enter,
      a beam corridor with a wall in it, a feature a fillet silently ate — all invisible to
      `is_valid` and the bounding box.*

```bash
python scripts/check.py facts out/part.step
python scripts/check.py geometry out/part.step --model part_model.py
```

## 3. Interfaces

- [ ] Every interface dimension has a written source: a standard ID, a vendor drawing, or a user
      measurement. **None came from memory.**
      *Catches: the single most expensive failure mode in this skill.*
- [ ] Every interface covered by a standard is declared in the model's `interfaces()` and passes
      `check.py interfaces`.
      *Catches: an interface nobody checked because the outer bounding box could not see it.*
- [ ] Features that receive a standardised component use `intent: "envelope"`.
      *Catches: a pocket sized to nominal, which fits only the smaller half of conforming parts.*
- [ ] Any standard entry marked `verified: false` was confirmed against the primary document, or
      the user was told it is unconfirmed.
      *Catches: propagating a derived number as if it were read from the standard.*
- [ ] Metric vs imperial is confirmed where both exist, and no expression mixes them.
      *Catches: the 25.0 vs 25.4 mm grid error, which accumulates to 1.6 mm over four holes.*
- [ ] Interfaces not covered by any bundled standard — a vendor drawing, a measurement — were
      reported to the user as unchecked, with the number and its source.
      *Catches: a silent gap where the automatic check simply had nothing to say.*

```bash
python scripts/check.py interfaces out/part.manifest.json

# one dimension by hand, when it is not declared in the model
python scripts/check.py fit --standard <id> --intent envelope --clearance <mm> --value <dim>=<mm>
```

## 4. Fits and assembly

- [ ] Every mating dimension has a deliberate clearance chosen for the process.
      *Catches: nominal-to-nominal fits, which do not assemble.*
- [ ] Multi-part assemblies were checked for interference.
      *Catches: parts that overlap in CAD and therefore cannot exist together.*
- [ ] Rigid multi-hole mounting patterns have at least one slot.
      *Catches: a four-hole bolt pattern binding on accumulated tolerance.*

```bash
python scripts/check.py clearance out/a.step out/b.step --min 0.3
```

## 5. Manufacturability

- [ ] Minimum wall and feature sizes are within the chosen process (`fabrication-limits.md`).
- [ ] Print or machining orientation is stated, and load runs along layers, not across them.
- [ ] Threads use inserts or captive nuts rather than printed threads, unless coarse.
- [ ] Enclosed cavities have a drain path for resin, and support-free access where possible.
- [ ] Milled internal corners have relief for the tool radius.

## 6. Material

- [ ] Material is compatible with the **cleaning agent**, not only the sample.
      *Catches: acrylic crazing on 70% ethanol; PLA distorting in an autoclave.*
- [ ] Sterilisation method is stated and the material actually survives it.
- [ ] Anything contacting cells, tissue, or animals has a justified material, or contact is
      designed out.
      *Catches: assuming a printed resin part is cell-safe.*
- [ ] Optical requirements — autofluorescence, scatter, transmission — are addressed if the part is
      near a beam or a detector.

## 7. Visual review — mandatory

- [ ] A snapshot was rendered **and read** after the most recent generation.
- [ ] Confirmed in the image: features on the intended faces; correct mold/chip polarity; every
      port, bore, and boss present, inside the body, and passing through; nothing consumed by a
      fillet; clear apertures unobstructed.

```bash
python scripts/snapshot.py out/part.step --out out/part.png
```

**This step is never waived by the numeric checks passing.** `is_valid: true` with a correct
bounding box is fully consistent with a pocket cut on the wrong face or an inverted mold. Those
errors are obvious in the picture and invisible in the numbers.

## 8. Report

Give the user, explicitly:

1. Process and material, and why.
2. Every interface dimension with its source and tolerance.
3. Clearances chosen, and the fit class they came from.
4. What the snapshot showed — described, not merely "a snapshot was generated".
5. Every check that did not pass, and every dimension you could not verify.
6. A recommendation to print a test coupon of the critical interface before committing to the full
   part, whenever the design depends on a fit.

State the unverified items plainly. A part list with one honest "this dimension needs
confirmation" is far more useful than a confident one that is silently wrong.

### `scripts/_common.py`

```python
"""Shared helpers for the lab-hardware-cad scripts.

Import of build123d is deferred so that standard-library-only commands
(``check.py standards``) work in an environment without the CAD kernel.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

# Model files are imported from the user's working directory; leaving compiled
# bytecode there puts a __pycache__ next to the deliverables.
sys.dont_write_bytecode = True

SKILL_ROOT = Path(__file__).resolve().parent.parent
STANDARDS_PATH = SKILL_ROOT / "assets" / "standards.json"

MESH_FORMATS = {".stl"}
BREP_FORMATS = {".step", ".stp"}


class LabCadError(RuntimeError):
    """A user-facing error: printed without a traceback."""


def eprint(message: str) -> None:
    """Progress and diagnostics go to stderr so stdout stays machine-readable."""
    print(message, file=sys.stderr)


def emit(payload: Any, as_json: bool, text: str | None = None) -> None:
    """Write a result to stdout as JSON or as human-readable text."""
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    else:
        print(text if text is not None else payload)


def load_standards() -> dict:
    """Load the bundled standards database. Standard library only."""
    if not STANDARDS_PATH.exists():
        raise LabCadError(f"standards database missing at {STANDARDS_PATH}")
    with STANDARDS_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def get_standard(standard_id: str) -> dict:
    data = load_standards()
    standards = data.get("standards", {})
    if standard_id not in standards:
        known = ", ".join(sorted(standards))
        raise LabCadError(f"unknown standard {standard_id!r}. Available: {known}")
    return standards[standard_id]


def require_build123d():
    """Import build123d, or fail with an actionable message."""
    try:
        import build123d  # noqa: PLC0415
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise LabCadError(
            "build123d is not installed in this interpreter.\n"
            "  uv venv --python 3.12 .venv-labcad\n"
            '  uv pip install --python .venv-labcad/bin/python "build123d==0.11.1" "matplotlib>=3.8"'
        ) from exc
    return build123d


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _coerce(value: str) -> Any:
    """Parse a --param value into the narrowest sensible Python type."""
    lowered = value.strip().lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    for caster in (int, float):
        try:
            return caster(value)
        except ValueError:
            continue
    return value


def parse_params(pairs: list[str] | None) -> dict[str, Any]:
    """Turn ``["bore_d_mm=6.1", "wall_t_mm=3"]`` into a dict."""
    params: dict[str, Any] = {}
    for pair in pairs or []:
        if "=" not in pair:
            raise LabCadError(f"--param expects key=value, got {pair!r}")
        key, _, raw = pair.partition("=")
        params[key.strip()] = _coerce(raw)
    return params


def model_parameters(module) -> dict[str, Any]:
    """Collect a model module's public scalar parameters for the manifest."""
    return {
        name: value
        for name, value in vars(module).items()
        if not name.startswith("_") and isinstance(value, (int, float, str, bool))
    }


def import_model(model_path: Path, overrides: dict[str, Any] | None = None):
    """Import a ``*_model.py`` file and apply ``--param`` overrides.

    Returns the module without calling ``build()``, so declared interfaces can be
    read without paying for the geometry.
    """
    model_path = model_path.resolve()
    if not model_path.exists():
        raise LabCadError(f"model file not found: {model_path}")

    spec = importlib.util.spec_from_file_location(model_path.stem, model_path)
    if spec is None or spec.loader is None:
        raise LabCadError(f"cannot import {model_path}")
    module = importlib.util.module_from_spec(spec)
    # Let the model resolve sibling imports.
    sys.path.insert(0, str(model_path.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)

    for key, value in (overrides or {}).items():
        if not hasattr(module, key):
            known = ", ".join(sorted(model_parameters(module)))
            raise LabCadError(
                f"model has no parameter {key!r}. Available: {known}"
            )
        setattr(module, key, value)
    return module


def run_model(model_path: Path, overrides: dict[str, Any] | None = None):
    """Import a ``*_model.py`` file, apply overrides, and call ``build()``.

    Returns ``(part, resolved_parameters)``.
    """
    module = import_model(model_path, overrides)

    builder = getattr(module, "build", None)
    if builder is None or not callable(builder):
        raise LabCadError(
            f"{Path(model_path).name} must define a callable build() that returns a Part"
        )

    part = builder()
    if part is None:
        raise LabCadError(f"{Path(model_path).name}: build() returned None")
    return part, model_parameters(module)


def model_interfaces(module) -> list[dict]:
    """Collect the interface checks a model declares about itself.

    A model exposes either a module-level ``INTERFACES`` list or an
    ``interfaces()`` callable returning one. Each entry names the standard and
    dimension the feature must satisfy and the value the model computed:

        INTERFACES = [
            {"feature": "plate pocket length",
             "standard": "slas-microplate-footprint",
             "dimension": "footprint_length",
             "value": pocket_l_mm,
             "intent": "envelope",
             "clearance": 0.80},
        ]

    This exists because most lab-hardware interfaces are internal features -- a
    pocket, a bore, a slot -- whose size is nowhere in the part's outer bounding
    box. Declaring them lets ``check.py interfaces`` verify the number the model
    actually built instead of one retyped by hand.
    """
    declared = getattr(module, "interfaces", None)
    if callable(declared):
        declared = declared()
    elif declared is None:
        declared = getattr(module, "INTERFACES", None)
    if declared is None:
        return []
    return normalise_interfaces(declared)


def normalise_interfaces(declared: Any) -> list[dict]:
    """Validate and fill in defaults for declared interface entries."""
    if isinstance(declared, dict):
        declared = [declared]
    if not isinstance(declared, (list, tuple)):
        raise LabCadError("INTERFACES must be a list of dicts")

    entries: list[dict] = []
    for index, raw in enumerate(declared):
        if not isinstance(raw, dict):
            raise LabCadError(f"INTERFACES[{index}] must be a dict, got {type(raw).__name__}")
        missing = [key for key in ("standard", "dimension", "value") if key not in raw]
        if missing:
            raise LabCadError(
                f"INTERFACES[{index}] is missing {', '.join(missing)}. Every entry needs "
                "standard, dimension, and value."
            )
        try:
            value = float(raw["value"])
        except (TypeError, ValueError) as exc:
            raise LabCadError(
                f"INTERFACES[{index}] value {raw['value']!r} is not a number"
            ) from exc
        intent = str(raw.get("intent", "match"))
        if intent not in {"match", "envelope"}:
            raise LabCadError(
                f"INTERFACES[{index}] intent must be 'match' or 'envelope', got {intent!r}"
            )
        entries.append({
            "feature": str(raw.get("feature", raw["dimension"])),
            "standard": str(raw["standard"]),
            "dimension": str(raw["dimension"]),
            "value": value,
            "intent": intent,
            "clearance": float(raw.get("clearance", 0.0)),
        })
    return entries


def model_checks(module) -> list[dict]:
    """Collect the geometry checks a model declares about itself.

    A model exposes a ``checks()`` callable (or a ``CHECKS`` list) of go/no-go
    gauge assertions evaluated against the BUILT solid -- unlike ``interfaces()``,
    which only compares declared numbers against the standards database. Each
    entry asserts one of:

      clear     - a region must contain no material (a screw shaft, a beam
                  corridor, a gauge part dropping into a pocket)
      material  - a region must contain material (a ridge, a ledge, a boss)
      bbox_*    - a bounding-box measure must sit inside [min, max]

    See ``normalise_checks`` for the entry schema.
    """
    declared = getattr(module, "checks", None)
    if callable(declared):
        declared = declared()
    elif declared is None:
        declared = getattr(module, "CHECKS", None)
    if declared is None:
        return []
    return normalise_checks(declared)


_MEASURE_NAMES = ("bbox_x", "bbox_y", "bbox_z", "bbox_min", "bbox_mid", "bbox_max")


def _normalise_region(raw: dict, index: int) -> dict:
    """Validate one region spec: {"cylinder": dia, ...} or {"box": (dx,dy,dz), ...}."""
    if "cylinder" in raw:
        try:
            dia = float(raw["cylinder"])
        except (TypeError, ValueError) as exc:
            raise LabCadError(f"CHECKS[{index}]: cylinder diameter must be a number") from exc
        if dia <= 0:
            raise LabCadError(f"CHECKS[{index}]: cylinder diameter must be > 0")
        axis = str(raw.get("axis", "z")).lower()
        if axis not in ("x", "y", "z"):
            raise LabCadError(f"CHECKS[{index}]: axis must be 'x', 'y', or 'z', got {axis!r}")
        at = raw.get("at", [(0.0, 0.0)])
        positions = []
        for pos in at:
            try:
                a, b = (float(pos[0]), float(pos[1]))
            except (TypeError, ValueError, IndexError) as exc:
                raise LabCadError(
                    f"CHECKS[{index}]: cylinder 'at' entries are 2D positions in the "
                    "plane perpendicular to the axis (axis z: (x, y); axis x: (y, z); "
                    f"axis y: (x, z)), got {pos!r}"
                ) from exc
            positions.append([a, b])
        span = raw.get("span")
        if span is not None:
            try:
                span = [float(span[0]), float(span[1])]
            except (TypeError, ValueError, IndexError) as exc:
                raise LabCadError(f"CHECKS[{index}]: span must be (start, end) along the axis") from exc
        return {"shape": "cylinder", "dia": dia, "axis": axis, "at": positions, "span": span}
    if "box" in raw:
        size = raw["box"]
        try:
            size = [float(size[0]), float(size[1]), float(size[2])]
        except (TypeError, ValueError, IndexError) as exc:
            raise LabCadError(f"CHECKS[{index}]: box must be (dx, dy, dz)") from exc
        if min(size) <= 0:
            raise LabCadError(f"CHECKS[{index}]: box dimensions must be > 0")
        at = raw.get("at", [(0.0, 0.0, 0.0)])
        positions = []
        for pos in at:
            try:
                positions.append([float(pos[0]), float(pos[1]), float(pos[2])])
            except (TypeError, ValueError, IndexError) as exc:
                raise LabCadError(
                    f"CHECKS[{index}]: box 'at' entries are 3D centres (x, y, z), got {pos!r}"
                ) from exc
        return {"shape": "box", "size": size, "at": positions}
    raise LabCadError(
        f"CHECKS[{index}]: a region needs 'cylinder': diameter or 'box': (dx, dy, dz)"
    )


def normalise_checks(declared: Any) -> list[dict]:
    """Validate and fill in defaults for declared geometry-check entries.

    Raw entry forms::

        {"feature": "M6 screws pass", "clear": {"cylinder": 6.6, "axis": "z",
         "at": [(37.5, 37.5), (-37.5, 37.5), (37.5, -37.5), (-37.5, -37.5)]}}
        {"feature": "plate at MMC drops in", "clear": {"box": (128.01, 85.73, 6.0),
         "at": [(0.0, 0.0, 7.0)]}}
        {"feature": "ridge stands proud", "material": {"box": (40.0, 0.8, 0.28),
         "at": [(0.0, 0.0, 4.15)]}, "min_mm3": 5.0}
        {"feature": "clears the turret", "bbox_z": {"max": 15.0}}

    A cylinder with no ``span`` runs through the whole part. ``tol_mm3`` (clear,
    default 0.01) and ``min_mm3`` (material, default 0.01) tune the pass volume.
    """
    if isinstance(declared, dict):
        declared = [declared]
    if not isinstance(declared, (list, tuple)):
        raise LabCadError("CHECKS must be a list of dicts")

    entries: list[dict] = []
    for index, raw in enumerate(declared):
        if not isinstance(raw, dict):
            raise LabCadError(f"CHECKS[{index}] must be a dict, got {type(raw).__name__}")
        kinds = [k for k in ("clear", "material", *_MEASURE_NAMES) if k in raw]
        if len(kinds) != 1:
            raise LabCadError(
                f"CHECKS[{index}] needs exactly one of 'clear', 'material', or a bbox "
                f"measure ({', '.join(_MEASURE_NAMES)}), got {kinds or 'none'}"
            )
        kind = kinds[0]
        entry: dict = {"feature": str(raw.get("feature", kind))}
        if kind in ("clear", "material"):
            region = raw[kind]
            if not isinstance(region, dict):
                raise LabCadError(f"CHECKS[{index}]: {kind!r} must be a region dict")
            entry["kind"] = kind
            entry["region"] = _normalise_region(region, index)
            entry["tol_mm3"] = float(raw.get("tol_mm3", 0.01))
            entry["min_mm3"] = float(raw.get("min_mm3", 0.01))
        else:
            bounds = raw[kind]
            if not isinstance(bounds, dict) or not (
                "min" in bounds or "max" in bounds
            ):
                raise LabCadError(
                    f"CHECKS[{index}]: {kind!r} needs a dict with 'min' and/or 'max' in mm"
                )
            entry["kind"] = "measure"
            entry["measure"] = kind
            entry["min"] = None if bounds.get("min") is None else float(bounds["min"])
            entry["max"] = None if bounds.get("max") is None else float(bounds["max"])
        entries.append(entry)
    return entries


def intersection_volume(shape_a, shape_b) -> float:
    """Volume of the boolean intersection, tolerant of the kernel's return types.

    Touching or disjoint solids yield ``None``, an empty ``Compound``, or a
    ``ShapeList`` with no ``.volume`` depending on the path taken; all of those
    count as zero.
    """
    try:
        result = shape_a & shape_b
    except Exception:  # noqa: BLE001 - kernel raises assorted OCCT errors
        try:
            result = shape_a.intersect(shape_b)
        except Exception as exc:  # noqa: BLE001
            raise LabCadError(f"boolean intersection failed: {exc}") from exc
    if result is None:
        return 0.0
    volume = getattr(result, "volume", None)
    if volume is not None:
        return float(volume)
    return float(sum(float(getattr(item, "volume", 0.0) or 0.0) for item in result))


def _region_solids(build123d, region: dict, part_bbox) -> list:
    """Materialise a region spec into one solid per 'at' position."""
    solids = []
    if region["shape"] == "box":
        dx, dy, dz = region["size"]
        for x, y, z in region["at"]:
            solids.append(build123d.Pos(x, y, z) * build123d.Box(dx, dy, dz))
        return solids

    dia = region["dia"]
    axis = region["axis"]
    span = region["span"]
    if span is None:
        lo = {"x": part_bbox.min.X, "y": part_bbox.min.Y, "z": part_bbox.min.Z}[axis] - 2.0
        hi = {"x": part_bbox.max.X, "y": part_bbox.max.Y, "z": part_bbox.max.Z}[axis] + 2.0
    else:
        lo, hi = sorted(span)
    length = hi - lo
    mid = (hi + lo) / 2.0
    for a, b in region["at"]:
        cyl = build123d.Cylinder(dia / 2.0, length)
        if axis == "z":
            solid = build123d.Pos(a, b, mid) * cyl
        elif axis == "x":
            solid = build123d.Pos(mid, a, b) * build123d.Rot(0, 90, 0) * cyl
        else:  # y; 'at' is (x, z)
            solid = build123d.Pos(a, mid, b) * build123d.Rot(90, 0, 0) * cyl
        solids.append(solid)
    return solids


def evaluate_checks(part, declared: list[dict]) -> list[dict]:
    """Evaluate normalised geometry checks against a built solid."""
    build123d = require_build123d()
    facts = shape_facts(part)
    bbox = part.bounding_box()
    results = []
    for entry in declared:
        result = dict(entry)
        if entry["kind"] == "measure":
            actual = measure(facts, entry["measure"])
            ok = True
            if entry["min"] is not None and actual < entry["min"] - 1e-9:
                ok = False
            if entry["max"] is not None and actual > entry["max"] + 1e-9:
                ok = False
            result.update({"actual_mm": round(actual, 4), "pass": ok})
        else:
            volumes = [
                round(intersection_volume(part, solid), 4)
                for solid in _region_solids(build123d, entry["region"], bbox)
            ]
            total = round(sum(volumes), 4)
            if entry["kind"] == "clear":
                ok = all(v <= entry["tol_mm3"] for v in volumes)
            else:
                ok = all(v >= entry["min_mm3"] for v in volumes)
            result.update({"volumes_mm3": volumes, "total_mm3": total, "pass": ok})
        results.append(result)
    return results


def format_check_result(item: dict) -> list[str]:
    """Human-readable lines for one evaluated geometry-check result."""
    mark = "PASS" if item["pass"] else "FAIL"
    if item["kind"] == "measure":
        bounds = []
        if item.get("min") is not None:
            bounds.append(f">= {item['min']:.3f}")
        if item.get("max") is not None:
            bounds.append(f"<= {item['max']:.3f}")
        return [f"  [{mark}] {item['feature']:<38} {item['measure']} "
                f"{item['actual_mm']:.3f} mm  expected {' and '.join(bounds)}"]
    region = item["region"]
    if region["shape"] == "cylinder":
        where = f"cyl d{region['dia']:g} axis {region['axis']} x{len(region['at'])}"
    else:
        dx, dy, dz = region["size"]
        where = f"box {dx:g}x{dy:g}x{dz:g} x{len(region['at'])}"
    if item["kind"] == "clear":
        detail = f"intruding {item['total_mm3']:.3f} mm^3 (tol {item['tol_mm3']:g}/position)"
    else:
        detail = (f"material {item['total_mm3']:.3f} mm^3 "
                  f"(min {item['min_mm3']:g}/position)")
    lines = [f"  [{mark}] {item['feature']:<38} {item['kind']} {where}  {detail}"]
    if not item["pass"]:
        lines.append(f"         per position (mm^3): {item['volumes_mm3']}")
    return lines


def cylinder_census(part) -> list[dict]:
    """Every cylindrical face in the part: radius, axis, extent, sweep.

    This is the instrument for reconciling what a render appears to show with
    what the solid actually contains: a bore is a ~360 degree sweep, an edge
    fillet ~90, and a counterbore is two coaxial full sweeps stacked along the
    axis with different radii.
    """
    build123d = require_build123d()
    from OCP.BRepAdaptor import BRepAdaptor_Surface  # noqa: PLC0415
    import math  # noqa: PLC0415

    rows = []
    for face in part.faces():
        if face.geom_type != build123d.GeomType.CYLINDER:
            continue
        cyl = BRepAdaptor_Surface(face.wrapped).Cylinder()
        ax = cyl.Axis()
        loc, direction = ax.Location(), ax.Direction()
        d = (direction.X(), direction.Y(), direction.Z())
        point = (loc.X(), loc.Y(), loc.Z())

        axis_name = None
        for name, vec in (("x", (1, 0, 0)), ("y", (0, 1, 0)), ("z", (0, 0, 1))):
            if abs(abs(d[0] * vec[0] + d[1] * vec[1] + d[2] * vec[2]) - 1.0) < 1e-6:
                axis_name = name
        # Canonicalise to the +axis direction so spans read in real coordinates
        # instead of sign-flipping for bores cut top-down.
        if axis_name is not None:
            d = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}[axis_name]

        bb = face.bounding_box()
        corners = [
            (x, y, z)
            for x in (bb.min.X, bb.max.X)
            for y in (bb.min.Y, bb.max.Y)
            for z in (bb.min.Z, bb.max.Z)
        ]
        proj = [x * d[0] + y * d[1] + z * d[2] for x, y, z in corners]
        extent = max(proj) - min(proj)
        radius = float(cyl.Radius())
        sweep = (
            math.degrees(float(face.area) / (radius * extent)) if radius * extent > 1e-12 else 0.0
        )
        # In-plane position, ordered like probe positions: axis z -> (x, y),
        # axis x -> (y, z), axis y -> (x, z). The axis point's own component
        # along the axis is arbitrary, so it is not reported for aligned axes.
        if axis_name == "z":
            at = [round(point[0], 4), round(point[1], 4)]
        elif axis_name == "x":
            at = [round(point[1], 4), round(point[2], 4)]
        elif axis_name == "y":
            at = [round(point[0], 4), round(point[2], 4)]
        else:
            at = [round(c, 4) for c in point]
        rows.append({
            "radius_mm": round(radius, 4),
            "diameter_mm": round(2 * radius, 4),
            "axis": axis_name or [round(c, 4) for c in d],
            "at_mm": at,
            "extent_mm": round(extent, 4),
            "span_min_mm": round(min(proj), 4),
            "span_max_mm": round(max(proj), 4),
            "sweep_deg": round(sweep, 1),
            "full": sweep >= 355.0,
        })
    rows.sort(key=lambda r: (str(r["axis"]), r["at_mm"], r["radius_mm"]))
    return rows


def load_shape(path: Path):
    """Load a STEP or STL file, or build a model, into a build123d shape."""
    path = Path(path)
    if not path.exists():
        raise LabCadError(f"file not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".py":
        part, _ = run_model(path)
        return part

    build123d = require_build123d()
    if suffix in BREP_FORMATS:
        return build123d.import_step(str(path))
    if suffix in MESH_FORMATS:
        eprint(
            f"warning: {path.name} is a mesh. Volume and validity are approximate, "
            "and STEP is the authoritative format. Prefer inspecting the STEP."
        )
        return build123d.import_stl(str(path))
    raise LabCadError(
        f"unsupported input {suffix!r}. Expected .step, .stp, .stl, or a *_model.py file."
    )


def _is_valid(shape) -> bool:
    """``Shape.is_valid`` is a property in build123d 0.11.x; older builds expose a method."""
    value = shape.is_valid
    return bool(value() if callable(value) else value)


def shape_facts(shape) -> dict:
    """Deterministic geometric facts about a shape, in millimetres."""
    build123d = require_build123d()
    bbox = shape.bounding_box()

    try:
        centre = shape.center(build123d.CenterOf.MASS)
        centre_of = "mass"
    except (ValueError, NotImplementedError):
        centre = bbox.center()
        centre_of = "bounding_box"

    try:
        solids = len(shape.solids())
    except (AttributeError, TypeError):
        solids = None

    return {
        "is_valid": _is_valid(shape),
        "bounding_box_mm": {
            "x": round(bbox.size.X, 4),
            "y": round(bbox.size.Y, 4),
            "z": round(bbox.size.Z, 4),
            "min": [round(bbox.min.X, 4), round(bbox.min.Y, 4), round(bbox.min.Z, 4)],
            "max": [round(bbox.max.X, 4), round(bbox.max.Y, 4), round(bbox.max.Z, 4)],
        },
        "volume_mm3": round(float(shape.volume), 4),
        "area_mm2": round(float(shape.area), 4),
        "center_mm": [round(centre.X, 4), round(centre.Y, 4), round(centre.Z, 4)],
        "center_of": centre_of,
        "solid_count": solids,
    }


def measure(facts: dict, name: str, swap_xy: bool = False) -> float:
    """Resolve a fit-check measure name against a facts dict."""
    box = facts["bounding_box_mm"]
    x, y = (box["y"], box["x"]) if swap_xy else (box["x"], box["y"])
    extents = sorted((x, y, box["z"]))
    table = {
        "bbox_x": x,
        "bbox_y": y,
        "bbox_z": box["z"],
        "bbox_min": extents[0],
        "bbox_mid": extents[1],
        "bbox_max": extents[2],
    }
    if name not in table:
        raise LabCadError(
            f"unknown measure {name!r}. Expected one of: {', '.join(sorted(table))}"
        )
    return table[name]


def main_guard(func) -> None:
    """Run a CLI entry point, converting LabCadError into a clean exit."""
    try:
        sys.exit(func())
    except LabCadError as exc:
        eprint(f"error: {exc}")
        sys.exit(2)
    except KeyboardInterrupt:  # pragma: no cover
        eprint("interrupted")
        sys.exit(130)
```

### `scripts/check.py`

```python
#!/usr/bin/env python3
"""Deterministic checks on lab-hardware geometry.

    python scripts/check.py standards --list
    python scripts/check.py standards --show slas-microplate-footprint
    python scripts/check.py facts out/carrier.step
    python scripts/check.py interfaces out/carrier.manifest.json
    python scripts/check.py geometry out/carrier.step --model carrier_model.py
    python scripts/check.py probe out/carrier.step --cyl 6.6 --at 37.5,37.5 --at -37.5,37.5
    python scripts/check.py bores out/carrier.step
    python scripts/check.py fit --standard slas-microplate-footprint \
        --intent envelope --clearance 0.8 --value footprint_length=128.81
    python scripts/check.py clearance out/carrier.step out/lid.step --min 0.3

``standards`` and ``interfaces`` on a manifest run on the standard library alone. The
other subcommands need build123d. Checking subcommands exit non-zero on failure so they
can gate a build.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import (  # noqa: E402
    LabCadError,
    cylinder_census,
    emit,
    eprint,
    evaluate_checks,
    format_check_result,
    get_standard,
    import_model,
    intersection_volume,
    load_shape,
    load_standards,
    main_guard,
    measure,
    model_checks,
    model_interfaces,
    normalise_checks,
    normalise_interfaces,
    shape_facts,
)


def cmd_standards(args) -> int:
    data = load_standards()
    standards = data["standards"]

    if args.show:
        entry = get_standard(args.show)
        lines = [
            f"{args.show}: {entry['title']}",
            f"  authority: {entry['authority']}",
            f"  document:  {entry['document']}",
            f"  url:       {entry.get('url', '-')}",
            f"  verified:  {entry.get('verified')}",
            "  dimensions (mm):",
        ]
        for name, dim in entry["dimensions"].items():
            band = f"+{dim.get('tol_plus', 0)}/-{dim.get('tol_minus', 0)}"
            lines.append(f"    {name}: {dim['nominal']} {band}")
            if dim.get("note"):
                lines.append(f"      note: {dim['note']}")
        if entry.get("design_note"):
            lines.append(f"  design note: {entry['design_note']}")
        if not entry.get("verified", False):
            lines.append("  WARNING: this entry is not verified against the primary document.")
        emit(entry, args.as_json, "\n".join(lines))
        return 0

    listing = [
        {
            "id": key,
            "title": value["title"],
            "document": value["document"],
            "verified": value.get("verified", False),
        }
        for key, value in sorted(standards.items())
    ]
    text = "\n".join(
        f"{item['id']:<32} {'ok ' if item['verified'] else 'UNVERIFIED'}  {item['title']}"
        for item in listing
    )
    emit(listing, args.as_json, text)
    return 0


def cmd_facts(args) -> int:
    shape = load_shape(args.target)
    facts = shape_facts(shape)
    box = facts["bounding_box_mm"]
    text = "\n".join([
        f"target:      {args.target}",
        f"is_valid:    {facts['is_valid']}",
        f"bbox (mm):   {box['x']:.4f} x {box['y']:.4f} x {box['z']:.4f}",
        f"bbox min:    {box['min']}",
        f"bbox max:    {box['max']}",
        f"volume:      {facts['volume_mm3']:.4f} mm^3",
        f"area:        {facts['area_mm2']:.4f} mm^2",
        f"centre ({facts['center_of']}): {facts['center_mm']}",
        f"solids:      {facts['solid_count']}",
    ])
    emit(facts, args.as_json, text)
    return 0 if facts["is_valid"] else 1


def _evaluate(
    entry, dimension: str, actual: float, offset: float, measure_label: str, intent: str
) -> dict:
    """Compare one declared dimension against a standard.

    Two intents, because they are different questions:

    ``match``    - this part must itself conform to the standard. Symmetric band
                   around nominal, widened (never shifted) by ``offset``.
    ``envelope`` - this feature must accept ANY conforming part (a pocket, bore,
                   or slot). One-sided minimum at maximum material condition plus
                   the clearance. Designing such a feature to nominal fits only
                   the smallest half of conforming parts.

    ``offset`` must be non-negative: a negative clearance would let a declaration
    move its own acceptance band and certify a nonconforming value.
    """
    if dimension not in entry["dimensions"]:
        known = ", ".join(sorted(entry["dimensions"]))
        raise LabCadError(f"unknown dimension {dimension!r}. Available: {known}")
    if offset < 0:
        raise LabCadError(
            f"{dimension}: clearance must be >= 0, got {offset}. A clearance widens the "
            "acceptance band; it cannot shift it. If the feature is deliberately "
            "undersized, say so in the report instead of encoding it as a negative "
            "clearance."
        )
    dim = entry["dimensions"][dimension]
    nominal = float(dim["nominal"])
    tol_plus = float(dim.get("tol_plus", 0.0))
    tol_minus = float(dim.get("tol_minus", 0.0))

    if intent == "envelope":
        low = nominal + tol_plus + offset
        high = None
        passed = actual >= low - 1e-9
        headroom = round(actual - low, 4)
    else:
        low = nominal - tol_minus - offset
        high = nominal + tol_plus + offset
        passed = low - 1e-9 <= actual <= high + 1e-9
        headroom = None

    return {
        "dimension": dimension,
        "measure": measure_label,
        "intent": intent,
        "nominal_mm": nominal,
        "max_material_mm": round(nominal + tol_plus, 4),
        "expected_range_mm": [round(low, 4), None if high is None else round(high, 4)],
        "actual_mm": round(actual, 4),
        "headroom_mm": headroom,
        "pass": passed,
    }


def cmd_fit(args) -> int:
    entry = get_standard(args.standard)
    offset = float(args.clearance)
    results = []

    if args.value:
        # Value mode: check dimensions the model computed. Needed whenever the
        # interface is an internal feature (a pocket, a bore, a slot), where the
        # part's outer bounding box is not the dimension that has to match.
        if args.target is not None:
            eprint(
                f"warning: --value was given, so {args.target} is not measured. Drop the "
                "target, or drop --value to check the outer bounding box."
            )
        for pair in args.value:
            if "=" not in pair:
                raise LabCadError(f"--value expects dimension=number, got {pair!r}")
            name, _, raw = pair.partition("=")
            try:
                actual = float(raw)
            except ValueError as exc:
                raise LabCadError(f"--value {pair!r}: {raw!r} is not a number") from exc
            results.append(
                _evaluate(entry, name.strip(), actual, offset, "declared", args.intent)
            )
    else:
        checks = entry.get("fit_checks", [])
        if not checks:
            raise LabCadError(
                f"{args.standard} defines no automatic bounding-box checks (it is a "
                "reference dimension set). Use --value to check a computed dimension, "
                "or `standards --show` and check the interface by hand."
            )
        if args.target is None:
            raise LabCadError("fit needs either a target file or one or more --value arguments")
        facts = shape_facts(load_shape(args.target))
        for check in checks:
            actual = measure(facts, check["measure"], swap_xy=args.swap_xy)
            results.append(
                _evaluate(
                    entry, check["dimension"], actual, offset, check["measure"], args.intent
                )
            )

    passed = all(item["pass"] for item in results)
    payload = {
        "standard": args.standard,
        "title": entry["title"],
        "document": entry["document"],
        "verified_source": entry.get("verified", False),
        "clearance_applied_mm": offset,
        "mode": "declared" if args.value else "bounding_box",
        "swap_xy": args.swap_xy,
        "checks": results,
        "pass": passed,
    }

    lines = [f"{args.standard} ({entry['document']})  intent={args.intent}"]
    for item in results:
        mark = "PASS" if item["pass"] else "FAIL"
        low, high = item["expected_range_mm"]
        if high is None:
            expected = f">= {low:.3f}  headroom {item['headroom_mm']:+.3f}"
        else:
            expected = f"{low:.3f}..{high:.3f}"
        lines.append(
            f"  [{mark}] {item['dimension']:<22} {item['measure']:<9} "
            f"actual {item['actual_mm']:>9.3f}  expected {expected}"
        )
    if not entry.get("verified", False):
        lines.append("  WARNING: standard entry is not verified against the primary document.")
    if not passed and not args.value:
        if not args.swap_xy:
            lines.append("  hint: if the part is modelled rotated 90 degrees, rerun with --swap-xy")
        lines.append(
            "  hint: bounding-box mode measures the OUTER envelope. If the interface is a "
            "pocket, bore, or slot, pass the computed dimension with --value instead."
        )
    lines.append("Reminder: a passing bounding box is not a passing part. Run snapshot.py.")
    emit(payload, args.as_json, "\n".join(lines))
    return 0 if passed else 1


def _declared_interfaces(target: Path) -> tuple[list[dict], str]:
    """Read a model's declared interfaces from a manifest or from the model itself."""
    suffix = target.suffix.lower()
    if suffix == ".json":
        if not target.exists():
            raise LabCadError(f"file not found: {target}")
        try:
            payload = json.loads(target.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise LabCadError(f"{target} is not valid JSON: {exc}") from exc
        return normalise_interfaces(payload.get("interfaces") or []), "manifest"
    if suffix == ".py":
        return model_interfaces(import_model(target)), "model"
    raise LabCadError(
        f"unsupported input {suffix!r}. Pass a *.manifest.json written by gen.py, or a "
        "*_model.py."
    )


def cmd_interfaces(args) -> int:
    """Check every interface a model declares about itself.

    This verifies the DECLARED numbers against the standards database: it catches
    a transcribed dimension, the wrong standard, and nominal-instead-of-MMC
    sizing. It does not measure the built geometry -- ``facts`` and the snapshot
    do that -- so a passing result here is necessary, not sufficient.

    A model whose part mates with nothing in the bundled database correctly
    declares no interfaces; that is a passing state, not an error. Every such
    unchecked dimension must then be named in the report.
    """
    declared, source = _declared_interfaces(args.target)

    if not declared:
        payload = {"target": str(args.target), "source": source, "checks": [], "pass": True}
        emit(payload, args.as_json, (
            f"{args.target.name}: 0 declared interfaces - nothing in this part mates "
            "with a bundled standard.\n"
            "That is fine IF it is true. Do not invent a declaration to fill the gap; "
            "instead name every interface dimension and its source (user spec, vendor "
            "drawing, measurement) as UNCHECKED in the report."
        ))
        return 0

    results = []
    for entry in declared:
        standard = get_standard(entry["standard"])
        result = _evaluate(
            standard,
            entry["dimension"],
            entry["value"],
            entry["clearance"],
            "declared",
            entry["intent"],
        )
        result["feature"] = entry["feature"]
        result["standard"] = entry["standard"]
        result["document"] = standard["document"]
        result["verified_source"] = standard.get("verified", False)
        result["clearance_applied_mm"] = entry["clearance"]
        results.append(result)

    passed = all(item["pass"] for item in results)
    payload = {
        "target": str(args.target),
        "source": source,
        "checks": results,
        "pass": passed,
    }

    lines = [f"{args.target.name}: {len(results)} declared interface(s) from the {source}"]
    for item in results:
        mark = "PASS" if item["pass"] else "FAIL"
        low, high = item["expected_range_mm"]
        if high is None:
            expected = f">= {low:.3f}  headroom {item['headroom_mm']:+.3f}"
        else:
            expected = f"{low:.3f}..{high:.3f}"
        lines.append(
            f"  [{mark}] {item['feature']:<26} {item['actual_mm']:>9.3f} mm  "
            f"expected {expected}"
        )
        lines.append(
            f"         {item['standard']} {item['dimension']} "
            f"({item['intent']}, clearance {item['clearance_applied_mm']} mm)"
        )
        if not item["verified_source"]:
            lines.append("         WARNING: standard entry is not verified against the document.")
    lines.append(
        "Note: this checks the values the model DECLARED, not the built geometry. "
        "A declaration computed from the same constants it is checked against will "
        "pass with zero headroom by construction. Run check.py facts and snapshot.py "
        "on the exported STEP to verify the geometry itself."
    )
    emit(payload, args.as_json, "\n".join(lines))
    return 0 if passed else 1


def cmd_geometry(args) -> int:
    """Evaluate a model's declared geometry checks against the built solid.

    Unlike ``interfaces``, which compares declared numbers against the standards
    database, this measures the geometry itself: material really is absent from
    every declared clear region, present in every material region, and the
    bounding box sits inside its declared bounds.
    """
    target = args.target
    if target.suffix.lower() == ".py":
        module = import_model(target)
        declared = model_checks(module)
        part = load_shape(target)
        geometry_source = target.name
    else:
        if args.model is None:
            raise LabCadError(
                "checking a STEP needs the model that declares the checks: "
                "check.py geometry out/part.step --model part_model.py"
            )
        declared = model_checks(import_model(args.model))
        part = load_shape(target)
        geometry_source = target.name

    if not declared:
        emit({"target": str(target), "checks": [], "pass": True}, args.as_json, (
            f"{target.name}: no declared geometry checks.\n"
            "Declare a checks() function for every geometric requirement in the "
            "request - clearance holes, keep-out corridors, a gauge part that must "
            "drop into a pocket, a feature that must stand proud, a size limit. "
            "See references/build123d-patterns.md."
        ))
        return 0

    results = evaluate_checks(part, declared)
    passed = all(item["pass"] for item in results)
    payload = {"target": str(target), "checks": results, "pass": passed}

    lines = [f"{geometry_source}: {len(results)} geometry check(s), measured from the solid"]
    for item in results:
        lines.extend(format_check_result(item))
    if not passed:
        lines.append("Fix the model source and regenerate; never patch the STEP.")
    emit(payload, args.as_json, "\n".join(lines))
    return 0 if passed else 1


def cmd_probe(args) -> int:
    """One ad-hoc region probe against a solid, without editing the model."""
    if (args.cyl is None) == (args.box is None):
        raise LabCadError("pass exactly one of --cyl DIA or --box DX,DY,DZ")

    region: dict = {}
    if args.cyl is not None:
        region["cylinder"] = args.cyl
        region["axis"] = args.axis
        if args.span:
            region["span"] = _parse_floats(args.span, 2, "--span")
        region["at"] = [_parse_floats(a, 2, "--at") for a in (args.at or ["0,0"])]
    else:
        region["box"] = _parse_floats(args.box, 3, "--box")
        region["at"] = [_parse_floats(a, 3, "--at") for a in (args.at or ["0,0,0"])]

    entry = {"feature": args.feature or f"probe ({args.expect})", args.expect: region}
    if args.expect == "material" and args.min_mm3 is not None:
        entry["min_mm3"] = args.min_mm3
    if args.expect == "clear" and args.tol_mm3 is not None:
        entry["tol_mm3"] = args.tol_mm3

    part = load_shape(args.target)
    results = evaluate_checks(part, normalise_checks([entry]))
    payload = {"target": str(args.target), "checks": results, "pass": results[0]["pass"]}
    emit(payload, args.as_json, "\n".join(
        [f"{args.target.name}: probe"] + format_check_result(results[0])
    ))
    return 0 if results[0]["pass"] else 1


def _parse_floats(raw: str, count: int, flag: str) -> list[float]:
    parts = [p for p in raw.replace(" ", "").split(",") if p]
    if len(parts) != count:
        raise LabCadError(f"{flag} expects {count} comma-separated numbers, got {raw!r}")
    try:
        return [float(p) for p in parts]
    except ValueError as exc:
        raise LabCadError(f"{flag}: {raw!r} is not numeric") from exc


def cmd_bores(args) -> int:
    """List every cylindrical face: the census for reconciling render vs solid."""
    part = load_shape(args.target)
    rows = cylinder_census(part)
    payload = {"target": str(args.target), "cylindrical_faces": rows}

    if not rows:
        emit(payload, args.as_json, f"{args.target.name}: no cylindrical faces.")
        return 0
    lines = [
        f"{args.target.name}: {len(rows)} cylindrical face(s). Full ~360 degree sweeps "
        "are bores/bosses; ~90 degree sweeps are edge fillets.",
    ]
    for r in rows:
        axis = r["axis"] if isinstance(r["axis"], str) else str(r["axis"])
        at = ", ".join(f"{v:g}" for v in r["at_mm"])
        kind = "full" if r["full"] else f"{r['sweep_deg']:g} deg"
        lines.append(
            f"  d {r['diameter_mm']:>8.3f}  axis {axis:<12} at ({at})"
            f"  span {r['span_min_mm']:g}..{r['span_max_mm']:g}  {kind}"
        )
    lines.append(
        "Reconcile this against the model's intent before trusting a render: a missing "
        "diameter or an unexpected span here is a real feature error, whatever the "
        "picture appears to show."
    )
    emit(payload, args.as_json, "\n".join(lines))
    return 0


def _min_distance(shape_a, shape_b) -> float | None:
    for method in ("distance_to", "distance"):
        func = getattr(shape_a, method, None)
        if callable(func):
            try:
                return float(func(shape_b))
            except (TypeError, ValueError):
                continue
    func = getattr(shape_a, "distance_to_with_closest_points", None)
    if callable(func):
        try:
            return float(func(shape_b)[0])
        except (TypeError, ValueError, IndexError):
            return None
    return None


def cmd_clearance(args) -> int:
    shape_a = load_shape(args.a)
    shape_b = load_shape(args.b)

    overlap_volume = 0.0
    try:
        overlap_volume = intersection_volume(shape_a, shape_b)
    except LabCadError as exc:
        eprint(f"warning: {exc}; relying on distance only")

    interferes = overlap_volume > 1e-6
    gap = None if interferes else _min_distance(shape_a, shape_b)

    payload = {
        "a": str(args.a),
        "b": str(args.b),
        "interference": interferes,
        "overlap_volume_mm3": round(overlap_volume, 6),
        "min_distance_mm": None if gap is None else round(gap, 4),
        "required_min_mm": args.min,
    }

    if interferes:
        payload["pass"] = False
        text = (
            f"INTERFERENCE: the two solids overlap by {overlap_volume:.4f} mm^3.\n"
            "Parts cannot be assembled as modelled."
        )
    elif gap is None:
        payload["pass"] = None
        text = (
            "Could not compute a minimum distance with this build123d build, and the "
            "solids do not overlap. Verify the fit visually with snapshot.py."
        )
    else:
        payload["pass"] = gap >= args.min
        mark = "PASS" if payload["pass"] else "FAIL"
        text = (
            f"[{mark}] minimum gap {gap:.4f} mm (required >= {args.min} mm)\n"
            f"       overlap volume {overlap_volume:.6f} mm^3"
        )

    emit(payload, args.as_json, text)
    if payload["pass"] is None:
        return 0
    return 0 if payload["pass"] else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="emit machine-readable JSON on stdout")
    sub = parser.add_subparsers(dest="command", required=True)

    p_std = sub.add_parser("standards", help="browse the bundled standards database")
    group = p_std.add_mutually_exclusive_group()
    group.add_argument("--list", action="store_true", help="list every standard (default)")
    group.add_argument("--show", metavar="ID", help="show one standard in full")
    p_std.set_defaults(func=cmd_standards)

    p_facts = sub.add_parser("facts", help="validity, bounding box, volume, area, centre")
    p_facts.add_argument("target", type=Path, help="STEP, STL, or *_model.py")
    p_facts.set_defaults(func=cmd_facts)

    p_int = sub.add_parser(
        "interfaces",
        help="check every interface a model declares about itself (the build gate)",
        description="Check each entry of a model's INTERFACES list against its standard. "
                    "Use this rather than `fit` whenever the interface is an internal "
                    "feature -- a pocket, bore, or slot -- which is most of the time. "
                    "Reading a manifest needs no geometry kernel.",
    )
    p_int.add_argument("target", type=Path,
                       help="a *.manifest.json written by gen.py, or a *_model.py")
    p_int.set_defaults(func=cmd_interfaces)

    p_geo = sub.add_parser(
        "geometry",
        help="evaluate the model's declared geometry checks against the built solid",
        description="Run every checks() entry -- clear regions, material regions, bbox "
                    "bounds -- as boolean gauges against the actual geometry. This is "
                    "the measured counterpart to `interfaces`, which only compares "
                    "declared numbers.",
    )
    p_geo.add_argument("target", type=Path, help="a *_model.py, or a STEP with --model")
    p_geo.add_argument("--model", type=Path, default=None,
                       help="the *_model.py declaring checks(), when target is a STEP")
    p_geo.set_defaults(func=cmd_geometry)

    p_probe = sub.add_parser(
        "probe",
        help="ad-hoc region gauge: is this cylinder/box clear of (or filled with) material?",
    )
    p_probe.add_argument("target", type=Path, help="STEP, STL, or *_model.py")
    p_probe.add_argument("--cyl", type=float, metavar="DIA",
                         help="cylindrical gauge of this diameter in mm")
    p_probe.add_argument("--box", metavar="DX,DY,DZ", help="box gauge, size in mm")
    p_probe.add_argument("--axis", choices=("x", "y", "z"), default="z",
                         help="cylinder axis (default: z); runs through the part unless "
                              "--span is given")
    p_probe.add_argument("--at", action="append", metavar="A,B[,C]",
                         help="position, repeatable. Cylinder: 2D in the plane "
                              "perpendicular to the axis (axis z: x,y; axis x: y,z; "
                              "axis y: x,z). Box: 3D centre x,y,z.")
    p_probe.add_argument("--span", metavar="A,B",
                         help="cylinder extent along its axis (default: through the part)")
    p_probe.add_argument("--expect", choices=("clear", "material"), default="clear",
                         help="'clear': no material in the region (default); "
                              "'material': the region must contain material")
    p_probe.add_argument("--tol-mm3", type=float, default=None,
                         help="max intruding volume per position for 'clear' (default 0.01)")
    p_probe.add_argument("--min-mm3", type=float, default=None,
                         help="min material volume per position for 'material' (default 0.01)")
    p_probe.add_argument("--feature", help="label for the output")
    p_probe.set_defaults(func=cmd_probe)

    p_bores = sub.add_parser(
        "bores",
        help="census of every cylindrical face: diameter, axis, span, sweep",
        description="The reconciliation instrument for step 6: compare what the render "
                    "appears to show against what the solid actually contains.",
    )
    p_bores.add_argument("target", type=Path, help="STEP, STL, or *_model.py")
    p_bores.set_defaults(func=cmd_bores)

    p_fit = sub.add_parser("fit", help="check one dimension against a standard by hand")
    p_fit.add_argument("target", type=Path, nargs="?",
                       help="STEP, STL, or *_model.py; omit when using --value")
    p_fit.add_argument("--standard", required=True, help="standard ID from `standards --list`")
    p_fit.add_argument("--value", action="append", metavar="DIMENSION=MM",
                       help="check a dimension the model computed, e.g. "
                            "footprint_length=128.81. Use this when the interface is an "
                            "internal feature. Repeatable; needs no geometry kernel.")
    p_fit.add_argument("--intent", choices=("match", "envelope"), default="match",
                       help="'match': this part must itself conform to the standard "
                            "(symmetric band). 'envelope': this feature must accept any "
                            "conforming part, so it is checked one-sided against maximum "
                            "material condition. Use 'envelope' for pockets, bores, and "
                            "slots. (default: match)")
    p_fit.add_argument("--clearance", type=float, default=0.0,
                       help="total intended clearance in mm, e.g. 0.8 for a pocket with "
                            "0.4 mm clearance per side (default: 0)")
    p_fit.add_argument("--swap-xy", action="store_true",
                       help="the part is modelled with x and y exchanged")
    p_fit.set_defaults(func=cmd_fit)

    p_clr = sub.add_parser("clearance", help="minimum distance between two solids")
    p_clr.add_argument("a", type=Path)
    p_clr.add_argument("b", type=Path)
    p_clr.add_argument("--min", type=float, default=0.2,
                       help="required minimum gap in mm (default: 0.2)")
    p_clr.set_defaults(func=cmd_clearance)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    main_guard(main)
```

### `scripts/gen.py`

```python
#!/usr/bin/env python3
"""Generate fabrication artifacts from a parametric build123d model.

Runs a model file's ``build()``, exports STEP (authoritative) and STL (preview and
printing), and writes a manifest recording the source hash, resolved parameters,
library versions, and measured geometry.

    python scripts/gen.py carrier_model.py --outdir out/
    python scripts/gen.py carrier_model.py --outdir out/ --param wall_t_mm=4.0
    python scripts/gen.py plate_model.py --outdir out/ --dxf     # 2D laser profile
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import (  # noqa: E402
    LabCadError,
    emit,
    eprint,
    evaluate_checks,
    format_check_result,
    import_model,
    main_guard,
    model_checks,
    model_interfaces,
    model_parameters,
    parse_params,
    require_build123d,
    sha256_of,
    shape_facts,
)


def _build123d_version() -> str:
    from importlib.metadata import PackageNotFoundError, version  # noqa: PLC0415

    try:
        return version("build123d")
    except PackageNotFoundError:  # pragma: no cover
        return "unknown"


def _export_dxf(part, path: Path, build123d, height: float | None) -> float:
    """Slice the part on a horizontal plane and write the profile as DXF.

    ``section()`` is a module-level operation in build123d 0.11.1, not a method on
    the shape. The default cut height is the middle of the part rather than z = 0,
    because a part modelled sitting on the build plate has nothing but a degenerate
    face at z = 0. Returns the height actually used, for the manifest.
    """
    if height is None:
        bbox = part.bounding_box()
        height = (float(bbox.min.Z) + float(bbox.max.Z)) / 2.0

    plane = build123d.Plane.XY.offset(height)
    try:
        profile = build123d.section(part, plane, mode=build123d.Mode.PRIVATE)
    except Exception as exc:  # noqa: BLE001 - the kernel raises assorted OCCT errors
        raise LabCadError(f"DXF section at z={height:.3f} mm failed: {exc}") from exc
    if not profile.faces():
        raise LabCadError(
            f"DXF section at z={height:.3f} mm is empty. Pass --dxf-z with a height "
            "that actually cuts material."
        )

    # Translate the section back to z = 0: DXF is a 2D format, and handing it a
    # profile at the section height makes the exporter warn about a non-planar
    # shape even though the written entities would be flat anyway.
    if abs(height) > 1e-9:
        profile = profile.moved(build123d.Location((0.0, 0.0, -height)))

    from build123d.exporters import ColorIndex  # noqa: PLC0415 - not in the top-level namespace

    exporter = build123d.ExportDXF(unit=build123d.Unit.MM)
    # Cut geometry goes on a named layer: laser shops key power and speed to
    # layer or colour, and geometry on layer 0 forces them to guess.
    exporter.add_layer("CUT", color=ColorIndex.RED)
    exporter.add_shape(profile, layer="CUT")
    exporter.write(str(path))
    return height


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("model", type=Path, help="path to a *_model.py exposing build() -> Part")
    parser.add_argument("--outdir", type=Path, default=Path("out"), help="output directory (default: out)")
    parser.add_argument("--name", help="artifact basename (default: model filename without _model)")
    parser.add_argument("--param", action="append", metavar="KEY=VALUE",
                        help="override a model parameter; repeatable")
    parser.add_argument("--tolerance", type=float, default=1e-3,
                        help="STL linear deflection in mm (default: 0.001)")
    parser.add_argument("--angular-tolerance", type=float, default=0.1,
                        help="STL angular deflection (default: 0.1)")
    parser.add_argument("--dxf", action="store_true",
                        help="also export a 2D DXF profile, sliced on a horizontal plane")
    parser.add_argument("--dxf-z", type=float, default=None, metavar="MM",
                        help="height of the DXF section plane (default: the middle of the part)")
    parser.add_argument("--no-stl", action="store_true", help="skip the STL export")
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit the manifest as JSON on stdout")
    args = parser.parse_args()

    if args.dxf_z is not None and not args.dxf:
        raise LabCadError("--dxf-z sets the section height for --dxf; pass --dxf as well")

    build123d = require_build123d()
    overrides = parse_params(args.param)

    eprint(f"building {args.model.name} ...")
    module = import_model(args.model, overrides)
    builder = getattr(module, "build", None)
    if builder is None or not callable(builder):
        raise LabCadError(f"{args.model.name} must define a callable build() that returns a Part")
    try:
        part = builder()
    except LabCadError:
        raise
    except Exception as exc:  # noqa: BLE001 - model code raises arbitrary errors
        import traceback  # noqa: PLC0415

        frames = traceback.extract_tb(exc.__traceback__)
        model_frames = [f for f in frames if f.filename == str(args.model.resolve())]
        where = (
            f" at {args.model.name}:{model_frames[-1].lineno} ({model_frames[-1].name})"
            if model_frames else ""
        )
        raise LabCadError(
            f"build() failed{where}: {type(exc).__name__}: {exc}"
        ) from exc
    if part is None:
        raise LabCadError(f"{args.model.name}: build() returned None")
    params = model_parameters(module)
    # Read the declared interfaces after build(), so a model that computes them in
    # build() and stores them on the module still reports the resolved numbers.
    interfaces = model_interfaces(module)
    if interfaces and overrides and not callable(getattr(module, "interfaces", None)):
        eprint(
            "WARNING: this model declares a static INTERFACES list, which was evaluated "
            "at import - before --param was applied. Any interface derived from an "
            "overridden parameter is now recorded WRONG. Convert INTERFACES into an "
            "interfaces() function that computes from the current parameters."
        )

    stem = args.name or args.model.stem.removesuffix("_model")
    outdir = args.outdir
    outdir.mkdir(parents=True, exist_ok=True)

    step_path = outdir / f"{stem}.step"
    build123d.export_step(part, str(step_path), unit=build123d.Unit.MM)
    eprint(f"wrote {step_path}")
    artifacts = {"step": str(step_path)}

    if not args.no_stl:
        stl_path = outdir / f"{stem}.stl"
        build123d.export_stl(
            part, str(stl_path),
            tolerance=args.tolerance,
            angular_tolerance=args.angular_tolerance,
        )
        eprint(f"wrote {stl_path}")
        artifacts["stl"] = str(stl_path)

    dxf_z = None
    dxf_error = None
    if args.dxf:
        dxf_path = outdir / f"{stem}.dxf"
        try:
            dxf_z = _export_dxf(part, dxf_path, build123d, args.dxf_z)
        except LabCadError as exc:
            # Not fatal: finish the manifest so the STEP already on disk keeps its
            # provenance record, and fail at the end instead.
            dxf_error = str(exc)
            eprint(f"warning: DXF export failed: {exc}")
        else:
            eprint(f"wrote {dxf_path} (section at z = {dxf_z:.3f} mm)")
            artifacts["dxf"] = str(dxf_path)

    facts = shape_facts(part)
    if not facts["is_valid"]:
        eprint(
            "WARNING: the generated solid fails OpenCascade validity checks. "
            "Fix the model source before fabricating."
        )

    # Evaluate the model's declared geometry checks against the solid just built.
    # These are measured, so a failure here is a real feature error, not a
    # declaration mismatch.
    declared_checks = model_checks(module)
    check_results = []
    checks_pass = True
    if declared_checks:
        check_results = evaluate_checks(part, declared_checks)
        checks_pass = all(item["pass"] for item in check_results)
        eprint(f"geometry checks: {len(check_results)}")
        for item in check_results:
            for line in format_check_result(item):
                eprint(line)
        if not checks_pass:
            eprint(
                "WARNING: geometry check(s) FAILED. The exported STEP does not meet "
                "the model's own declared requirements; fix the source and rerun."
            )

    manifest = {
        "artifact_name": stem,
        "source": {
            "path": str(args.model.resolve()),
            "sha256": sha256_of(args.model),
        },
        "parameters": params,
        "overrides": overrides,
        "interfaces": interfaces,
        "geometry_checks": {"declared": declared_checks, "results": check_results,
                            "pass": checks_pass},
        "geometry": facts,
        "artifacts": artifacts,
        "dxf_section_z_mm": dxf_z,
        "dxf_error": dxf_error,
        "environment": {
            "build123d": _build123d_version(),
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "units": "mm",
    }

    manifest_path = outdir / f"{stem}.manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    eprint(f"wrote {manifest_path}")

    if not interfaces:
        eprint(
            "note: no declared interfaces. Correct if nothing here mates with a bundled "
            "standard - do not invent one; name unchecked interface dimensions in the report."
        )

    box = facts["bounding_box_mm"]
    checks_note = (
        f"geometry checks: {sum(1 for c in check_results if c['pass'])}/{len(check_results)} pass"
        if check_results else "geometry checks: none declared"
    )
    lines = [
        f"{stem}: {box['x']:.2f} x {box['y']:.2f} x {box['z']:.2f} mm, "
        f"volume {facts['volume_mm3']:.1f} mm^3, valid={facts['is_valid']}, "
        f"declared interfaces: {len(interfaces)}, {checks_note}",
        f"Next: python scripts/check.py facts {step_path}",
    ]
    if interfaces:
        lines.append(f"      python scripts/check.py interfaces {manifest_path}")
    lines.append(
        f"      python scripts/snapshot.py {step_path} --out {outdir / (stem + '.png')}"
    )
    emit(manifest, args.as_json, "\n".join(lines))
    return 0 if facts["is_valid"] and dxf_error is None and checks_pass else 1


if __name__ == "__main__":
    main_guard(main)
```

### `scripts/snapshot.py`

```python
#!/usr/bin/env python3
"""Render a part to a multi-view PNG for mandatory visual review.

    python scripts/snapshot.py out/carrier.step --out out/carrier.png
    python scripts/snapshot.py carrier_model.py --out out/carrier.png --views iso,front,top

Renders offscreen through matplotlib's Agg backend, so it needs no display, no GPU,
and no viewer application. Faces come from OpenCascade's tessellation; the outlines
are the model's real BREP edges, drawn without hidden-line removal, so the render
reads slightly x-ray.

This step exists because ``is_valid`` and a correct bounding box are both fully
consistent with a pocket cut on the wrong face, an inverted mold polarity, or a
feature placed outside the body. Look at the image.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import (  # noqa: E402
    LabCadError,
    eprint,
    load_shape,
    main_guard,
)

# elevation, azimuth
VIEWS = {
    "iso": (24.0, -58.0),
    "front": (0.0, -90.0),
    "back": (0.0, 90.0),
    "right": (0.0, 0.0),
    "left": (0.0, 180.0),
    "top": (89.9, -90.0),
    "bottom": (-89.9, -90.0),
}
DEFAULT_VIEWS = ["iso", "front", "right", "top", "left", "bottom"]


def _require_matplotlib():
    try:
        import matplotlib  # noqa: PLC0415
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise LabCadError(
            "matplotlib is not installed in this interpreter.\n"
            '  uv pip install --python .venv-labcad/bin/python "matplotlib>=3.8"'
        ) from exc
    matplotlib.use("Agg")
    return matplotlib


def _to_rgb(color: str):
    from matplotlib.colors import to_rgb  # noqa: PLC0415

    return to_rgb(color)


def _shade(base, normals, elevation: float, azimuth: float):
    """Flat-shade each triangle by its angle to the camera for this view.

    Without this every face renders the same colour, which makes pockets,
    steps, and bosses almost impossible to read - defeating the purpose of a
    review render.
    """
    import numpy as np  # noqa: PLC0415

    elev_rad = np.radians(elevation)
    azim_rad = np.radians(azimuth)
    camera = np.array([
        np.cos(elev_rad) * np.cos(azim_rad),
        np.cos(elev_rad) * np.sin(azim_rad),
        np.sin(elev_rad),
    ])
    # Offset the light from the camera so faces square-on to the viewer still
    # separate from those angled away.
    light = camera + np.array([0.35, 0.25, 0.55])
    light /= np.linalg.norm(light)

    intensity = np.abs(normals @ light)
    scale = 0.55 + 0.45 * intensity
    colors = np.clip(np.asarray(base)[None, :] * scale[:, None], 0.0, 1.0)
    return colors


def _view_label(name: str, bbox) -> str:
    """In-plane extents for this view, in millimetres."""
    size_x, size_y, size_z = float(bbox.size.X), float(bbox.size.Y), float(bbox.size.Z)
    plane = {
        "front": (size_x, size_z),
        "back": (size_x, size_z),
        "right": (size_y, size_z),
        "left": (size_y, size_z),
        "top": (size_x, size_y),
        "bottom": (size_x, size_y),
    }.get(name)
    if plane is None:
        return ""
    return f"{plane[0]:.2f} x {plane[1]:.2f} mm"


def _edge_polylines(shape, samples: int = 24) -> list:
    """Sample the shape's real BREP edges as polylines.

    Drawing triangle edges instead puts a diagonal across every flat rectangular
    face -- pure tessellation noise that reads as a crease or a feature in a review
    render. The BREP edges are the ones a machinist would see.
    """
    try:
        edges = shape.edges()
    except (AttributeError, TypeError):  # pragma: no cover - kernel dependent
        return []

    polylines = []
    for edge in edges:
        try:
            straight = "LINE" in str(edge.geom_type)
            count = 2 if straight else samples
            points = [edge @ (index / (count - 1)) for index in range(count)]
            polylines.append([(float(p.X), float(p.Y), float(p.Z)) for p in points])
        except Exception:  # noqa: BLE001 - skip an edge the kernel cannot sample
            continue
    return polylines


def _tessellate(shape, deviation: float):
    """Return (vertices, triangles) as plain nested lists."""
    bbox = shape.bounding_box()
    diagonal = max(float(bbox.diagonal), 1.0)
    tolerance = diagonal * deviation
    vertices, triangles = shape.tessellate(tolerance)
    if not triangles:
        raise LabCadError(
            "tessellation produced no triangles; the shape may be empty or invalid"
        )
    points = [[float(v.X), float(v.Y), float(v.Z)] for v in vertices]
    return points, triangles


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("target", type=Path, help="STEP, STL, or *_model.py")
    parser.add_argument("--out", type=Path, required=True, help="output PNG path")
    parser.add_argument("--views", default=",".join(DEFAULT_VIEWS),
                        help=f"comma-separated views from {', '.join(VIEWS)} "
                             f"(default: {','.join(DEFAULT_VIEWS)})")
    parser.add_argument("--deviation", type=float, default=0.002,
                        help="tessellation deviation as a fraction of the bbox diagonal "
                             "(default: 0.002; lower is finer and slower)")
    parser.add_argument("--dpi", type=int, default=150)
    parser.add_argument("--color", default="#7ea9d4", help="base face colour")
    parser.add_argument("--no-edges", action="store_true",
                        help="skip the BREP edge overlay; faster on parts with thousands "
                             "of edges, at the cost of feature outlines")
    parser.add_argument("--show-axes", action="store_true",
                        help="draw mm axes and ticks; off by default because the "
                             "collapsed axis in an orthographic view overlaps its labels")
    args = parser.parse_args()

    requested = [name.strip() for name in args.views.split(",") if name.strip()]
    unknown = [name for name in requested if name not in VIEWS]
    if unknown:
        raise LabCadError(
            f"unknown view(s): {', '.join(unknown)}. Available: {', '.join(VIEWS)}"
        )

    _require_matplotlib()
    import matplotlib.pyplot as plt  # noqa: PLC0415
    from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection  # noqa: PLC0415

    eprint(f"loading {args.target} ...")
    shape = load_shape(args.target)

    eprint("tessellating ...")
    points, triangles = _tessellate(shape, args.deviation)
    outlines = [] if args.no_edges else _edge_polylines(shape)
    eprint(f"{len(points)} vertices, {len(triangles)} triangles, {len(outlines)} edges")

    import numpy as np  # noqa: PLC0415

    vertices = np.asarray(points, dtype=float)
    index = np.asarray(triangles, dtype=int)
    faces = vertices[index]

    # Per-face normals, used to shade each view from its own camera direction.
    normals = np.cross(faces[:, 1] - faces[:, 0], faces[:, 2] - faces[:, 0])
    lengths = np.linalg.norm(normals, axis=1, keepdims=True)
    normals = normals / np.where(lengths == 0.0, 1.0, lengths)

    base = _to_rgb(args.color)

    bbox = shape.bounding_box()
    centre = [
        (float(bbox.min.X) + float(bbox.max.X)) / 2.0,
        (float(bbox.min.Y) + float(bbox.max.Y)) / 2.0,
        (float(bbox.min.Z) + float(bbox.max.Z)) / 2.0,
    ]
    reach = max(float(bbox.size.X), float(bbox.size.Y), float(bbox.size.Z), 1e-6) / 2.0
    reach *= 1.08

    columns = min(3, len(requested))
    rows = (len(requested) + columns - 1) // columns
    figure = plt.figure(figsize=(4.2 * columns, 4.2 * rows))

    for position, name in enumerate(requested, start=1):
        elevation, azimuth = VIEWS[name]
        axes = figure.add_subplot(rows, columns, position, projection="3d")

        shaded = _shade(base, normals, elevation, azimuth)
        collection = Poly3DCollection(
            faces, facecolors=shaded, edgecolors="none", alpha=1.0,
        )
        axes.add_collection3d(collection)
        if outlines:
            # Matplotlib cannot hidden-line-remove across collections, so these
            # include far-side edges. That reads as slightly x-ray, and is called
            # out in the message below rather than hidden.
            axes.add_collection3d(Line3DCollection(
                outlines, colors=[(0.10, 0.16, 0.24, 0.7)], linewidths=0.5,
            ))
        axes.set_xlim(centre[0] - reach, centre[0] + reach)
        axes.set_ylim(centre[1] - reach, centre[1] + reach)
        axes.set_zlim(centre[2] - reach, centre[2] + reach)
        # zoom fills the frame; without it, turning the axes off leaves the shape
        # small in a mostly empty subplot.
        try:
            axes.set_box_aspect((1, 1, 1), zoom=1.0 if args.show_axes else 1.45)
        except TypeError:  # matplotlib < 3.6 has no zoom parameter
            axes.set_box_aspect((1, 1, 1))
        axes.view_init(elev=elevation, azim=azimuth)
        # Matplotlib's 3D default is perspective, which bends a square part into a
        # wedge and makes a straight wall look tapered - the exact kind of thing this
        # render exists to rule out. Every view here is a true orthographic projection.
        axes.set_proj_type("ortho")
        axes.set_title(f"{name}   {_view_label(name, bbox)}", fontsize=10)

        if args.show_axes:
            axes.set_xlabel("x (mm)", fontsize=7)
            axes.set_ylabel("y (mm)", fontsize=7)
            axes.set_zlabel("z (mm)", fontsize=7)
            axes.tick_params(labelsize=6)
        else:
            # Orthographic views collapse one axis, which produces a stack of
            # overlapping tick labels. Legibility of the shape is the point here;
            # use `check.py facts` for numbers.
            axes.set_axis_off()

    figure.suptitle(
        f"{args.target.name}   "
        f"{float(bbox.size.X):.2f} x {float(bbox.size.Y):.2f} x {float(bbox.size.Z):.2f} mm",
        fontsize=12,
    )
    figure.tight_layout()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.out, dpi=args.dpi, bbox_inches="tight")
    plt.close(figure)

    eprint(f"wrote {args.out}")
    print(
        f"{args.out}\n"
        "Now READ the image. Confirm: pockets on the intended face, mold polarity "
        "correct, every port and boss present and inside the body, no feature "
        "consumed by a fillet.\n"
        "Reading it: views are true orthographic, and the outlines are the model's real "
        "edges, hidden ones included. So a circle showing 'through' material is a "
        "far-side bore, not a window - the part is not transparent."
    )
    return 0


if __name__ == "__main__":
    main_guard(main)
```

### `assets/standards.json`

```json
{
  "schema_version": "1.0",
  "units": "mm",
  "note": "Dimensional standards for lab-hardware interfaces. Every entry carries a source. Entries with verified=false were not confirmed against the primary document during authoring and must be checked before use.",
  "last_reviewed": "2026-08-15",
  "standards": {
    "slas-microplate-footprint": {
      "title": "Microplate footprint (base outline)",
      "authority": "ANSI/SLAS",
      "document": "ANSI/SLAS 1-2004 (R2012) Footprint Dimensions",
      "url": "https://www.slas.org/SLAS/assets/File/public/standards/ANSI_SLAS_1-2004_FootprintDimensions.pdf",
      "verified": true,
      "dimensions": {
        "footprint_length": {
          "nominal": 127.76,
          "tol_plus": 0.25,
          "tol_minus": 0.25,
          "note": "Measured within 12.7 mm of the outside corners. Relaxes to +/-0.5 mm at any point along the side."
        },
        "footprint_width": {
          "nominal": 85.48,
          "tol_plus": 0.25,
          "tol_minus": 0.25,
          "note": "Measured within 12.7 mm of the outside corners. Relaxes to +/-0.5 mm at any point along the side."
        },
        "corner_radius": {
          "nominal": 3.18,
          "tol_plus": 1.6,
          "tol_minus": 1.6,
          "note": "Outside radius of the four bottom-flange corners (convex). A receiving pocket's internal fillet must be no LARGER than the minimum (1.58) or it bulges into the plate corner and binds; a sharp pocket corner or a corner-relief cut always clears. Do not size the pocket fillet to the maximum radius."
        }
      },
      "fit_checks": [
        {"measure": "bbox_x", "dimension": "footprint_length"},
        {"measure": "bbox_y", "dimension": "footprint_width"}
      ],
      "design_note": "For a pocket that receives a plate, add clearance per side on top of the maximum material condition (127.76 + 0.25 = 128.01). Check the pocket, not the plate."
    },
    "slas-microplate-height": {
      "title": "Microplate height",
      "authority": "ANSI/SLAS",
      "document": "ANSI/SLAS 2-2004 (R2012) Height Dimensions",
      "url": "https://www.slas.org/SLAS/assets/File/public/standards/ANSI_SLAS_2-2004_HeightDimensions.pdf",
      "verified": true,
      "dimensions": {
        "plate_height": {
          "nominal": 14.35,
          "tol_plus": 0.25,
          "tol_minus": 0.25,
          "note": "Datum A (resting plane) to the maximum protrusion of the perimeter wells. Secondary sources also quote +/-0.76 mm; consult the document before relying on the tighter band. Lidded and deep-well plates are taller and out of scope of this dimension."
        }
      },
      "fit_checks": [
        {"measure": "bbox_z", "dimension": "plate_height"}
      ]
    },
    "slas-microplate-flange": {
      "title": "Microplate bottom outside flange height",
      "authority": "ANSI/SLAS",
      "document": "ANSI/SLAS 3-2004 (R2012) Bottom Outside Flange Dimensions",
      "url": "https://www.slas.org/SLAS/assets/File/public/standards/ANSI_SLAS_3-2004_BottomOutsideFlangeDimensions.pdf",
      "verified": true,
      "dimensions": {
        "flange_height_short": {"nominal": 2.41, "tol_plus": 0.38, "tol_minus": 0.38},
        "flange_height_medium": {"nominal": 6.10, "tol_plus": 0.38, "tol_minus": 0.38},
        "flange_height_tall": {"nominal": 7.62, "tol_plus": 0.38, "tol_minus": 0.38}
      },
      "fit_checks": [],
      "design_note": "Three flange heights are standardised. A gripper or carrier that assumes one will drop plates built to another. Ask which the user has."
    },
    "slas-well-positions-96": {
      "title": "96-well plate well positions",
      "authority": "ANSI/SLAS",
      "document": "ANSI/SLAS 4-2004 (R2012) Well Positions",
      "url": "https://www.slas.org/SLAS/assets/File/public/standards/ANSI_SLAS_4-2004_WellPositions.pdf",
      "verified": true,
      "dimensions": {
        "well_pitch": {"nominal": 9.0, "tol_plus": 0.0, "tol_minus": 0.0, "note": "Centre-to-centre in both x and y."},
        "a1_offset_x": {"nominal": 14.38, "tol_plus": 0.0, "tol_minus": 0.0, "note": "Left outside edge to the centre of column 1."},
        "a1_offset_y": {"nominal": 11.24, "tol_plus": 0.0, "tol_minus": 0.0, "note": "Top outside edge to the centre of row A."},
        "well_position_tolerance": {"nominal": 0.70, "tol_plus": 0.0, "tol_minus": 0.0, "note": "Each well centre lies within a 0.70 mm diameter of nominal. This is a positional tolerance zone, not a +/- band."}
      },
      "fit_checks": [],
      "design_note": "Grid layout: x = a1_offset_x + 9.0 * column_index, y = a1_offset_y + 9.0 * row_index, measured from the plate outline corner."
    },
    "slas-well-positions-384": {
      "title": "384-well plate well positions",
      "authority": "ANSI/SLAS",
      "document": "ANSI/SLAS 4-2004 (R2012) Well Positions",
      "url": "https://www.slas.org/SLAS/assets/File/public/standards/ANSI_SLAS_4-2004_WellPositions.pdf",
      "verified": false,
      "dimensions": {
        "well_pitch": {"nominal": 4.5, "tol_plus": 0.0, "tol_minus": 0.0, "note": "Centre-to-centre in both x and y."},
        "a1_offset_x": {"nominal": 12.13, "tol_plus": 0.0, "tol_minus": 0.0, "note": "UNVERIFIED. Derived as the 96-well offset minus half the 96-well pitch. Confirm against ANSI/SLAS 4-2004 before cutting metal."},
        "a1_offset_y": {"nominal": 8.99, "tol_plus": 0.0, "tol_minus": 0.0, "note": "UNVERIFIED. Derived, as above. Confirm against the document."}
      },
      "fit_checks": [],
      "design_note": "Only well_pitch is confirmed here. Read the standard for the A1 offsets before relying on them."
    },
    "slas-well-positions-1536": {
      "title": "1536-well plate well positions",
      "authority": "ANSI/SLAS",
      "document": "ANSI/SLAS 4-2004 (R2012) Well Positions",
      "url": "https://www.slas.org/SLAS/assets/File/public/standards/ANSI_SLAS_4-2004_WellPositions.pdf",
      "verified": false,
      "dimensions": {
        "well_pitch": {"nominal": 2.25, "tol_plus": 0.0, "tol_minus": 0.0, "note": "Centre-to-centre in both x and y."},
        "a1_offset_x": {"nominal": 11.005, "tol_plus": 0.0, "tol_minus": 0.0, "note": "UNVERIFIED. Derived from the 96-well offset. Confirm against ANSI/SLAS 4-2004."},
        "a1_offset_y": {"nominal": 7.865, "tol_plus": 0.0, "tol_minus": 0.0, "note": "UNVERIFIED. Derived, as above. Confirm against the document."}
      },
      "fit_checks": [],
      "design_note": "Only well_pitch is confirmed here."
    },
    "cuvette-standard-10mm": {
      "title": "Standard 10 mm path-length spectrophotometer cuvette",
      "authority": "De facto industry convention",
      "document": "No single ANSI/ISO document fixes this; it is a near-universal convention across suppliers.",
      "url": "https://spectrecology.com/blog/guide-to-cuvettes/",
      "verified": true,
      "dimensions": {
        "external_width": {"nominal": 12.5, "tol_plus": 0.1, "tol_minus": 0.1, "note": "Tolerance is indicative; suppliers vary."},
        "external_depth": {"nominal": 12.5, "tol_plus": 0.1, "tol_minus": 0.1},
        "external_height": {"nominal": 45.0, "tol_plus": 0.5, "tol_minus": 0.5, "note": "Body height excluding any cap or stopper. Semi-micro and micro cuvettes share the external footprint but differ in height and internal geometry."},
        "path_length": {"nominal": 10.0, "tol_plus": 0.0, "tol_minus": 0.0, "note": "Internal optical path. 12.5 external minus 2 x 1.25 mm wall."},
        "wall_thickness": {"nominal": 1.25, "tol_plus": 0.0, "tol_minus": 0.0}
      },
      "fit_checks": [
        {"measure": "bbox_x", "dimension": "external_width"},
        {"measure": "bbox_y", "dimension": "external_depth"}
      ],
      "design_note": "Because this is a convention rather than a standard, a holder should be designed with generous clearance or a compliant feature. Confirm against the user's actual cuvettes."
    },
    "optical-breadboard-metric": {
      "title": "Metric optical breadboard hole grid",
      "authority": "De facto industry convention",
      "document": "Universal across Thorlabs, Newport, Edmund and others for metric tables.",
      "url": "https://www.thorlabs.com/imperial-and-metric-threading",
      "verified": true,
      "dimensions": {
        "grid_pitch": {"nominal": 25.0, "tol_plus": 0.0, "tol_minus": 0.0, "note": "Metric grid. NOT interchangeable with the 25.4 mm imperial grid."},
        "thread": {"nominal": 6.0, "tol_plus": 0.0, "tol_minus": 0.0, "note": "M6 x 1.0 tapped holes."},
        "clearance_hole_close": {"nominal": 6.4, "tol_plus": 0.0, "tol_minus": 0.0, "note": "Close-fit clearance for an M6 cap screw."},
        "clearance_hole_normal": {"nominal": 6.6, "tol_plus": 0.0, "tol_minus": 0.0, "note": "Normal-fit clearance for M6. Prefer this on printed parts."},
        "counterbore_dia": {"nominal": 11.0, "tol_plus": 0.0, "tol_minus": 0.0, "note": "For an M6 socket head cap screw head (nominal head dia 10 mm)."},
        "screw_head_height": {"nominal": 6.0, "tol_plus": 0.0, "tol_minus": 0.0, "note": "M6 socket head cap screw head height (ISO 4762). A counterbore shallower than this leaves the head proud, not flush."},
        "border": {"nominal": 12.5, "tol_plus": 0.0, "tol_minus": 0.0, "note": "Typical edge-to-first-hole distance. A property of the TABLE, not of your part: your plate's edge margin is a free design choice, so do not declare this as an interface."}
      },
      "fit_checks": [],
      "design_note": "Slot rather than hole one of any pair of mounting features to absorb grid and print tolerance."
    },
    "optical-breadboard-imperial": {
      "title": "Imperial optical breadboard hole grid",
      "authority": "De facto industry convention",
      "document": "Universal across Thorlabs, Newport, Edmund and others for imperial tables.",
      "url": "https://www.thorlabs.com/imperial-and-metric-threading",
      "verified": true,
      "dimensions": {
        "grid_pitch": {"nominal": 25.4, "tol_plus": 0.0, "tol_minus": 0.0, "note": "1 inch exactly. Over four holes this differs from the metric grid by 1.6 mm."},
        "thread_major_dia": {"nominal": 6.35, "tol_plus": 0.0, "tol_minus": 0.0, "note": "1/4-20 UNC: 0.25 inch major diameter, 20 threads per inch."},
        "clearance_hole_normal": {"nominal": 6.8, "tol_plus": 0.0, "tol_minus": 0.0, "note": "Normal-fit clearance for a 1/4-20 screw."},
        "counterbore_dia": {"nominal": 11.2, "tol_plus": 0.0, "tol_minus": 0.0, "note": "For a 1/4-20 socket head cap screw head."},
        "screw_head_height": {"nominal": 6.35, "tol_plus": 0.0, "tol_minus": 0.0, "note": "1/4-20 socket head cap screw head height (0.25 inch). A counterbore shallower than this leaves the head proud, not flush."},
        "border": {"nominal": 12.7, "tol_plus": 0.0, "tol_minus": 0.0, "note": "Typical 0.5 inch edge-to-first-hole distance. A property of the TABLE, not of your part: your plate's edge margin is a free design choice, so do not declare this as an interface."}
      },
      "fit_checks": [],
      "design_note": "Ask which table the user has. Assuming the wrong system is the most common optomechanical design error."
    },
    "cage-system-30mm": {
      "title": "30 mm cage system",
      "authority": "Thorlabs (de facto standard, second-sourced by others)",
      "document": "Thorlabs 30 mm cage system construction rods and cage plates",
      "url": "https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_ID=2273",
      "verified": true,
      "dimensions": {
        "rod_spacing": {"nominal": 30.0, "tol_plus": 0.0, "tol_minus": 0.0, "note": "Rod centre to rod centre, on a square pattern. 1.18 inch."},
        "rod_diameter": {"nominal": 6.0, "tol_plus": 0.0, "tol_minus": 0.0, "note": "ER series cage rods."},
        "plate_thickness_typical": {"nominal": 8.9, "tol_plus": 0.0, "tol_minus": 0.0, "note": "0.35 inch, the CP33 standard cage plate. Informational, not a mating dimension: custom plates may be any thickness, but matching it keeps optical path budgets simple."}
      },
      "fit_checks": [],
      "design_note": "The 30 mm rod square is centred on the optical axis. A custom plate must place its aperture at the centroid of the four rod bores. Bore diameter is rod_diameter plus twice the free-sliding per-side clearance for YOUR process (fabrication-limits.md): about 6.2 CNC, 6.4 SLA, 6.8 FDM. 6.1 is a reamed-metal number and binds on printed parts. Four bores on a common square over-constrain each other, so do not go tighter than the fits table. Declare the bore against rod_diameter with intent envelope and the clearance you chose."
    },
    "sm1-lens-tube-thread": {
      "title": "SM1 lens tube thread",
      "authority": "Thorlabs (de facto standard)",
      "document": "Thorlabs SM1 series threading",
      "url": "https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=4114",
      "verified": true,
      "dimensions": {
        "thread_major_dia": {"nominal": 26.289, "tol_plus": 0.0, "tol_minus": 0.0, "note": "1.035 inch-40 thread. Holds 1 inch diameter optics."},
        "threads_per_inch": {"nominal": 40.0, "tol_plus": 0.0, "tol_minus": 0.0},
        "pitch": {"nominal": 0.635, "tol_plus": 0.0, "tol_minus": 0.0, "note": "25.4 / 40 mm."},
        "optic_dia": {"nominal": 25.4, "tol_plus": 0.0, "tol_minus": 0.0, "note": "1 inch optic."}
      },
      "fit_checks": [],
      "design_note": "A 40 TPI thread has a 0.635 mm pitch, which is at or below the resolution of most FDM printers. Print a clearance bore and use a purchased SM1 adapter or a tapped insert rather than printing the thread."
    }
  }
}
```
