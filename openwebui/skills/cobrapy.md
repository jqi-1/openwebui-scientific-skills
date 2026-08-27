---
name: cobrapy
description: Constraint-based metabolic modeling (COBRA). FBA, FVA, gene knockouts, flux sampling, SBML models, for systems biology and metabolic engineering analysis.
---

# COBRApy - Constraint-Based Reconstruction and Analysis

## Overview

COBRApy is a Python library for constraint-based reconstruction and analysis (COBRA) of metabolic models, essential for systems biology research. Work with genome-scale metabolic models, perform computational simulations of cellular metabolism, conduct metabolic engineering analyses, and predict phenotypic behaviors.

**Version note:** Examples target **cobra 0.31.1** on PyPI (import `cobra`). Docs: [cobrapy.readthedocs.io](https://cobrapy.readthedocs.io/en/latest/). Repo: [opencobra/cobrapy](https://github.com/opencobra/cobrapy).

## When to Use This Skill

Use this skill when:
- Loading, building, or exporting genome-scale metabolic models (SBML, JSON, YAML)
- Running FBA, pFBA, FVA, or flux sampling on COBRA models
- Performing gene or reaction knockout screens and production envelope analysis
- Designing or optimizing growth media and exchange constraints
- Gap-filling infeasible models or validating model consistency

## Installation

```bash
uv pip install "cobra==0.31.1"
```

MATLAB model I/O (optional):

```bash
uv pip install "cobra[array]==0.31.1"
```

COBRApy uses [optlang](https://optlang.readthedocs.io/) for solvers. GLPK installs automatically via `swiglpk`. For large MILPs/QPs, cobra 0.29+ adds a **hybrid** solver (HIGHS/OSQP); `model.solver = "osqp"` now routes through hybrid and may error on plain LPs in a future release—prefer `model.solver = "hybrid"` when available.

## Core Capabilities

COBRApy provides comprehensive tools organized into several key areas:

### 1. Model Management

Load existing models from repositories or files:
```python
from cobra.io import load_model

# Bundled locally (no network): textbook, iJO1366, salmonella
model = load_model("textbook")      # alias for e_coli_core (95 reactions)
model = load_model("e_coli_core")   # same core E. coli model
model = load_model("iJO1366")       # genome-scale E. coli (bundled)
model = load_model("salmonella")    # Salmonella iYS1720 (bundled)

# Remote (BiGG / BioModels; requires network, cached after first fetch)
model = load_model("iML1515")       # E. coli genome-scale on BiGG

# Load from files
from cobra.io import read_sbml_model, load_json_model, load_yaml_model
model = read_sbml_model("path/to/model.xml")
model = load_json_model("path/to/model.json")
model = load_yaml_model("path/to/model.yml")
```

Save models in various formats:
```python
from cobra.io import write_sbml_model, save_json_model, save_yaml_model
write_sbml_model(model, "output.xml")  # Preferred format
save_json_model(model, "output.json")  # For Escher compatibility
save_yaml_model(model, "output.yml")   # Human-readable
```

### 2. Model Structure and Components

Access and inspect model components:
```python
# Access components
model.reactions      # DictList of all reactions
model.metabolites    # DictList of all metabolites
model.genes          # DictList of all genes

# Get specific items by ID or index
reaction = model.reactions.get_by_id("PFK")
metabolite = model.metabolites[0]

# Inspect properties
print(reaction.reaction)        # Stoichiometric equation
print(reaction.bounds)          # Flux constraints
print(reaction.gene_reaction_rule)  # GPR logic
print(metabolite.formula)       # Chemical formula
print(metabolite.compartment)   # Cellular location
```

### 3. Flux Balance Analysis (FBA)

Perform standard FBA simulation:
```python
# Basic optimization
solution = model.optimize()
print(f"Objective value: {solution.objective_value}")
print(f"Status: {solution.status}")

# Access fluxes
print(solution.fluxes["PFK"])
print(solution.fluxes.head())

# Fast optimization (objective value only)
objective_value = model.slim_optimize()

# Change objective
model.objective = "ATPM"
solution = model.optimize()
```

Parsimonious FBA (minimize total flux):
```python
from cobra.flux_analysis import pfba
solution = pfba(model)
```

Geometric FBA (find central solution):
```python
from cobra.flux_analysis import geometric_fba
solution = geometric_fba(model)
```

### 4. Flux Variability Analysis (FVA)

Determine flux ranges for all reactions:
```python
from cobra.flux_analysis import flux_variability_analysis

# Standard FVA
fva_result = flux_variability_analysis(model)

# FVA at 90% optimality
fva_result = flux_variability_analysis(model, fraction_of_optimum=0.9)

# Loopless FVA (eliminates thermodynamically infeasible loops)
fva_result = flux_variability_analysis(model, loopless=True)

# FVA for specific reactions
fva_result = flux_variability_analysis(
    model,
    reaction_list=["PFK", "FBA", "PGI"]
)
```

### 5. Gene and Reaction Deletion Studies

Perform knockout analyses:
```python
from cobra.flux_analysis import (
    single_gene_deletion,
    single_reaction_deletion,
    double_gene_deletion,
    double_reaction_deletion
)

# Single deletions
gene_results = single_gene_deletion(model)
reaction_results = single_reaction_deletion(model)

# Double deletions (uses multiprocessing)
double_gene_results = double_gene_deletion(
    model,
    processes=4  # Number of CPU cores
)

# Manual knockout using context manager
with model:
    model.genes.get_by_id("b0008").knock_out()
    solution = model.optimize()
    print(f"Growth after knockout: {solution.objective_value}")
# Model automatically reverts after context exit
```

### 6. Growth Media and Minimal Media

Manage growth medium:
```python
# View current medium
print(model.medium)

# Modify medium (must reassign entire dict)
medium = model.medium
medium["EX_glc__D_e"] = 10.0  # Set glucose uptake
medium["EX_o2_e"] = 0.0       # Anaerobic conditions
model.medium = medium

# Calculate minimal media
from cobra.medium import minimal_medium

# Minimize total import flux
min_medium = minimal_medium(model, minimize_components=False)

# Minimize number of components (uses MILP, slower)
min_medium = minimal_medium(
    model,
    minimize_components=True,
    open_exchanges=True
)
```

### 7. Flux Sampling

Sample the feasible flux space:
```python
from cobra.sampling import sample

# Sample using OptGP (default, supports parallel processing)
samples = sample(model, n=1000, method="optgp", processes=4)

# Sample using ACHR
samples = sample(model, n=1000, method="achr")

# Validate samples
from cobra.sampling import OptGPSampler
sampler = OptGPSampler(model, processes=4)
sampler.sample(1000)
validation = sampler.validate(sampler.samples)
print(validation.value_counts())  # Should be all 'v' for valid
```

### 8. Production Envelopes

Calculate phenotype phase planes:
```python
from cobra.flux_analysis import production_envelope

# Standard production envelope
envelope = production_envelope(
    model,
    reactions=["EX_glc__D_e", "EX_o2_e"],
    objective="EX_ac_e"  # Acetate production
)

# With carbon yield
envelope = production_envelope(
    model,
    reactions=["EX_glc__D_e", "EX_o2_e"],
    carbon_sources="EX_glc__D_e"
)

# Visualize (use matplotlib or pandas plotting)
import matplotlib.pyplot as plt
envelope.plot(x="EX_glc__D_e", y="EX_o2_e", kind="scatter")
plt.show()
```

### 9. Gapfilling

Add reactions to make models feasible:
```python
from cobra.flux_analysis import gapfill

# Provide a universal reaction database (SBML/JSON); not bundled in cobra 0.31+
from cobra.io import read_sbml_model
universal = read_sbml_model("path/to/universal_reactions.xml")

# Perform gapfilling
with model:
    # Remove reactions to create gaps for demonstration
    model.remove_reactions([model.reactions.PGI])

    # Find reactions needed
    solution = gapfill(model, universal)
    print(f"Reactions to add: {solution}")
```

### 10. Model Building

Build models from scratch:
```python
from cobra import Model, Reaction, Metabolite

# Create model
model = Model("my_model")

# Create metabolites
atp_c = Metabolite("atp_c", formula="C10H12N5O13P3",
                   name="ATP", compartment="c")
adp_c = Metabolite("adp_c", formula="C10H12N5O10P2",
                   name="ADP", compartment="c")
pi_c = Metabolite("pi_c", formula="HO4P",
                  name="Phosphate", compartment="c")

# Create reaction
reaction = Reaction("ATPASE")
reaction.name = "ATP hydrolysis"
reaction.subsystem = "Energy"
reaction.lower_bound = 0.0
reaction.upper_bound = 1000.0

# Add metabolites with stoichiometry
reaction.add_metabolites({
    atp_c: -1.0,
    adp_c: 1.0,
    pi_c: 1.0
})

# Add gene-reaction rule
reaction.gene_reaction_rule = "(gene1 and gene2) or gene3"

# Add to model
model.add_reactions([reaction])

# Add boundary reactions
model.add_boundary(atp_c, type="exchange")
model.add_boundary(adp_c, type="demand")

# Set objective
model.objective = "ATPASE"
```

## Common Workflows

### Workflow 1: Load Model and Predict Growth

```python
from cobra.io import load_model

# Load model (textbook = fast tutorial; iJO1366 / iML1515 for genome-scale)
model = load_model("textbook")

# Run FBA
solution = model.optimize()
print(f"Growth rate: {solution.objective_value:.3f} /h")

# Show active pathways
print(solution.fluxes[solution.fluxes.abs() > 1e-6])
```

### Workflow 2: Gene Knockout Screen

```python
from cobra.io import load_model
from cobra.flux_analysis import single_gene_deletion

# Load model
model = load_model("textbook")
baseline = model.slim_optimize()

# Perform single gene deletions
results = single_gene_deletion(model)

# Find essential genes (growth < threshold)
essential_genes = results[results["growth"] < 0.01]
print(f"Found {len(essential_genes)} essential genes")

# Find genes with minimal impact
neutral_genes = results[results["growth"] > 0.9 * baseline]
```

### Workflow 3: Media Optimization

```python
from cobra.io import load_model
from cobra.medium import minimal_medium

# Load model
model = load_model("textbook")

# Calculate minimal medium for 50% of max growth
target_growth = model.slim_optimize() * 0.5
min_medium = minimal_medium(
    model,
    target_growth,
    minimize_components=True
)

print(f"Minimal medium components: {len(min_medium)}")
print(min_medium)
```

### Workflow 4: Flux Uncertainty Analysis

```python
from cobra.io import load_model
from cobra.flux_analysis import flux_variability_analysis
from cobra.sampling import sample

# Load model
model = load_model("textbook")

# First check flux ranges at optimality
fva = flux_variability_analysis(model, fraction_of_optimum=1.0)

# For reactions with large ranges, sample to understand distribution
samples = sample(model, n=1000)

# Analyze specific reaction
reaction_id = "PFK"
import matplotlib.pyplot as plt
samples[reaction_id].hist(bins=50)
plt.xlabel(f"Flux through {reaction_id}")
plt.ylabel("Frequency")
plt.show()
```

### Workflow 5: Context Manager for Temporary Changes

Use context managers to make temporary modifications:
```python
# Model remains unchanged outside context
with model:
    # Temporarily change objective
    model.objective = "ATPM"

    # Temporarily modify bounds
    model.reactions.EX_glc__D_e.lower_bound = -5.0

    # Temporarily knock out genes
    model.genes.b0008.knock_out()

    # Optimize with changes
    solution = model.optimize()
    print(f"Modified growth: {solution.objective_value}")

# All changes automatically reverted
solution = model.optimize()
print(f"Original growth: {solution.objective_value}")
```

## Key Concepts

### DictList Objects
Models use `DictList` objects for reactions, metabolites, and genes - behaving like both lists and dictionaries:
```python
# Access by index
first_reaction = model.reactions[0]

# Access by ID
pfk = model.reactions.get_by_id("PFK")

# Query methods
atp_reactions = model.reactions.query("atp")
```

### Flux Constraints
Reaction bounds define feasible flux ranges:
- **Irreversible**: `lower_bound = 0, upper_bound > 0`
- **Reversible**: `lower_bound < 0, upper_bound > 0`
- Set both bounds simultaneously with `.bounds` to avoid inconsistencies

### Gene-Reaction Rules (GPR)
Boolean logic linking genes to reactions:
```python
# AND logic (both required)
reaction.gene_reaction_rule = "gene1 and gene2"

# OR logic (either sufficient)
reaction.gene_reaction_rule = "gene1 or gene2"

# Complex logic
reaction.gene_reaction_rule = "(gene1 and gene2) or (gene3 and gene4)"
```

### Exchange Reactions
Special reactions representing metabolite import/export:
- Named with prefix `EX_` by convention
- Positive flux = secretion, negative flux = uptake
- Managed through `model.medium` dictionary

## Best Practices

1. **Use context managers** for temporary modifications to avoid state management issues
2. **Validate models** before analysis using `model.slim_optimize()` to ensure feasibility
3. **Check solution status** after optimization - `optimal` indicates successful solve
4. **Use loopless FVA** when thermodynamic feasibility matters
5. **Set fraction_of_optimum** appropriately in FVA to explore suboptimal space
6. **Parallelize** computationally expensive operations (sampling, double deletions) — start with small `n` and `processes=1` on genome-scale models
7. **Prefer SBML format** for model exchange and long-term storage
8. **Use slim_optimize()** when only objective value needed for performance
9. **Validate flux samples** to ensure numerical stability
10. **Confirm output paths** before writing CSV/PNG files from workflow examples

## Troubleshooting

**Infeasible solutions**: Check medium constraints, reaction bounds, and model consistency
**Slow optimization**: Try different solvers (GLPK, CPLEX, Gurobi) via `model.solver`
**Unbounded solutions**: Verify exchange reactions have appropriate upper bounds
**Import errors**: Ensure correct file format and valid SBML identifiers

## References

For detailed workflows and API patterns, refer to:
- `references/workflows.md` - Comprehensive step-by-step workflow examples
- `references/api_quick_reference.md` - Common function signatures and patterns

Official documentation: https://cobrapy.readthedocs.io/en/latest/

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/cobrapy/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/api_quick_reference.md`

# COBRApy API Quick Reference

Quick reference for **cobra 0.31.1**. Full API: https://cobrapy.readthedocs.io/

## Model I/O

### Loading Models

```python
from cobra.io import load_model, read_sbml_model, load_json_model, load_yaml_model, load_matlab_model

# Bundled locally (cobra.data): textbook, iJO1366, salmonella
model = load_model("textbook")      # e_coli_core (95 reactions)
model = load_model("e_coli_core")   # same as textbook
model = load_model("iJO1366")       # genome-scale E. coli
model = load_model("salmonella")    # iYS1720

# BiGG / BioModels (network + disk cache)
model = load_model("iML1515")

# From files
model = read_sbml_model(filename, f_replace={}, **kwargs)
model = load_json_model(filename)
model = load_yaml_model(filename)
model = load_matlab_model(filename, variable_name=None)
```

### Saving Models

```python
from cobra.io import write_sbml_model, save_json_model, save_yaml_model, save_matlab_model

write_sbml_model(model, filename, f_replace={}, **kwargs)
save_json_model(model, filename, pretty=False, **kwargs)
save_yaml_model(model, filename, **kwargs)
save_matlab_model(model, filename, **kwargs)
```

## Model Structure

### Core Classes

```python
from cobra import Model, Reaction, Metabolite, Gene

# Create model
model = Model(id_or_model=None, name=None)

# Create metabolite
metabolite = Metabolite(
    id=None,
    formula=None,
    name="",
    charge=None,
    compartment=None
)

# Create reaction
reaction = Reaction(
    id=None,
    name="",
    subsystem="",
    lower_bound=0.0,
    upper_bound=None
)

# Create gene
gene = Gene(id=None, name="", functional=True)
```

### Model Attributes

```python
# Component access (DictList objects)
model.reactions       # DictList of Reaction objects
model.metabolites     # DictList of Metabolite objects
model.genes          # DictList of Gene objects

# Special reaction lists
model.exchanges      # Exchange reactions (external transport)
model.demands        # Demand reactions (metabolite sinks)
model.sinks          # Sink reactions
model.boundary       # All boundary reactions

# Model properties
model.objective      # Current objective (read/write)
model.objective_direction  # "max" or "min"
model.medium         # Growth medium (dict of exchange: bound)
model.solver         # Optimization solver
```

### DictList Methods

```python
# Access by index
item = model.reactions[0]

# Access by ID
item = model.reactions.get_by_id("PFK")

# Query by string (substring match)
items = model.reactions.query("atp")      # Case-insensitive search
items = model.reactions.query(lambda x: x.subsystem == "Glycolysis")

# List comprehension
items = [r for r in model.reactions if r.lower_bound < 0]

# Check membership
"PFK" in model.reactions
```

## Optimization

### Basic Optimization

```python
# Full optimization (returns Solution object)
solution = model.optimize()

# Attributes of Solution
solution.objective_value   # Objective function value
solution.status           # Optimization status ("optimal", "infeasible", etc.)
solution.fluxes          # Pandas Series of reaction fluxes
solution.shadow_prices   # Pandas Series of metabolite shadow prices
solution.reduced_costs   # Pandas Series of reduced costs

# Fast optimization (returns float only)
objective_value = model.slim_optimize()

# Change objective
model.objective = "ATPM"
model.objective = model.reactions.ATPM
model.objective = {model.reactions.ATPM: 1.0}

# Change optimization direction
model.objective_direction = "max"  # or "min"
```

### Solver Configuration

```python
# Check available solvers
from cobra.util.solver import solvers
print(solvers)  # typically includes glpk; CPLEX/Gurobi if installed

# Change solver
model.solver = "glpk"  # default via swiglpk
# model.solver = "hybrid"   # HIGHS/OSQP for large MILPs/QPs (0.29+)
# model.solver = "cplex"    # or "gurobi" with licenses installed

# OSQP: deprecated as standalone LP solver; routes through hybrid in 0.29+

# Solver-specific configuration
model.solver.configuration.timeout = 60  # seconds
model.solver.configuration.verbosity = 1
model.solver.configuration.tolerances.feasibility = 1e-9
```

## Flux Analysis

### Flux Balance Analysis (FBA)

```python
from cobra.flux_analysis import pfba, geometric_fba

# Parsimonious FBA
solution = pfba(model, fraction_of_optimum=1.0, **kwargs)

# Geometric FBA
solution = geometric_fba(model, epsilon=1e-06, max_tries=200)
```

### Flux Variability Analysis (FVA)

```python
from cobra.flux_analysis import flux_variability_analysis

fva_result = flux_variability_analysis(
    model,
    reaction_list=None,        # List of reaction IDs or None for all
    loopless=False,            # Eliminate thermodynamically infeasible loops
    fraction_of_optimum=1.0,   # Optimality fraction (0.0-1.0)
    pfba_factor=None,          # Optional pFBA constraint
    processes=1                # Number of parallel processes
)

# Returns DataFrame with columns: minimum, maximum
```

### Gene and Reaction Deletions

```python
from cobra.flux_analysis import (
    single_gene_deletion,
    single_reaction_deletion,
    double_gene_deletion,
    double_reaction_deletion
)

# Single deletions
results = single_gene_deletion(
    model,
    gene_list=None,     # None for all genes
    processes=1,
    **kwargs
)

results = single_reaction_deletion(
    model,
    reaction_list=None,  # None for all reactions
    processes=1,
    **kwargs
)

# Double deletions
results = double_gene_deletion(
    model,
    gene_list1=None,
    gene_list2=None,
    processes=1,
    **kwargs
)

results = double_reaction_deletion(
    model,
    reaction_list1=None,
    reaction_list2=None,
    processes=1,
    **kwargs
)

# Returns DataFrame with columns: ids, growth, status
# For double deletions, index is MultiIndex of gene/reaction pairs
```

### Flux Sampling

```python
from cobra.sampling import sample, OptGPSampler, ACHRSampler

# Simple interface
samples = sample(
    model,
    n,                  # Number of samples
    method="optgp",     # or "achr"
    thinning=100,       # Thinning factor (sample every n iterations)
    processes=1,        # Parallel processes (OptGP only)
    seed=None          # Random seed
)

# Advanced interface with sampler objects
sampler = OptGPSampler(model, processes=4, thinning=100)
sampler = ACHRSampler(model, thinning=100)

# Generate samples
samples = sampler.sample(n)

# Validate samples
validation = sampler.validate(sampler.samples)
# Returns array of 'v' (valid), 'l' (lower bound violation),
# 'u' (upper bound violation), 'e' (equality violation)

# Batch sampling
sampler.batch(n_samples, n_batches)
```

### Production Envelopes

```python
from cobra.flux_analysis import production_envelope

envelope = production_envelope(
    model,
    reactions,              # List of 1-2 reaction IDs
    objective=None,         # Objective reaction ID (None uses model objective)
    carbon_sources=None,    # Carbon source for yield calculation
    points=20,              # Number of points to calculate
    threshold=0.01          # Minimum objective value threshold
)

# Returns DataFrame with columns:
# - First reaction flux
# - Second reaction flux (if provided)
# - objective_minimum, objective_maximum
# - carbon_yield_minimum, carbon_yield_maximum (if carbon source specified)
# - mass_yield_minimum, mass_yield_maximum
```

### Gapfilling

```python
from cobra.flux_analysis import gapfill

# Basic gapfilling
solution = gapfill(
    model,
    universal=None,         # Universal model with candidate reactions
    lower_bound=0.05,       # Minimum objective flux
    penalties=None,         # Dict of reaction: penalty
    demand_reactions=True,  # Add demand reactions if needed
    exchange_reactions=False,
    iterations=1
)

# Returns list of Reaction objects to add

# Multiple solutions
solutions = []
for i in range(5):
    sol = gapfill(model, universal, iterations=1)
    solutions.append(sol)
    # Prevent finding same solution by increasing penalties
```

### Other Analysis Methods

```python
from cobra.flux_analysis import (
    find_blocked_reactions,
    find_essential_genes,
    find_essential_reactions
)

# Blocked reactions (cannot carry flux)
blocked = find_blocked_reactions(
    model,
    reaction_list=None,
    zero_cutoff=1e-9,
    open_exchanges=False
)

# Essential genes/reactions
essential_genes = find_essential_genes(model, threshold=0.01)
essential_reactions = find_essential_reactions(model, threshold=0.01)
```

## Media and Boundary Conditions

### Medium Management

```python
# Get current medium (returns dict)
medium = model.medium

# Set medium (must reassign entire dict)
medium = model.medium
medium["EX_glc__D_e"] = 10.0
medium["EX_o2_e"] = 20.0
model.medium = medium

# Alternative: individual modification
with model:
    model.reactions.EX_glc__D_e.lower_bound = -10.0
```

### Minimal Media

```python
from cobra.medium import minimal_medium

min_medium = minimal_medium(
    model,
    min_objective_value=0.1,  # Minimum growth rate
    minimize_components=False, # If True, uses MILP (slower)
    open_exchanges=False,      # Open all exchanges before optimization
    exports=False,             # Allow metabolite export
    penalties=None             # Dict of exchange: penalty
)

# Returns Series of exchange reactions with fluxes
```

### Boundary Reactions

```python
# Add boundary reaction
model.add_boundary(
    metabolite,
    type="exchange",    # or "demand", "sink"
    reaction_id=None,   # Auto-generated if None
    lb=None,
    ub=None,
    sbo_term=None
)

# Access boundary reactions
exchanges = model.exchanges     # System boundary
demands = model.demands         # Intracellular removal
sinks = model.sinks            # Intracellular exchange
boundaries = model.boundary    # All boundary reactions
```

## Model Manipulation

### Adding Components

```python
# Add reactions
model.add_reactions([reaction1, reaction2, ...])
model.add_reaction(reaction)

# Add metabolites
reaction.add_metabolites({
    metabolite1: -1.0,  # Consumed (negative stoichiometry)
    metabolite2: 1.0    # Produced (positive stoichiometry)
})

# Add metabolites to model
model.add_metabolites([metabolite1, metabolite2, ...])

# Add genes (usually automatic via gene_reaction_rule)
model.genes += [gene1, gene2, ...]
```

### Removing Components

```python
# Remove reactions
model.remove_reactions([reaction1, reaction2, ...])
model.remove_reactions(["PFK", "FBA"])

# Remove metabolites (removes from reactions too)
model.remove_metabolites([metabolite1, metabolite2, ...])

# Remove genes (usually via gene_reaction_rule)
model.genes.remove(gene)
```

### Modifying Reactions

```python
# Set bounds
reaction.bounds = (lower, upper)
reaction.lower_bound = 0.0
reaction.upper_bound = 1000.0

# Modify stoichiometry
reaction.add_metabolites({metabolite: 1.0})
reaction.subtract_metabolites({metabolite: 1.0})

# Change gene-reaction rule
reaction.gene_reaction_rule = "(gene1 and gene2) or gene3"

# Knock out
reaction.knock_out()
gene.knock_out()
```

### Model Copying

```python
# Deep copy (independent model)
model_copy = model.copy()

# Copy specific reactions
new_model = Model("subset")
reactions_to_copy = [model.reactions.PFK, model.reactions.FBA]
new_model.add_reactions(reactions_to_copy)
```

## Context Management

Use context managers for temporary modifications:

```python
# Changes automatically revert after with block
with model:
    model.objective = "ATPM"
    model.reactions.EX_glc__D_e.lower_bound = -5.0
    model.genes.b0008.knock_out()
    solution = model.optimize()

# Model state restored here

# Multiple nested contexts
with model:
    model.objective = "ATPM"
    with model:
        model.genes.b0008.knock_out()
        # Both modifications active
    # Only objective change active

# Context management with reactions
with model:
    model.reactions.PFK.knock_out()
    # Equivalent to: reaction.lower_bound = reaction.upper_bound = 0
```

## Reaction and Metabolite Properties

### Reaction Attributes

```python
reaction.id                      # Unique identifier
reaction.name                    # Human-readable name
reaction.subsystem               # Pathway/subsystem
reaction.bounds                  # (lower_bound, upper_bound)
reaction.lower_bound
reaction.upper_bound
reaction.reversibility          # Boolean (lower_bound < 0)
reaction.gene_reaction_rule     # GPR string
reaction.genes                  # Set of associated Gene objects
reaction.metabolites            # Dict of {metabolite: stoichiometry}

# Methods
reaction.reaction               # Stoichiometric equation string
reaction.build_reaction_string() # Same as above
reaction.check_mass_balance()   # Returns imbalances or empty dict
reaction.get_coefficient(metabolite_id)
reaction.add_metabolites({metabolite: coeff})
reaction.subtract_metabolites({metabolite: coeff})
reaction.knock_out()
```

### Metabolite Attributes

```python
metabolite.id                   # Unique identifier
metabolite.name                 # Human-readable name
metabolite.formula              # Chemical formula
metabolite.charge               # Charge
metabolite.compartment          # Compartment ID
metabolite.reactions            # FrozenSet of associated reactions

# Methods
metabolite.summary()            # Print production/consumption
metabolite.copy()
```

### Gene Attributes

```python
gene.id                         # Unique identifier
gene.name                       # Human-readable name
gene.functional                 # Boolean activity status
gene.reactions                  # FrozenSet of associated reactions

# Methods
gene.knock_out()
```

## Model Validation

### Consistency Checking

```python
from cobra.manipulation import check_mass_balance, check_metabolite_compartment_formula

# Check all reactions for mass balance
unbalanced = {}
for reaction in model.reactions:
    balance = reaction.check_mass_balance()
    if balance:
        unbalanced[reaction.id] = balance

# Check metabolite formulas are valid
check_metabolite_compartment_formula(model)
```

### Model Statistics

```python
# Basic stats
print(f"Reactions: {len(model.reactions)}")
print(f"Metabolites: {len(model.metabolites)}")
print(f"Genes: {len(model.genes)}")

# Advanced stats
print(f"Exchanges: {len(model.exchanges)}")
print(f"Demands: {len(model.demands)}")

# Blocked reactions
from cobra.flux_analysis import find_blocked_reactions
blocked = find_blocked_reactions(model)
print(f"Blocked reactions: {len(blocked)}")

# Essential genes
from cobra.flux_analysis import find_essential_genes
essential = find_essential_genes(model)
print(f"Essential genes: {len(essential)}")
```

## Summary Methods

```python
# Model summary
model.summary()                  # Overall model info

# Metabolite summary
model.metabolites.atp_c.summary()

# Reaction summary
model.reactions.PFK.summary()

# Summary with FVA
model.summary(fva=0.95)         # Include FVA at 95% optimality
```

## Common Patterns

### Batch Analysis Pattern

```python
results = []
for condition in conditions:
    with model:
        # Apply condition
        setup_condition(model, condition)

        # Analyze
        solution = model.optimize()

        # Store result
        results.append({
            "condition": condition,
            "growth": solution.objective_value,
            "status": solution.status
        })

df = pd.DataFrame(results)
```

### Systematic Knockout Pattern

```python
knockout_results = []
for gene in model.genes:
    with model:
        gene.knock_out()

        solution = model.optimize()

        knockout_results.append({
            "gene": gene.id,
            "growth": solution.objective_value if solution.status == "optimal" else 0,
            "status": solution.status
        })

df = pd.DataFrame(knockout_results)
```

### Parameter Scan Pattern

```python
parameter_values = np.linspace(0, 20, 21)
results = []

for value in parameter_values:
    with model:
        model.reactions.EX_glc__D_e.lower_bound = -value

        solution = model.optimize()

        results.append({
            "glucose_uptake": value,
            "growth": solution.objective_value,
            "acetate_secretion": solution.fluxes["EX_ac_e"]
        })

df = pd.DataFrame(results)
```

This quick reference covers the most commonly used COBRApy functions and patterns. For complete API documentation, see https://cobrapy.readthedocs.io/en/latest/

**File outputs:** Workflow examples that call `to_csv` or `savefig` should use a user-approved `OUTDIR` — see `references/workflows.md`.

### `references/workflows.md`

# COBRApy Comprehensive Workflows

This document provides detailed step-by-step workflows for common COBRApy tasks in metabolic modeling.

**Operational notes (cobra 0.31.1):**
- Confirm with the user before writing CSV/PNG files; set `OUTDIR` to a user-approved path.
- `load_model("ecoli")` and `load_model("universal")` no longer work — use `textbook` / `e_coli_core`, `iJO1366`, or BiGG IDs such as `iML1515`.
- Double deletions, loopless FVA, and large sampling runs can take hours on genome-scale models — use `textbook` for exploration, lower `n`/`processes`, or subset `gene_list1`.

```python
OUTDIR = "cobrapy_output"  # set with user approval before running workflows
```

## Workflow 1: Complete Knockout Study with Visualization

This workflow demonstrates how to perform a comprehensive gene knockout study and visualize the results.

```python
import pandas as pd
import matplotlib.pyplot as plt
from cobra.io import load_model
from cobra.flux_analysis import single_gene_deletion, double_gene_deletion

# Step 1: Load model (textbook = core tutorial; use iJO1366 for genome-scale)
model = load_model("textbook")
print(f"Loaded model: {model.id}")
print(f"Model contains {len(model.reactions)} reactions, {len(model.metabolites)} metabolites, {len(model.genes)} genes")

# Step 2: Get baseline growth rate
baseline = model.slim_optimize()
print(f"Baseline growth rate: {baseline:.3f} /h")

# Step 3: Perform single gene deletions
print("Performing single gene deletions...")
single_results = single_gene_deletion(model)

# Step 4: Classify genes by impact
essential_genes = single_results[single_results["growth"] < 0.01]
severely_impaired = single_results[(single_results["growth"] >= 0.01) &
                                   (single_results["growth"] < 0.5 * baseline)]
moderately_impaired = single_results[(single_results["growth"] >= 0.5 * baseline) &
                                     (single_results["growth"] < 0.9 * baseline)]
neutral_genes = single_results[single_results["growth"] >= 0.9 * baseline]

print(f"\nSingle Deletion Results:")
print(f"  Essential genes: {len(essential_genes)}")
print(f"  Severely impaired: {len(severely_impaired)}")
print(f"  Moderately impaired: {len(moderately_impaired)}")
print(f"  Neutral genes: {len(neutral_genes)}")

# Step 5: Visualize distribution
fig, ax = plt.subplots(figsize=(10, 6))
single_results["growth"].hist(bins=50, ax=ax)
ax.axvline(baseline, color='r', linestyle='--', label='Baseline')
ax.set_xlabel("Growth rate (/h)")
ax.set_ylabel("Number of genes")
ax.set_title("Distribution of Growth Rates After Single Gene Deletions")
ax.legend()
plt.tight_layout()
plt.savefig(f"{OUTDIR}/single_deletion_distribution.png", dpi=300)

# Step 6: Identify gene pairs for double deletions
# Focus on non-essential genes to find synthetic lethals
target_genes = single_results[single_results["growth"] >= 0.5 * baseline].index.tolist()
target_genes = [list(gene)[0] for gene in target_genes[:50]]  # Limit for performance

print(f"\nPerforming double deletions on {len(target_genes)} genes...")
# Double deletions scale poorly — use processes=1 on large models unless user approves
double_results = double_gene_deletion(
    model,
    gene_list1=target_genes,
    processes=1
)

# Step 7: Find synthetic lethal pairs
synthetic_lethals = double_results[
    (double_results["growth"] < 0.01) &
    (single_results.loc[double_results.index.get_level_values(0)]["growth"].values >= 0.5 * baseline) &
    (single_results.loc[double_results.index.get_level_values(1)]["growth"].values >= 0.5 * baseline)
]

print(f"Found {len(synthetic_lethals)} synthetic lethal gene pairs")
print("\nTop 10 synthetic lethal pairs:")
print(synthetic_lethals.head(10))

# Step 8: Export results (confirm OUTDIR with user first)
single_results.to_csv(f"{OUTDIR}/single_gene_deletions.csv")
double_results.to_csv(f"{OUTDIR}/double_gene_deletions.csv")
synthetic_lethals.to_csv(f"{OUTDIR}/synthetic_lethals.csv")
```

## Workflow 2: Media Design and Optimization

This workflow shows how to systematically design growth media and find minimal media compositions.

```python
from cobra.io import load_model
from cobra.medium import minimal_medium
import pandas as pd

# Step 1: Load model and check current medium
model = load_model("textbook")
current_medium = model.medium
print("Current medium composition:")
for exchange, bound in current_medium.items():
    metabolite_id = exchange.replace("EX_", "").replace("_e", "")
    print(f"  {metabolite_id}: {bound:.2f} mmol/gDW/h")

# Step 2: Get baseline growth
baseline_growth = model.slim_optimize()
print(f"\nBaseline growth rate: {baseline_growth:.3f} /h")

# Step 3: Calculate minimal medium for different growth targets
growth_targets = [0.25, 0.5, 0.75, 1.0]
minimal_media = {}

for fraction in growth_targets:
    target_growth = baseline_growth * fraction
    print(f"\nCalculating minimal medium for {fraction*100:.0f}% growth ({target_growth:.3f} /h)...")

    min_medium = minimal_medium(
        model,
        target_growth,
        minimize_components=True,
        open_exchanges=True
    )

    minimal_media[fraction] = min_medium
    print(f"  Required components: {len(min_medium)}")
    print(f"  Components: {list(min_medium.index)}")

# Step 4: Compare media compositions
media_df = pd.DataFrame(minimal_media).fillna(0)
media_df.to_csv(f"{OUTDIR}/minimal_media_comparison.csv")

# Step 5: Test aerobic vs anaerobic conditions
print("\n--- Aerobic vs Anaerobic Comparison ---")

# Aerobic
model_aerobic = model.copy()
aerobic_growth = model_aerobic.slim_optimize()
aerobic_medium = minimal_medium(model_aerobic, aerobic_growth * 0.9, minimize_components=True)

# Anaerobic
model_anaerobic = model.copy()
medium_anaerobic = model_anaerobic.medium
medium_anaerobic["EX_o2_e"] = 0.0
model_anaerobic.medium = medium_anaerobic
anaerobic_growth = model_anaerobic.slim_optimize()
anaerobic_medium = minimal_medium(model_anaerobic, anaerobic_growth * 0.9, minimize_components=True)

print(f"Aerobic growth: {aerobic_growth:.3f} /h (requires {len(aerobic_medium)} components)")
print(f"Anaerobic growth: {anaerobic_growth:.3f} /h (requires {len(anaerobic_medium)} components)")

# Step 6: Identify unique requirements
aerobic_only = set(aerobic_medium.index) - set(anaerobic_medium.index)
anaerobic_only = set(anaerobic_medium.index) - set(aerobic_medium.index)
shared = set(aerobic_medium.index) & set(anaerobic_medium.index)

print(f"\nShared components: {len(shared)}")
print(f"Aerobic-only: {aerobic_only}")
print(f"Anaerobic-only: {anaerobic_only}")

# Step 7: Test custom medium
print("\n--- Testing Custom Medium ---")
custom_medium = {
    "EX_glc__D_e": 10.0,  # Glucose
    "EX_o2_e": 20.0,       # Oxygen
    "EX_nh4_e": 5.0,       # Ammonium
    "EX_pi_e": 5.0,        # Phosphate
    "EX_so4_e": 1.0,       # Sulfate
}

with model:
    model.medium = custom_medium
    custom_growth = model.optimize().objective_value
    print(f"Growth on custom medium: {custom_growth:.3f} /h")

    # Check which nutrients are limiting
    for exchange in custom_medium:
        with model:
            # Double the uptake rate
            medium_test = model.medium
            medium_test[exchange] *= 2
            model.medium = medium_test
            test_growth = model.optimize().objective_value
            improvement = (test_growth - custom_growth) / custom_growth * 100
            if improvement > 1:
                print(f"  {exchange}: +{improvement:.1f}% growth when doubled (LIMITING)")
```

## Workflow 3: Flux Space Exploration with Sampling

This workflow demonstrates comprehensive flux space analysis using FVA and sampling.

```python
from cobra.io import load_model
from cobra.flux_analysis import flux_variability_analysis
from cobra.sampling import sample
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: Load model
model = load_model("textbook")
baseline = model.slim_optimize()
print(f"Baseline growth: {baseline:.3f} /h")

# Step 2: Perform FVA at optimal growth (loopless=True is much slower)
print("\nPerforming FVA at optimal growth...")
fva_optimal = flux_variability_analysis(model, fraction_of_optimum=1.0)

# Step 3: Identify reactions with flexibility
fva_optimal["range"] = fva_optimal["maximum"] - fva_optimal["minimum"]
fva_optimal["relative_range"] = fva_optimal["range"] / (fva_optimal["maximum"].abs() + 1e-9)

flexible_reactions = fva_optimal[fva_optimal["range"] > 1.0].sort_values("range", ascending=False)
print(f"\nFound {len(flexible_reactions)} reactions with >1.0 mmol/gDW/h flexibility")
print("\nTop 10 most flexible reactions:")
print(flexible_reactions.head(10)[["minimum", "maximum", "range"]])

# Step 4: Perform FVA at suboptimal growth (90%)
print("\nPerforming FVA at 90% optimal growth...")
fva_suboptimal = flux_variability_analysis(model, fraction_of_optimum=0.9)
fva_suboptimal["range"] = fva_suboptimal["maximum"] - fva_suboptimal["minimum"]

# Step 5: Compare flexibility at different optimality levels
comparison = pd.DataFrame({
    "range_100": fva_optimal["range"],
    "range_90": fva_suboptimal["range"]
})
comparison["range_increase"] = comparison["range_90"] - comparison["range_100"]

print("\nReactions with largest increase in flexibility at suboptimality:")
print(comparison.sort_values("range_increase", ascending=False).head(10))

# Step 6: Perform flux sampling (reduce n/processes on genome-scale models)
print("\nPerforming flux sampling (1000 samples)...")
samples = sample(model, n=500, method="optgp", processes=1)

# Step 7: Analyze sampling results for key reactions
key_reactions = ["PFK", "FBA", "TPI", "GAPD", "PGK", "PGM", "ENO", "PYK"]
available_key_reactions = [r for r in key_reactions if r in samples.columns]

if available_key_reactions:
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    axes = axes.flatten()

    for idx, reaction_id in enumerate(available_key_reactions[:8]):
        ax = axes[idx]
        samples[reaction_id].hist(bins=30, ax=ax, alpha=0.7)

        # Overlay FVA bounds
        fva_min = fva_optimal.loc[reaction_id, "minimum"]
        fva_max = fva_optimal.loc[reaction_id, "maximum"]
        ax.axvline(fva_min, color='r', linestyle='--', label='FVA min')
        ax.axvline(fva_max, color='r', linestyle='--', label='FVA max')

        ax.set_xlabel("Flux (mmol/gDW/h)")
        ax.set_ylabel("Frequency")
        ax.set_title(reaction_id)
        if idx == 0:
            ax.legend()

    plt.tight_layout()
    plt.savefig(f"{OUTDIR}/flux_distributions.png", dpi=300)

# Step 8: Calculate correlation between reactions
print("\nCalculating flux correlations...")
correlation_matrix = samples[available_key_reactions].corr()

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap="coolwarm",
            center=0, ax=ax, square=True)
ax.set_title("Flux Correlations Between Key Glycolysis Reactions")
plt.tight_layout()
plt.savefig(f"{OUTDIR}/flux_correlations.png", dpi=300)

# Step 9: Identify reaction modules (highly correlated groups)
print("\nHighly correlated reaction pairs (|r| > 0.9):")
for i in range(len(correlation_matrix)):
    for j in range(i+1, len(correlation_matrix)):
        corr = correlation_matrix.iloc[i, j]
        if abs(corr) > 0.9:
            print(f"  {correlation_matrix.index[i]} <-> {correlation_matrix.columns[j]}: {corr:.3f}")

# Step 10: Export all results
fva_optimal.to_csv(f"{OUTDIR}/fva_optimal.csv")
fva_suboptimal.to_csv(f"{OUTDIR}/fva_suboptimal.csv")
samples.to_csv(f"{OUTDIR}/flux_samples.csv")
correlation_matrix.to_csv(f"{OUTDIR}/flux_correlations.csv")
```

## Workflow 4: Production Strain Design

This workflow demonstrates how to design a production strain for a target metabolite.

```python
from cobra.io import load_model
from cobra.flux_analysis import (
    production_envelope,
    flux_variability_analysis,
    single_gene_deletion
)
import pandas as pd
import matplotlib.pyplot as plt

# Step 1: Define production target
TARGET_METABOLITE = "EX_ac_e"  # Acetate production
CARBON_SOURCE = "EX_glc__D_e"  # Glucose uptake

# Step 2: Load model (textbook has acetate exchange; use iJO1366 for genome-scale)
model = load_model("textbook")
biomass_id = list(model.objective.variables)[0].name  # e.g. Biomass_Ecoli_core
print(f"Designing strain for {TARGET_METABOLITE} production")

# Step 3: Calculate baseline production envelope
print("\nCalculating production envelope...")
envelope = production_envelope(
    model,
    reactions=[CARBON_SOURCE, TARGET_METABOLITE],
    carbon_sources=CARBON_SOURCE
)

# Visualize production envelope
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(envelope[CARBON_SOURCE], envelope["mass_yield_maximum"], 'b-', label='Max yield')
ax.plot(envelope[CARBON_SOURCE], envelope["mass_yield_minimum"], 'r-', label='Min yield')
ax.set_xlabel(f"Glucose uptake (mmol/gDW/h)")
ax.set_ylabel(f"Acetate yield")
ax.set_title("Wild-type Production Envelope")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTDIR}/production_envelope_wildtype.png", dpi=300)

# Step 4: Maximize production while maintaining growth
print("\nOptimizing for production...")

max_growth = model.slim_optimize()
MIN_GROWTH = 0.1 * max_growth  # Maintain at least 10% of max growth

with model:
    model.reactions.get_by_id(biomass_id).lower_bound = MIN_GROWTH
    model.objective = TARGET_METABOLITE
    model.objective_direction = "max"
    production_solution = model.optimize()

    max_production = production_solution.objective_value
    print(f"Maximum production: {max_production:.3f} mmol/gDW/h")
    print(f"Growth rate: {production_solution.fluxes[biomass_id]:.3f} /h")

# Step 5: Identify beneficial gene knockouts
print("\nScreening for beneficial knockouts...")
model.objective = TARGET_METABOLITE
model.objective_direction = "max"

knockout_results = []
for gene in model.genes:
    with model:
        model.reactions.get_by_id(biomass_id).lower_bound = MIN_GROWTH
        model.objective = TARGET_METABOLITE
        model.objective_direction = "max"
        gene.knock_out()
        try:
            solution = model.optimize()
            if solution.status == "optimal":
                production = solution.objective_value
                growth = solution.fluxes[biomass_id]

                if production > max_production * 1.05:  # >5% improvement
                    knockout_results.append({
                        "gene": gene.id,
                        "production": production,
                        "growth": growth,
                        "improvement": (production / max_production - 1) * 100
                    })
        except:
            continue

knockout_df = pd.DataFrame(knockout_results)
if len(knockout_df) > 0:
    knockout_df = knockout_df.sort_values("improvement", ascending=False)
    print(f"\nFound {len(knockout_df)} beneficial knockouts:")
    print(knockout_df.head(10))
    knockout_df.to_csv(f"{OUTDIR}/beneficial_knockouts.csv", index=False)
else:
    print("No beneficial single knockouts found")

# Step 6: Test combination of best knockouts
if len(knockout_df) > 0:
    print("\nTesting knockout combinations...")
    top_genes = knockout_df.head(3)["gene"].tolist()

    with model:
        model.reactions.get_by_id(biomass_id).lower_bound = MIN_GROWTH
        model.objective = TARGET_METABOLITE
        model.objective_direction = "max"
        for gene_id in top_genes:
            model.genes.get_by_id(gene_id).knock_out()

        solution = model.optimize()
        if solution.status == "optimal":
            combined_production = solution.objective_value
            combined_growth = solution.fluxes[biomass_id]
            combined_improvement = (combined_production / max_production - 1) * 100

            print(f"\nCombined knockout results:")
            print(f"  Genes: {', '.join(top_genes)}")
            print(f"  Production: {combined_production:.3f} mmol/gDW/h")
            print(f"  Growth: {combined_growth:.3f} /h")
            print(f"  Improvement: {combined_improvement:.1f}%")

# Step 7: Analyze flux distribution in production strain
if len(knockout_df) > 0:
    best_gene = knockout_df.iloc[0]["gene"]

    with model:
        model.reactions.get_by_id(biomass_id).lower_bound = MIN_GROWTH
        model.objective = TARGET_METABOLITE
        model.objective_direction = "max"
        model.genes.get_by_id(best_gene).knock_out()
        solution = model.optimize()

        # Get active pathways
        active_fluxes = solution.fluxes[solution.fluxes.abs() > 0.1]
        active_fluxes.to_csv(f"{OUTDIR}/production_strain_fluxes_{best_gene}_knockout.csv")

        print(f"\nActive reactions in production strain: {len(active_fluxes)}")
```

## Workflow 5: Model Validation and Debugging

This workflow shows systematic approaches to validate and debug metabolic models.

```python
from cobra.io import load_model, read_sbml_model
from cobra.flux_analysis import flux_variability_analysis
import pandas as pd

# Step 1: Load model
model = load_model("textbook")  # Or read_sbml_model("your_model.xml")
print(f"Model: {model.id}")
print(f"Reactions: {len(model.reactions)}")
print(f"Metabolites: {len(model.metabolites)}")
print(f"Genes: {len(model.genes)}")

# Step 2: Check model feasibility
print("\n--- Feasibility Check ---")
try:
    objective_value = model.slim_optimize()
    print(f"Model is feasible (objective: {objective_value:.3f})")
except:
    print("Model is INFEASIBLE")
    print("Troubleshooting steps:")

    # Check for blocked reactions
    from cobra.flux_analysis import find_blocked_reactions
    blocked = find_blocked_reactions(model)
    print(f"  Blocked reactions: {len(blocked)}")
    if len(blocked) > 0:
        print(f"  First 10 blocked: {list(blocked)[:10]}")

    # Check medium
    print(f"\n  Current medium: {model.medium}")

    # Try opening all exchanges
    for reaction in model.exchanges:
        reaction.lower_bound = -1000

    try:
        objective_value = model.slim_optimize()
        print(f"\n  Model feasible with open exchanges (objective: {objective_value:.3f})")
        print("  Issue: Medium constraints too restrictive")
    except:
        print("\n  Model still infeasible with open exchanges")
        print("  Issue: Structural problem (missing reactions, mass imbalance, etc.)")

# Step 3: Check mass and charge balance
print("\n--- Mass and Charge Balance Check ---")
unbalanced_reactions = []
for reaction in model.reactions:
    try:
        balance = reaction.check_mass_balance()
        if balance:
            unbalanced_reactions.append({
                "reaction": reaction.id,
                "imbalance": balance
            })
    except:
        pass

if unbalanced_reactions:
    print(f"Found {len(unbalanced_reactions)} unbalanced reactions:")
    for item in unbalanced_reactions[:10]:
        print(f"  {item['reaction']}: {item['imbalance']}")
else:
    print("All reactions are mass balanced")

# Step 4: Identify dead-end metabolites
print("\n--- Dead-end Metabolite Check ---")
dead_end_metabolites = []
for metabolite in model.metabolites:
    producing_reactions = [r for r in metabolite.reactions
                          if r.metabolites[metabolite] > 0]
    consuming_reactions = [r for r in metabolite.reactions
                          if r.metabolites[metabolite] < 0]

    if len(producing_reactions) == 0 or len(consuming_reactions) == 0:
        dead_end_metabolites.append({
            "metabolite": metabolite.id,
            "producers": len(producing_reactions),
            "consumers": len(consuming_reactions)
        })

if dead_end_metabolites:
    print(f"Found {len(dead_end_metabolites)} dead-end metabolites:")
    for item in dead_end_metabolites[:10]:
        print(f"  {item['metabolite']}: {item['producers']} producers, {item['consumers']} consumers")
else:
    print("No dead-end metabolites found")

# Step 5: Check for duplicate reactions
print("\n--- Duplicate Reaction Check ---")
reaction_equations = {}
duplicates = []

for reaction in model.reactions:
    equation = reaction.build_reaction_string()
    if equation in reaction_equations:
        duplicates.append({
            "reaction1": reaction_equations[equation],
            "reaction2": reaction.id,
            "equation": equation
        })
    else:
        reaction_equations[equation] = reaction.id

if duplicates:
    print(f"Found {len(duplicates)} duplicate reaction pairs:")
    for item in duplicates[:10]:
        print(f"  {item['reaction1']} == {item['reaction2']}")
else:
    print("No duplicate reactions found")

# Step 6: Identify orphan genes
print("\n--- Orphan Gene Check ---")
orphan_genes = [gene for gene in model.genes if len(gene.reactions) == 0]

if orphan_genes:
    print(f"Found {len(orphan_genes)} orphan genes (not associated with reactions):")
    print(f"  First 10: {[g.id for g in orphan_genes[:10]]}")
else:
    print("No orphan genes found")

# Step 7: Check for thermodynamically infeasible loops (loopless FVA is slow on large models)
print("\n--- Thermodynamic Loop Check ---")
fva_standard = flux_variability_analysis(model)
fva_loopless = flux_variability_analysis(model, loopless=True)

loop_reactions = []
for reaction_id in fva_standard.index:
    standard_range = fva_standard.loc[reaction_id, "maximum"] - fva_standard.loc[reaction_id, "minimum"]
    loopless_range = fva_loopless.loc[reaction_id, "maximum"] - fva_loopless.loc[reaction_id, "minimum"]

    if standard_range > loopless_range + 0.1:
        loop_reactions.append({
            "reaction": reaction_id,
            "standard_range": standard_range,
            "loopless_range": loopless_range
        })

if loop_reactions:
    print(f"Found {len(loop_reactions)} reactions potentially involved in loops:")
    loop_df = pd.DataFrame(loop_reactions).sort_values("standard_range", ascending=False)
    print(loop_df.head(10))
else:
    print("No thermodynamically infeasible loops detected")

# Step 8: Generate validation report
print("\n--- Generating Validation Report ---")
validation_report = {
    "model_id": model.id,
    "feasible": objective_value if 'objective_value' in locals() else None,
    "n_reactions": len(model.reactions),
    "n_metabolites": len(model.metabolites),
    "n_genes": len(model.genes),
    "n_unbalanced": len(unbalanced_reactions),
    "n_dead_ends": len(dead_end_metabolites),
    "n_duplicates": len(duplicates),
    "n_orphan_genes": len(orphan_genes),
    "n_loop_reactions": len(loop_reactions)
}

validation_df = pd.DataFrame([validation_report])
validation_df.to_csv(f"{OUTDIR}/model_validation_report.csv", index=False)
print(f"Validation report saved to {OUTDIR}/model_validation_report.csv")
```

These workflows provide comprehensive templates for common COBRApy tasks. Adapt them as needed for specific research questions and models.
