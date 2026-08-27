---
name: medchem
description: Medicinal chemistry filters for compound triage. Apply drug-likeness rules (Lipinski, Veber, CNS), structural alert catalogs (PAINS, NIBR, ChEMBL), complexity metrics, and the medchem query language for library filtering.
---

# Medchem

## Overview

Medchem is a Python library from [datamol-io](https://github.com/datamol-io/medchem) for molecular filtering and prioritization in drug discovery. Apply literature-derived drug-likeness rules, named alert catalogs, complexity thresholds, chemical-group detection, and a custom query language to triage compound libraries at scale. Filters are context-specific guidelines — combine with domain expertise and target knowledge.

**Version note:** Examples target **medchem 2.0.5** (PyPI stable, Nov 2024). Requires **Python ≥3.9**. Depends on **datamol** and **RDKit** (installed automatically). `RuleFilters` and structural filter classes return **pandas DataFrames**. Lilly demerits require optional native binaries (`mamba install lilly-medchem-rules`).

## When to Use This Skill

This skill should be used when:
- Applying drug-likeness rules (Lipinski, Veber, CNS, lead-like) to compound libraries
- Filtering molecules by structural alerts, PAINS, or NIBR screening-deck rules
- Prioritizing compounds for hit-to-lead or lead optimization
- Calculating complexity metrics against ZINC-derived thresholds
- Detecting functional groups or named substructure catalogs
- Building multi-criteria filters with the medchem query language

## Installation

```bash
uv pip install medchem datamol
```

Optional — Eli Lilly demerit filter (requires conda-forge native binaries):

```bash
mamba install -c conda-forge lilly-medchem-rules
```

## Core Capabilities

### 1. Medicinal Chemistry Rules

Apply established drug-likeness rules via `medchem.rules`.

**List available rules:**

```python
import medchem as mc

mc.rules.RuleFilters.list_available_rules_names()
# ['rule_of_five', 'rule_of_five_beyond', 'rule_of_four', 'rule_of_three', ...]
```

**Single rule on one molecule:**

```python
import datamol as dm
import medchem as mc

smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"  # aspirin
mc.rules.basic_rules.rule_of_five(smiles)   # True
mc.rules.basic_rules.rule_of_cns(smiles)    # True
mc.rules.basic_rules.rule_of_veber(smiles)  # True
```

**Multiple rules with `RuleFilters` (returns a DataFrame):**

```python
import datamol as dm
import medchem as mc

mols = [dm.to_mol(s) for s in smiles_list]

rfilter = mc.rules.RuleFilters(
    rule_list=["rule_of_five", "rule_of_oprea", "rule_of_cns", "rule_of_leadlike_soft"]
)
df = rfilter(mols=mols, n_jobs=-1, progress=True, keep_props=False)

# Columns: mol, pass_all, pass_any, rule_of_five, rule_of_oprea, ...
passing = df[df["pass_all"]]
```

Use `keep_props=True` to include computed descriptors (`mw`, `clogp`, `tpsa`, etc.) in the result.

### 2. Structural Alert Filters

Detect problematic patterns with `medchem.structural`. Both classes return **DataFrames** with `pass_filter`, `status`, and `reasons` columns.

**Common alerts (ChEMBL-derived rule sets):**

```python
import medchem as mc

alert_filter = mc.structural.CommonAlertsFilters()
df = alert_filter(mols=mol_list, n_jobs=-1, progress=True)
# df columns: mol, pass_filter, status, reasons

clean = df[df["pass_filter"]]
```

**NIBR filters (Novartis screening-deck curation):**

```python
nibr_filter = mc.structural.NIBRFilters()
df = nibr_filter(mols=mol_list, n_jobs=-1, progress=True)
# df columns: mol, pass_filter, status, severity, reasons, n_covalent_motif, special_mol
```

Compounds with `severity >= 10` are excluded by default (see NIBR paper).

### 3. Named Catalog Filters (PAINS, Brenk, etc.)

Use `medchem.catalogs.NamedCatalogs` for RDKit `FilterCatalog` instances, or the functional API:

```python
import medchem as mc

# List available named catalogs
mc.catalogs.list_named_catalogs()
# ['tox', 'pains', 'pains_a', 'brenk', 'nibr', 'zinc', ...]

# Functional API — True means molecule passes (no alert match)
passes = mc.functional.alert_filter(mols=mol_list, alerts=["pains"], n_jobs=-1)

# Or via catalog objects
passes = mc.functional.catalog_filter(
    mols=mol_list,
    catalogs=[mc.catalogs.NamedCatalogs.pains()],
    n_jobs=-1,
)
```

### 4. Functional API

`medchem.functional` provides one-call wrappers that return boolean masks (True = passes):

```python
import medchem as mc

mc.functional.rules_filter(mols=mol_list, rules=["rule_of_five", "rule_of_cns"], n_jobs=-1)
mc.functional.nibr_filter(mols=mol_list, max_severity=10, n_jobs=-1)
mc.functional.alert_filter(mols=mol_list, alerts=["pains", "brenk"], n_jobs=-1)
mc.functional.complexity_filter(mols=mol_list, complexity_metric="bertz", limit="99", n_jobs=-1)
```

Other helpers: `catalog_filter`, `chemical_group_filter`, `lilly_demerit_filter` (requires optional binaries), `macrocycle_filter`, `bredt_filter`, `protecting_groups_filter`, and more.

### 5. Chemical Groups

Detect functional groups and curated pattern collections via `medchem.groups`:

```python
import medchem as mc

# Browse available group collections
mc.groups.list_default_chemical_groups()
# ['privileged_scaffolds', 'common_warhead_covalent_inhibitors', 'rings_in_drugs', ...]

group = mc.groups.ChemicalGroup(groups=["privileged_scaffolds"])
group.has_match(mol)                          # bool
group.get_matches(mol)                        # dict of group → atom indices
group.filter(mols)                            # molecules matching the group

# Returns molecules that do NOT match the group
mc.functional.chemical_group_filter(mols=mol_list, chemical_group=group, n_jobs=-1)
```

Custom groups can be loaded from a file via `groups_db` (CSV with `smiles`/`smarts`, `name`, `group` columns).

### 6. Molecular Complexity

Compare complexity metrics to precomputed ZINC-15 percentile thresholds:

```python
import medchem as mc

# Single molecule
cf = mc.complexity.ComplexityFilter(limit="99", complexity_metric="bertz")
cf(mol)  # True if below 99th-percentile threshold

# Batch via functional API
mc.functional.complexity_filter(
    mols=mol_list,
    complexity_metric="bertz",  # also: sas, qed, whitlock, barone, smcm, twc
    limit="99",
    n_jobs=-1,
)

# Direct metric functions
mc.complexity.WhitlockCT(mol)
mc.complexity.BaroneCT(mol)
```

### 7. Scaffold Constraints

`medchem.constraints.Constraints` matches a core scaffold and applies per-atom constraint functions — not simple MW/LogP ranges. For property bounds, use `RuleFilters`, descriptors via `mc.rules.list_descriptors()`, or the query language.

```python
import datamol as dm
import medchem as mc

core = dm.to_mol("c1ccccc1")
constraints = mc.constraints.Constraints(
    core=core,
    constraint_fns={"query": lambda mol, atom_idx, query: ...},
)
constraints(mol)
```

### 8. Medchem Query Language

Build multi-criteria filters with `medchem.query.QueryFilter`:

```python
import medchem as mc

# Rule + alert combination
qf = mc.query.QueryFilter('MATCHRULE("rule_of_five") AND NOT HASALERT("pains")')
mask = qf(mols=mol_list, n_jobs=-1)  # list[bool]

# CNS-like with property bounds
qf = mc.query.QueryFilter('MATCHRULE("rule_of_cns") AND HASPROP("tpsa", <=, 90)')
mask = qf(mols=mol_list, n_jobs=-1)
```

**Query syntax:**
- `MATCHRULE("rule_of_five")` — apply a named rule
- `HASALERT("pains")` — match a named catalog (`pains`, `brenk`, `nibr`, `tox`, …)
- `HASPROP("mw", <, 500)` — compare a descriptor (unquoted comparator)
- `HASGROUP("privileged_scaffolds")` — match a chemical group
- `HASSUBSTRUCTURE("c1ccccc1")` — substructure match
- Operators: `AND`, `OR`, `NOT`

List available descriptors: `mc.rules.list_descriptors()`

## Workflow Patterns

### Pattern 1: Initial Triage of a Compound Library

```python
import datamol as dm
import medchem as mc
import pandas as pd

df = pd.read_csv("compounds.csv")
mols = [dm.to_mol(s) for s in df["smiles"]]

# Drug-likeness rules
rules_df = mc.rules.RuleFilters(rule_list=["rule_of_five", "rule_of_veber"])(mols=mols, n_jobs=-1)

# PAINS + common alerts via query
qf = mc.query.QueryFilter('MATCHRULE("rule_of_five") AND NOT HASALERT("pains")')
pass_mask = qf(mols=mols, n_jobs=-1)

df["passes_rules"] = rules_df["pass_all"].values
df["drug_like"] = pass_mask
filtered_df = df[df["drug_like"]]
filtered_df.to_csv("filtered_compounds.csv", index=False)
```

### Pattern 2: Lead Optimization Filtering

```python
import medchem as mc

rules_df = mc.rules.RuleFilters(rule_list=["rule_of_leadlike_soft"])(mols=candidates, n_jobs=-1)
nibr_df = mc.structural.NIBRFilters()(mols=candidates, n_jobs=-1)
complex_mask = mc.functional.complexity_filter(
    mols=candidates, complexity_metric="bertz", limit="95", n_jobs=-1
)

passes = (
    rules_df["pass_all"]
    & nibr_df["pass_filter"]
    & complex_mask
)
```

### Pattern 3: Detect Functional Groups

```python
import medchem as mc

group = mc.groups.ChemicalGroup(groups=["common_warhead_covalent_inhibitors"])
matches = [group.has_match(mol) for mol in mol_list]
warhead_mols = [mol for mol, m in zip(mol_list, matches) if m]
```

## Best Practices

1. **Context matters** — marketed drugs often violate Ro5; prodrugs and natural products are common exceptions.
2. **Combine filters** — rules, alert catalogs, and complexity thresholds work best together.
3. **Use parallelization** — pass `n_jobs=-1` for libraries >1000 molecules.
4. **Check return types** — `RuleFilters` and structural classes return DataFrames; functional helpers return boolean arrays.
5. **Lilly demerits are optional** — install `lilly-medchem-rules` separately; default max demerits is 160 in the functional API.
6. **Document decisions** — retain `status`, `reasons`, and `severity` columns for audit trails.

## Resources

### references/api_guide.md
Module-by-module API reference with signatures, return types, and patterns.

### references/rules_catalog.md
Catalog of available rules, alert sets, complexity metrics, and filter selection guidelines.

### scripts/filter_molecules.py
Batch filtering script for CSV/TSV/SDF/SMILES inputs with configurable rules, alerts, and complexity thresholds.

```bash
uv run python scripts/filter_molecules.py input.csv \
  --rules rule_of_five,rule_of_cns --pains --nibr --output filtered.csv
```

## Documentation

- Official docs: https://medchem-docs.datamol.io/
- GitHub: https://github.com/datamol-io/medchem
- PyPI: https://pypi.org/project/medchem/ (2.0.5)

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/medchem/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/api_guide.md`

# Medchem API Reference

Reference for **medchem 2.0.5**. Official docs: https://medchem-docs.datamol.io/stable/api/

## Module: medchem.rules

### Class: RuleFilters

Filter molecules by multiple medicinal chemistry rules. Returns a **pandas DataFrame**.

**Constructor:**

```python
RuleFilters(rule_list: List[Union[str, Callable]], rule_list_names: Optional[List[str]] = None)
```

**Call signature:**

```python
__call__(
    mols: Sequence[Union[str, Mol]],
    n_jobs: int = -1,
    progress: bool = False,
    progress_leave: bool = False,
    scheduler: str = "auto",
    keep_props: bool = False,
    fail_if_invalid: bool = True,
) -> pd.DataFrame
```

**Return columns:** `mol`, `pass_all`, `pass_any`, plus one boolean column per rule. With `keep_props=True`, descriptor columns (`mw`, `clogp`, `tpsa`, etc.) are included.

**Class methods:**

```python
RuleFilters.list_available_rules_names()  # list of 22 rule names
RuleFilters.list_available_rules()        # rules with property metadata
```

**Example:**

```python
rfilter = mc.rules.RuleFilters(rule_list=["rule_of_five", "rule_of_cns"])
df = rfilter(mols=mol_list, n_jobs=-1, progress=True)
passing = df[df["pass_all"]]
```

### Module: medchem.rules.basic_rules

Individual rule functions for single molecules. Each returns `bool` (True = passes).

| Function | Description |
|----------|-------------|
| `rule_of_five(mol)` | Lipinski Rule of Five |
| `rule_of_five_beyond(mol)` | Beyond Ro5 (large binding sites) |
| `rule_of_four(mol)` | Rule of Four |
| `rule_of_three(mol)` | Fragment library Rule of Three |
| `rule_of_three_extended(mol)` | Extended Ro3 |
| `rule_of_two(mol)` | Rule of Two |
| `rule_of_ghose(mol)` | Ghose filter |
| `rule_of_veber(mol)` | Veber oral bioavailability |
| `rule_of_reos(mol)` | REOS filter |
| `rule_of_chemaxon_druglikeness(mol)` | ChemAxon drug-likeness |
| `rule_of_egan(mol)` | Egan permeability |
| `rule_of_pfizer_3_75(mol)` | Pfizer 3/75 filter |
| `rule_of_gsk_4_400(mol)` | GSK 4/400 filter |
| `rule_of_oprea(mol)` | Oprea lead-like |
| `rule_of_xu(mol)` | Xu filter |
| `rule_of_cns(mol)` | CNS drug-likeness |
| `rule_of_respiratory(mol)` | Respiratory drug-likeness |
| `rule_of_zinc(mol)` | ZINC-like |
| `rule_of_leadlike_soft(mol)` | Soft lead-like |
| `rule_of_druglike_soft(mol)` | Soft drug-like |
| `rule_of_generative_design(mol)` | Generative design space |
| `rule_of_generative_design_strict(mol)` | Strict generative design |

### Descriptor helpers

```python
mc.rules.list_descriptors()  # property names for query language
```

---

## Module: medchem.structural

### Class: CommonAlertsFilters

ChEMBL-derived structural alert filter sets (Glaxo, Dundee, BMS, etc.).

```python
CommonAlertsFilters()
```

**Returns DataFrame columns:** `mol`, `pass_filter`, `status`, `reasons`

- `status`: one of `"exclude"`, `"flag"`, `"annotations"`, `"ok"`
- `pass_filter`: bool — True if compound passes

**Methods:**

```python
list_default_available_alerts()  # DataFrame of alert definitions
__call__(mols, n_jobs=-1, progress=False, ...) -> pd.DataFrame
```

### Class: NIBRFilters

Novartis screening-deck curation filters ([Schuffenhauer et al., J. Med. Chem. 2020](https://dx.doi.org/10.1021/acs.jmedchem.0c01332)).

```python
NIBRFilters()
```

**Returns DataFrame columns:** `mol`, `pass_filter`, `status`, `severity`, `reasons`, `n_covalent_motif`, `special_mol`

- `severity`: 0 = clean; 1–9 = flags; ≥10 = excluded by default

### Lilly demerits (optional)

Requires `mamba install lilly-medchem-rules`. Access via:

```python
mc.functional.lilly_demerit_filter(mols, max_demerits=160, n_jobs=-1)
# or
from medchem.structural.lilly_demerits import LillyDemeritsFilters
```

---

## Module: medchem.functional

High-level boolean-mask API. **True = passes** (no alert / passes all rules).

| Function | Description |
|----------|-------------|
| `rules_filter(mols, rules, n_jobs=None, ...)` | Apply rule list |
| `nibr_filter(mols, max_severity=10, n_jobs=None, ...)` | NIBR filter |
| `alert_filter(mols, alerts, alerts_db=None, n_jobs=1, ...)` | Named alert catalogs |
| `catalog_filter(mols, catalogs, n_jobs=-1, ...)` | RDKit FilterCatalog list |
| `complexity_filter(mols, complexity_metric="bertz", limit="99", ...)` | Complexity threshold |
| `lilly_demerit_filter(mols, max_demerits=160, ...)` | Lilly demerits (optional) |
| `chemical_group_filter(mols, chemical_group, ...)` | Exclude group matches |
| `catalog_filter(mols, catalogs, ...)` | Custom catalog list |
| `bredt_filter(mols, ...)` | Bredt instability filter |
| `macrocycle_filter(mols, ...)` | Macrocycle filter |
| `protecting_groups_filter(mols, ...)` | Protecting group filter |
| `ring_infraction_filter(mols, ...)` | Ring infraction filter |
| `symmetry_filter(mols, ...)` | Symmetry filter |

---

## Module: medchem.catalogs

### NamedCatalogs

Static methods returning RDKit `FilterCatalog` objects:

```python
mc.catalogs.list_named_catalogs()
# tox, pains, pains_a, pains_b, pains_c, nih, zinc, brenk, dundee, bms,
# glaxo, schembl, mlsmr, inpharmatica, lint, nibr, bredt, toxicophore, ...

mc.catalogs.NamedCatalogs.pains()
mc.catalogs.NamedCatalogs.brenk()
mc.catalogs.NamedCatalogs.nibr()
mc.catalogs.NamedCatalogs.bredt()
```

**Helpers:**

```python
catalog_from_smarts(smarts_list)
merge_catalogs(catalogs)
list_named_catalogs()
```

---

## Module: medchem.groups

### ChemicalGroup

Detect functional groups from the global-chem curated library.

```python
ChemicalGroup(groups=None, n_jobs=None, groups_db=None)
```

**Methods:**

```python
has_match(mol, exact_match=False, terminal_only=False) -> bool
get_matches(mol, use_smiles=True, exact_match=False, terminal_only=False) -> dict
filter(mols) -> list[Mol]
get_catalog() -> FilterCatalog
list_groups() -> list
list_hierarchy_groups() -> list
```

**Listing helpers:**

```python
mc.groups.list_default_chemical_groups(hierarchy=False)
mc.groups.list_functional_group_names(unique=True)
mc.groups.get_functional_group_map()  # name → SMARTS
```

---

## Module: medchem.complexity

### Class: ComplexityFilter

Compare a metric to ZINC-15 percentile thresholds. Operates on **single molecules**.

```python
ComplexityFilter(
    limit="99",
    complexity_metric="bertz",
    threshold_stats_file="zinc_15_available",
)
cf(mol)  # -> bool
```

**Available metrics** (`ComplexityFilter.list_default_available_filters()`):
`bertz`, `sas`, `qed`, `clogp`, `whitlock`, `barone`, `smcm`, `twc`

**Direct metric functions:**

```python
mc.complexity.WhitlockCT(mol)
mc.complexity.BaroneCT(mol)
mc.complexity.SMCM(mol)
mc.complexity.TWC(mol)
```

For batch filtering, use `mc.functional.complexity_filter()`.

---

## Module: medchem.constraints

### Class: Constraints

Scaffold-based substructure matching with per-atom constraint functions — **not** simple property-range filters.

```python
Constraints(core: Mol, constraint_fns: Dict[str, Callable], prop_name: str = "query")
constraints(mol)  # -> bool or match details
```

Use `RuleFilters` or the query language for MW/LogP/TPSA bounds.

---

## Module: medchem.query

### Class: QueryFilter

Parse and evaluate the medchem query language.

```python
QueryFilter(query: str, grammar: Optional[str] = None, parser: str = "lalr")
qf(mols, n_jobs=-1, progress=True, scheduler="processes") -> list[bool]
```

**Grammar constructs:**

| Construct | Example |
|-----------|---------|
| Rule match | `MATCHRULE("rule_of_five")` |
| Alert catalog | `HASALERT("pains")` |
| Property compare | `HASPROP("mw", <, 500)` |
| Chemical group | `HASGROUP("privileged_scaffolds")` |
| Substructure | `HASSUBSTRUCTURE("c1ccccc1")` |
| Superstructure | `HASSUPERSTRUCTURE("CCO")` |
| Boolean | `true`, `false` |
| Logic | `AND`, `OR`, `NOT` |

**Example queries:**

```python
'MATCHRULE("rule_of_five") AND NOT HASALERT("pains")'
'MATCHRULE("rule_of_cns") AND HASPROP("tpsa", <=, 90)'
'NOT HASALERT("brenk") AND HASPROP("mw", >=, 200)'
```

### Class: QueryOperator

Holds available properties, catalogs, rules, and functional groups used by the parser.

---

## Common Patterns

### Parallel processing

```python
df = mc.rules.RuleFilters(rule_list=["rule_of_five"])(mols=mol_list, n_jobs=-1, progress=True)
mask = mc.functional.nibr_filter(mols=mol_list, n_jobs=-1)
```

### Combining filters

```python
rules_df = mc.rules.RuleFilters(rule_list=["rule_of_five"])(mols=mol_list, n_jobs=-1)
alerts_df = mc.structural.CommonAlertsFilters()(mols=mol_list, n_jobs=-1)

passing = [
    mol for i, mol in enumerate(mol_list)
    if rules_df.iloc[i]["pass_all"] and alerts_df.iloc[i]["pass_filter"]
]
```

### Working with DataFrames

```python
import pandas as pd
import datamol as dm
import medchem as mc

df = pd.read_csv("molecules.csv")
df["mol"] = df["smiles"].apply(dm.to_mol)

results = mc.rules.RuleFilters(rule_list=["rule_of_five", "rule_of_cns"])(
    mols=df["mol"].tolist(), n_jobs=-1
)
df = pd.concat([df, results.drop(columns=["mol"])], axis=1)
filtered = df[df["pass_all"]]
```

### `references/rules_catalog.md`

# Medchem Rules and Filters Catalog

Catalog of medicinal chemistry rules, alert sets, and filters in **medchem 2.0.5**.

## Table of Contents

1. [Drug-Likeness Rules](#drug-likeness-rules)
2. [Lead-Likeness Rules](#lead-likeness-rules)
3. [Fragment Rules](#fragment-rules)
4. [CNS and Target-Class Rules](#cns-and-target-class-rules)
5. [Structural Alert Filters](#structural-alert-filters)
6. [Named Catalogs](#named-catalogs)
7. [Complexity Metrics](#complexity-metrics)
8. [Chemical Group Collections](#chemical-group-collections)
9. [Filter Selection Guidelines](#filter-selection-guidelines)

---

## Drug-Likeness Rules

### Rule of Five (Lipinski)

**Reference:** Lipinski et al., *Adv Drug Deliv Rev* (1997) 23:3–25

**Criteria:** MW ≤ 500, LogP ≤ 5, HBD ≤ 5, HBA ≤ 10

```python
mc.rules.basic_rules.rule_of_five(mol)
# or
mc.rules.RuleFilters(rule_list=["rule_of_five"])
```

### Rule of Five Beyond

**Reference:** Doak et al., (2015) — compounds beyond Ro5 for large binding sites

**Criteria:** MW ≤ 1000, LogP ∈ [-2, 10], HBD ≤ 6, HBA ≤ 15, TPSA ≤ 250, rotatable bonds ≤ 20

```python
mc.rules.basic_rules.rule_of_five_beyond(mol)
```

### Rule of Veber

**Reference:** Veber et al., *J Med Chem* (2002) 45:2615–2623

**Criteria:** Rotatable bonds ≤ 10, TPSA ≤ 140 Ų

```python
mc.rules.basic_rules.rule_of_veber(mol)
```

### REOS (Rapid Elimination Of Swill)

**Reference:** Walters & Murcko, *Adv Drug Deliv Rev* (2002) 54:255–271

**Criteria:** MW 200–500, LogP −5 to 5, HBD 0–5, HBA 0–10

```python
mc.rules.basic_rules.rule_of_reos(mol)
```

### Egan, Ghose, Pfizer, GSK, Xu

Additional literature filters available as `rule_of_egan`, `rule_of_ghose`, `rule_of_pfizer_3_75`, `rule_of_gsk_4_400`, `rule_of_xu`.

### Rule of Druglike (Soft)

Combined soft drug-likeness criteria:

```python
mc.rules.basic_rules.rule_of_druglike_soft(mol)
```

---

## Lead-Likeness Rules

### Rule of Oprea

**Reference:** Oprea et al., *J Chem Inf Comput Sci* (2001) 41:1308–1315

**Criteria:** MW 200–350, LogP −2 to 4, rotatable bonds ≤ 7, rings ≤ 4

```python
mc.rules.basic_rules.rule_of_oprea(mol)
```

### Rule of Leadlike (Soft)

**Criteria:** MW 250–450, LogP −3 to 4, rotatable bonds ≤ 10

```python
mc.rules.basic_rules.rule_of_leadlike_soft(mol)
```

---

## Fragment Rules

### Rule of Three

**Reference:** Congreve et al., *Drug Discov Today* (2003) 8:876–877

**Criteria:** MW ≤ 300, LogP ≤ 3, HBD ≤ 3, HBA ≤ 3, rotatable bonds ≤ 3, PSA ≤ 60 Ų

```python
mc.rules.basic_rules.rule_of_three(mol)
```

Also available: `rule_of_three_extended`, `rule_of_two`, `rule_of_four`.

---

## CNS and Target-Class Rules

### Rule of CNS

**Criteria:** MW ≤ 450, LogP −1 to 5, HBD ≤ 2, TPSA ≤ 90 Ų

```python
mc.rules.basic_rules.rule_of_cns(mol)
```

### Rule of Respiratory

Target-class filter for respiratory drugs:

```python
mc.rules.basic_rules.rule_of_respiratory(mol)
```

### Generative Design Rules

For ML-generated molecules:

```python
mc.rules.basic_rules.rule_of_generative_design(mol)
mc.rules.basic_rules.rule_of_generative_design_strict(mol)
```

---

## Structural Alert Filters

### PAINS (Pan Assay INterference compoundS)

**Reference:** Baell & Holloway, *J Med Chem* (2010) 53:2719–2740

Apply via named catalog — not a `basic_rules` function:

```python
mc.functional.alert_filter(mols, alerts=["pains"], n_jobs=-1)
# or query: NOT HASALERT("pains")
```

Sub-catalogs: `pains_a`, `pains_b`, `pains_c`.

### Common Alerts Filters

ChEMBL-curated rule sets (Glaxo, Dundee, BMS, MLSMR, etc.):

```python
alert_filter = mc.structural.CommonAlertsFilters()
df = alert_filter(mols=mol_list, n_jobs=-1)
# status: exclude | flag | annotations | ok
```

### NIBR Filters

Novartis screening-deck curation ([Schuffenhauer et al., 2020](https://dx.doi.org/10.1021/acs.jmedchem.0c01332)):

```python
nibr_filter = mc.structural.NIBRFilters()
df = nibr_filter(mols=mol_list, n_jobs=-1)
# severity >= 10 → excluded by default
```

Or via functional API with `max_severity=10`.

### Lilly Demerits (optional)

Requires `mamba install lilly-medchem-rules`. 275 structural patterns; default exclusion at >160 demerits:

```python
mc.functional.lilly_demerit_filter(mols, max_demerits=160, n_jobs=-1)
```

---

## Named Catalogs

Available via `mc.catalogs.list_named_catalogs()` and `NamedCatalogs` static methods:

| Catalog | Purpose |
|---------|---------|
| `pains`, `pains_a/b/c` | PAINS substructure filters |
| `brenk` | Unwanted functional groups |
| `nih` | NIH screening filters |
| `zinc` | ZINC structural filters |
| `glaxo`, `dundee`, `bms` | Pharma-derived alert sets |
| `mlsmr`, `inpharmatica`, `lint` | Additional screening sets |
| `nibr` | NIBR catalog (substructure) |
| `bredt` | Bredt rule violations (unstable structures) |
| `tox`, `toxicophore`, `carcinogen` | Toxicity patterns |
| `reactive_unstable_toxic` | Reactive/unstable groups |
| `unstable_graph` | Unstable molecular graphs |

```python
cat = mc.catalogs.NamedCatalogs.brenk()
passes = mc.functional.catalog_filter(mols, catalogs=[cat], n_jobs=-1)
```

---

## Complexity Metrics

Compared to ZINC-15 percentile thresholds via `ComplexityFilter` or `complexity_filter()`:

| Metric | Description |
|--------|-------------|
| `bertz` | Bertz molecular complexity |
| `sas` | Synthetic accessibility score |
| `qed` | Quantitative Estimate of Drug-likeness |
| `clogp` | Calculated LogP |
| `whitlock` | Whitlock CT (rings, unsaturation, heteroatoms, chirality) |
| `barone` | Barone complexity |
| `smcm` | Synthetic complexity metric |
| `twc` | Total walk count |

```python
mc.functional.complexity_filter(mols, complexity_metric="bertz", limit="99", n_jobs=-1)
```

`limit="99"` keeps compounds below the 99th percentile on ZINC-15.

---

## Chemical Group Collections

Browse with `mc.groups.list_default_chemical_groups()`:

| Group | Application |
|-------|-------------|
| `privileged_scaffolds` | Common drug scaffolds |
| `common_warhead_covalent_inhibitors` | Covalent warhead patterns |
| `electrophilic_warheads_for_kinases` | Kinase covalent motifs |
| `rings_in_drugs` | Ring systems in approved drugs |
| `phase_2_hetereocyclic_rings` | Phase 2 heterocycles |
| `common_monomer_repeating_units` | Polymer/repeating units |
| `emerging_perfluoroalkyls` | PFAS-related patterns |

```python
group = mc.groups.ChemicalGroup(groups=["privileged_scaffolds"])
group.has_match(mol)
```

Custom groups: provide a CSV via `groups_db` with columns `smiles`/`smarts`, `name`, `group`.

---

## Filter Selection Guidelines

### Initial Screening (HTS deck)

```python
qf = mc.query.QueryFilter('MATCHRULE("rule_of_five") AND NOT HASALERT("pains")')
mask = qf(mols=mol_list, n_jobs=-1)
```

### Hit-to-Lead

```python
rules = mc.rules.RuleFilters(rule_list=["rule_of_oprea"])(mols, n_jobs=-1)
nibr = mc.structural.NIBRFilters()(mols, n_jobs=-1)
```

### Lead Optimization

```python
rules = mc.rules.RuleFilters(rule_list=["rule_of_druglike_soft"])(mols, n_jobs=-1)
alerts = mc.structural.CommonAlertsFilters()(mols, n_jobs=-1)
complexity = mc.functional.complexity_filter(mols, complexity_metric="bertz", limit="95", n_jobs=-1)
```

### CNS Targets

```python
qf = mc.query.QueryFilter('MATCHRULE("rule_of_cns") AND HASPROP("tpsa", <=, 90)')
mask = qf(mols, n_jobs=-1)
```

### Fragment-Based Discovery

```python
rules = mc.rules.RuleFilters(rule_list=["rule_of_three"])(mols, n_jobs=-1)
complexity = mc.functional.complexity_filter(mols, complexity_metric="bertz", limit="90", n_jobs=-1)
```

---

## Important Considerations

**Filters are guidelines, not absolutes:**
- ~10% of marketed oral drugs violate Ro5
- Natural products and prodrugs often fail standard rules
- Passing filters does not guarantee clinical success

**Combine with ML when appropriate:**

```python
rules_df = mc.rules.RuleFilters(rule_list=["rule_of_five"])(mols, n_jobs=-1)
filtered_mols = [m for m, ok in zip(mols, rules_df["pass_all"]) if ok]
# score filtered_mols with downstream ML model
```

---

## References

1. Lipinski CA et al. *Adv Drug Deliv Rev* (1997) 23:3–25
2. Veber DF et al. *J Med Chem* (2002) 45:2615–2623
3. Oprea TI et al. *J Chem Inf Comput Sci* (2001) 41:1308–1315
4. Congreve M et al. *Drug Discov Today* (2003) 8:876–877
5. Baell JB & Holloway GA. *J Med Chem* (2010) 53:2719–2740
6. Walters WP & Murcko MA. *Adv Drug Deliv Rev* (2002) 54:255–271
7. Schuffenhauer A et al. *J Med Chem* (2020) — NIBR screening deck
8. Doak BC et al. (2015) — Beyond Rule of Five

### `scripts/filter_molecules.py`

```python
#!/usr/bin/env python3
"""
Batch molecular filtering using the medchem library.

Usage:
    uv run python filter_molecules.py input.csv --rules rule_of_five,rule_of_cns --pains --output filtered.csv
    uv run python filter_molecules.py input.sdf --rules rule_of_veber --nibr --complexity 99 --output results.csv
    uv run python filter_molecules.py smiles.txt --query 'MATCHRULE("rule_of_five") AND NOT HASALERT("pains")' --output clean.csv
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Tuple

try:
    import pandas as pd
    import datamol as dm
    import medchem as mc
    from rdkit import Chem
    from tqdm import tqdm
except ImportError as e:
    print(f"Error: Missing required package: {e}")
    print("Install dependencies: uv pip install medchem datamol pandas tqdm")
    sys.exit(1)


def load_molecules(
    input_file: Path, smiles_column: str = "smiles"
) -> Tuple[pd.DataFrame, List[Chem.Mol]]:
    """Load molecules from CSV/TSV, SDF, or plain SMILES text files."""
    suffix = input_file.suffix.lower()

    if suffix == ".sdf":
        print(f"Loading SDF file: {input_file}")
        supplier = Chem.SDMolSupplier(str(input_file))
        mols = [mol for mol in supplier if mol is not None]
        data = []
        for mol in mols:
            props = mol.GetPropsAsDict()
            props["smiles"] = Chem.MolToSmiles(mol)
            data.append(props)
        df = pd.DataFrame(data)

    elif suffix in [".csv", ".tsv"]:
        print(f"Loading CSV/TSV file: {input_file}")
        sep = "\t" if suffix == ".tsv" else ","
        df = pd.read_csv(input_file, sep=sep)
        if smiles_column not in df.columns:
            print(f"Error: Column '{smiles_column}' not found")
            print(f"Available columns: {', '.join(df.columns)}")
            sys.exit(1)
        print("Converting SMILES to molecules...")
        mols = [dm.to_mol(smi) for smi in tqdm(df[smiles_column], desc="Parsing")]

    elif suffix == ".txt":
        print(f"Loading text file: {input_file}")
        with open(input_file) as f:
            smiles_list = [line.strip() for line in f if line.strip()]
        df = pd.DataFrame({"smiles": smiles_list})
        print("Converting SMILES to molecules...")
        mols = [dm.to_mol(smi) for smi in tqdm(smiles_list, desc="Parsing")]

    else:
        print(f"Error: Unsupported file format: {suffix}")
        print("Supported formats: .csv, .tsv, .sdf, .txt")
        sys.exit(1)

    valid_indices = [i for i, mol in enumerate(mols) if mol is not None]
    if len(valid_indices) < len(mols):
        n_invalid = len(mols) - len(valid_indices)
        print(f"Warning: {n_invalid} invalid molecules removed")
        df = df.iloc[valid_indices].reset_index(drop=True)
        mols = [mols[i] for i in valid_indices]

    print(f"Loaded {len(mols)} valid molecules")
    return df, mols


def apply_rule_filters(
    mols: List[Chem.Mol], rules: List[str], n_jobs: int
) -> pd.DataFrame:
    """Apply medicinal chemistry rule filters. Returns rule result columns."""
    print(f"\nApplying rule filters: {', '.join(rules)}")
    rfilter = mc.rules.RuleFilters(rule_list=rules)
    results = rfilter(mols=mols, n_jobs=n_jobs, progress=True)
    return results.drop(columns=["mol"], errors="ignore")


def apply_common_alerts(mols: List[Chem.Mol], n_jobs: int) -> pd.DataFrame:
    """Apply ChEMBL-derived common structural alerts."""
    print("\nApplying common structural alerts...")
    alert_filter = mc.structural.CommonAlertsFilters()
    results = alert_filter(mols=mols, n_jobs=n_jobs, progress=True)
    return results.drop(columns=["mol"], errors="ignore").rename(
        columns={"pass_filter": "passes_common_alerts", "status": "common_alert_status"}
    )


def apply_nibr(mols: List[Chem.Mol], n_jobs: int) -> pd.DataFrame:
    """Apply NIBR screening-deck filters."""
    print("\nApplying NIBR filters...")
    nibr_filter = mc.structural.NIBRFilters()
    results = nibr_filter(mols=mols, n_jobs=n_jobs, progress=True)
    return results.drop(columns=["mol"], errors="ignore").rename(
        columns={"pass_filter": "passes_nibr", "status": "nibr_status"}
    )


def apply_alert_catalog(
    mols: List[Chem.Mol], alerts: List[str], n_jobs: int
) -> pd.DataFrame:
    """Apply named alert catalogs (pains, brenk, etc.)."""
    print(f"\nApplying alert catalogs: {', '.join(alerts)}")
    for alert in alerts:
        passes = mc.functional.alert_filter(
            mols=mols, alerts=[alert], n_jobs=n_jobs, progress=True
        )
        yield alert, passes


def apply_lilly(mols: List[Chem.Mol], max_demerits: int, n_jobs: int) -> pd.DataFrame:
    """Apply Lilly demerit filter (requires lilly-medchem-rules)."""
    print(f"\nApplying Lilly demerits filter (max={max_demerits})...")
    try:
        passes = mc.functional.lilly_demerit_filter(
            mols=mols, max_demerits=max_demerits, n_jobs=n_jobs, progress=True
        )
    except ImportError as e:
        print(f"Warning: Lilly filter unavailable: {e}")
        print("Install with: mamba install -c conda-forge lilly-medchem-rules")
        return pd.DataFrame({"passes_lilly": [None] * len(mols)})
    return pd.DataFrame({"passes_lilly": passes})


def apply_complexity(
    mols: List[Chem.Mol], limit: str, method: str, n_jobs: int
) -> pd.DataFrame:
    """Filter by complexity percentile threshold."""
    print(f"\nApplying complexity filter (metric={method}, limit={limit} percentile)...")
    passes = mc.functional.complexity_filter(
        mols=mols,
        complexity_metric=method,
        limit=limit,
        n_jobs=n_jobs,
        progress=True,
    )
    return pd.DataFrame({f"passes_complexity_{method}": passes})


def apply_query(mols: List[Chem.Mol], query: str, n_jobs: int) -> pd.DataFrame:
    """Apply medchem query language filter."""
    print(f"\nApplying query: {query}")
    qf = mc.query.QueryFilter(query)
    passes = qf(mols=mols, n_jobs=n_jobs, progress=True)
    return pd.DataFrame({"passes_query": passes})


def apply_groups(mols: List[Chem.Mol], groups: List[str]) -> pd.DataFrame:
    """Detect chemical group matches."""
    print(f"\nDetecting chemical groups: {', '.join(groups)}")
    detector = mc.groups.ChemicalGroup(groups=groups)
    return pd.DataFrame(
        {f"has_{g}": [detector.has_match(mol) for mol in mols] for g in groups}
    )


def generate_summary(df: pd.DataFrame, output_file: Path) -> None:
    """Write a text summary of filtering results."""
    summary_file = output_file.parent / f"{output_file.stem}_summary.txt"
    pass_cols = [c for c in df.columns if c.startswith("passes_") or c == "pass_all"]

    with open(summary_file, "w") as f:
        f.write("=" * 80 + "\nMEDCHEM FILTERING SUMMARY\n" + "=" * 80 + "\n\n")
        f.write(f"Total molecules processed: {len(df)}\n\n")

        for col in pass_cols:
            if col in df.columns and df[col].dtype == bool:
                n_pass = df[col].sum()
                pct = 100 * n_pass / len(df) if len(df) else 0
                f.write(f"  {col}: {n_pass} passed ({pct:.1f}%)\n")

        if pass_cols:
            bool_cols = [c for c in pass_cols if c in df.columns and df[c].dtype == bool]
            if bool_cols:
                df["_passes_all"] = df[bool_cols].all(axis=1)
                n_all = df["_passes_all"].sum()
                pct = 100 * n_all / len(df) if len(df) else 0
                f.write(f"\n  All filters passed: {n_all} ({pct:.1f}%)\n")

        f.write("\n" + "=" * 80 + "\n")

    print(f"\nSummary report saved to: {summary_file}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch molecular filtering using medchem",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("input", type=Path, help="Input file (CSV, TSV, SDF, or TXT)")
    parser.add_argument("--output", "-o", type=Path, required=True, help="Output CSV file")
    parser.add_argument("--smiles-column", default="smiles", help="SMILES column name (default: smiles)")

    parser.add_argument("--rules", help="Comma-separated rules (e.g. rule_of_five,rule_of_cns)")
    parser.add_argument("--query", help='Medchem query string (e.g. MATCHRULE("rule_of_five") AND NOT HASALERT("pains"))')
    parser.add_argument("--common-alerts", action="store_true", help="Apply common structural alerts")
    parser.add_argument("--nibr", action="store_true", help="Apply NIBR filters")
    parser.add_argument("--lilly", action="store_true", help="Apply Lilly demerits (requires lilly-medchem-rules)")
    parser.add_argument("--lilly-max", type=int, default=160, help="Max Lilly demerits (default: 160)")
    parser.add_argument(
        "--alerts",
        help="Comma-separated alert catalogs (e.g. pains,brenk). Shorthand for --pains when set to pains",
    )
    parser.add_argument("--pains", action="store_true", help="Apply PAINS filter (alias for --alerts pains)")

    parser.add_argument(
        "--complexity",
        help="Complexity percentile limit (e.g. 99 keeps below 99th percentile on ZINC-15)",
    )
    parser.add_argument(
        "--complexity-method",
        default="bertz",
        choices=["bertz", "sas", "qed", "clogp", "whitlock", "barone", "smcm", "twc"],
        help="Complexity metric (default: bertz)",
    )
    parser.add_argument("--groups", help="Comma-separated chemical groups to detect")
    parser.add_argument("--n-jobs", type=int, default=-1, help="Parallel jobs (-1 = all cores)")
    parser.add_argument("--no-summary", action="store_true", help="Skip summary report")
    parser.add_argument("--filter-output", action="store_true", help="Only output molecules passing all filters")

    args = parser.parse_args()

    if not any([args.rules, args.query, args.common_alerts, args.nibr, args.lilly,
                args.pains, args.alerts, args.complexity, args.groups]):
        print("Error: Specify at least one filter (--rules, --query, --pains, --nibr, etc.)")
        sys.exit(1)

    df, mols = load_molecules(args.input, args.smiles_column)
    result_parts = [df.reset_index(drop=True)]

    if args.rules:
        rule_list = [r.strip() for r in args.rules.split(",")]
        unknown = set(rule_list) - set(mc.rules.RuleFilters.list_available_rules_names())
        if unknown:
            print(f"Warning: Unknown rules (will error at runtime): {', '.join(sorted(unknown))}")
        result_parts.append(apply_rule_filters(mols, rule_list, args.n_jobs))

    if args.query:
        result_parts.append(apply_query(mols, args.query, args.n_jobs))

    if args.common_alerts:
        result_parts.append(apply_common_alerts(mols, args.n_jobs))

    if args.nibr:
        result_parts.append(apply_nibr(mols, args.n_jobs))

    if args.lilly:
        result_parts.append(apply_lilly(mols, args.lilly_max, args.n_jobs))

    alert_list = []
    if args.pains:
        alert_list.append("pains")
    if args.alerts:
        alert_list.extend(a.strip() for a in args.alerts.split(","))
    for alert in dict.fromkeys(alert_list):
        col_name = f"passes_{alert}"
        _, passes = next(apply_alert_catalog(mols, [alert], args.n_jobs))
        result_parts.append(pd.DataFrame({col_name: passes}))

    if args.complexity:
        result_parts.append(
            apply_complexity(mols, args.complexity, args.complexity_method, args.n_jobs)
        )

    if args.groups:
        group_list = [g.strip() for g in args.groups.split(",")]
        result_parts.append(apply_groups(mols, group_list))

    df_final = pd.concat(result_parts, axis=1)

    if args.filter_output:
        pass_cols = [c for c in df_final.columns if c.startswith("passes_") or c == "pass_all"]
        bool_cols = [c for c in pass_cols if c in df_final.columns and df_final[c].dtype == bool]
        if bool_cols:
            mask = df_final[bool_cols].all(axis=1)
            df_final = df_final[mask]
            print(f"\nFiltered to {len(df_final)} molecules passing all filters")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    df_final.to_csv(args.output, index=False)
    print(f"\nResults saved to: {args.output}")

    if not args.no_summary:
        generate_summary(df_final, args.output)

    print("\nDone!")


if __name__ == "__main__":
    main()
```
