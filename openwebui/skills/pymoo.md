---
name: pymoo
description: Multi-objective optimization framework. NSGA-II, NSGA-III, MOEA/D, Pareto fronts, constraint handling, benchmarks (ZDT, DTLZ), for engineering design and optimization problems.
---

# Pymoo - Multi-Objective Optimization in Python

## Overview

Pymoo is a comprehensive Python framework for optimization with emphasis on multi-objective problems. Solve single and multi-objective optimization using state-of-the-art algorithms (NSGA-II/III, MOEA/D, SPEA2), benchmark problems (ZDT, DTLZ), customizable genetic operators, and multi-criteria decision making methods. Excels at finding trade-off solutions (Pareto fronts) for problems with conflicting objectives. Current stable release: **pymoo 0.6.1.6** (November 2025).

## Installation

```bash
uv pip install pymoo
```

For reproducible environments, pin a version: `uv pip install "pymoo==0.6.1.6"`.

**Dependencies:** NumPy (2.x compatible since 0.6.1.3), SciPy, matplotlib (visualization). Autograd is optional for gradient-based features (since 0.6.1.3).

**Documentation:** https://pymoo.org/ — LLM-friendly index: https://pymoo.org/llms.txt

## When to Use This Skill

This skill should be used when:
- Solving optimization problems with one or multiple objectives
- Finding Pareto-optimal solutions and analyzing trade-offs
- Implementing evolutionary algorithms (GA, DE, PSO, NSGA-II/III)
- Working with constrained optimization problems
- Benchmarking algorithms on standard test problems (ZDT, DTLZ, WFG)
- Customizing genetic operators (crossover, mutation, selection)
- Visualizing high-dimensional optimization results
- Making decisions from multiple competing solutions
- Handling binary, discrete, continuous, or mixed-variable problems

## Core Concepts

### The Unified Interface

Pymoo uses a consistent `minimize()` function for all optimization tasks:

```python
from pymoo.optimize import minimize

result = minimize(
    problem,        # What to optimize
    algorithm,      # How to optimize
    termination,    # When to stop
    seed=1,
    verbose=True
)
```

**Result object contains:**
- `result.X`: Decision variables of optimal solution(s)
- `result.F`: Objective values of optimal solution(s)
- `result.G`: Constraint violations (if constrained)
- `result.algorithm`: Algorithm object with history

### Problem Definition Styles

Pymoo supports three problem definition styles:

- **`Problem`**: Vectorized — `_evaluate` receives a batch of solutions (matrix)
- **`ElementwiseProblem`**: One solution per call — recommended for custom problems and parallel evaluation
- **`FunctionalProblem`**: Define objectives and constraints as separate functions without subclassing

### Problem Types

**Single-objective:** One objective to minimize/maximize
**Multi-objective:** 2-3 conflicting objectives → Pareto front
**Many-objective:** 4+ objectives → High-dimensional Pareto front
**Constrained:** Objectives + inequality/equality constraints
**Mixed-variable:** Continuous, integer, binary, and categorical variables in one problem
**Dynamic:** Time-varying objectives or constraints

## Quick Start Workflows

Nine runnable workflows are in
[references/quick_start_workflows.md](references/quick_start_workflows.md):

| # | Workflow | Use when |
| --- | --- | --- |
| 1 | Single-objective optimization | one objective, GA or DE |
| 2 | Multi-objective (2-3 objectives) | NSGA-II and a Pareto front |
| 3 | Many-objective (4+ objectives) | NSGA-III or reference-direction methods |
| 4 | Custom problem definition | subclassing `Problem` / `ElementwiseProblem` |
| 5 | Constraint handling | inequality and equality constraints |
| 6 | Decision making from a Pareto front | scalarization and MCDM selection |
| 7 | Visualization | scatter, PCP, radviz, and heatmap views |
| 8 | Parallel evaluation | threads, processes, or Dask for expensive objectives |
| 9 | Mixed-variable optimization | integer, binary, and categorical variables |

## Algorithm Selection Guide

### Single-Objective Problems

| Algorithm | Best For | Key Features |
|-----------|----------|--------------|
| **GA** | General-purpose | Flexible, customizable operators |
| **DE** | Continuous optimization | Good global search |
| **PSO** | Smooth landscapes | Fast convergence |
| **CMA-ES** | Difficult/noisy problems | Self-adapting |

### Multi-Objective Problems (2-3 objectives)

| Algorithm | Best For | Key Features |
|-----------|----------|--------------|
| **NSGA-II** | Standard benchmark | Fast, reliable, well-tested |
| **SPEA2** | Archive-based MOO | Strength-based fitness, external archive |
| **R-NSGA-II** | Preference regions | Reference point guidance |
| **MOEA/D** | Decomposable problems | Scalarization approach |

### Many-Objective Problems (4+ objectives)

| Algorithm | Best For | Key Features |
|-----------|----------|--------------|
| **NSGA-III** | 4-15 objectives | Reference direction-based |
| **RVEA** | Adaptive search | Reference vector evolution |
| **AGE-MOEA** | Complex landscapes | Adaptive geometry |

### Constrained Problems

| Approach | Algorithm | When to Use |
|----------|-----------|-------------|
| Feasibility-first | Any algorithm | Large feasible region |
| Specialized | SRES, ISRES | Heavy constraints |
| Penalty | GA + penalty | Algorithm compatibility |

**See:** `references/algorithms.md` for comprehensive algorithm reference

## Benchmark Problems

### Quick problem access:
```python
from pymoo.problems import get_problem

# Single-objective
problem = get_problem("rastrigin", n_var=10)
problem = get_problem("rosenbrock", n_var=10)

# Multi-objective
problem = get_problem("zdt1")        # Convex front
problem = get_problem("zdt2")        # Non-convex front
problem = get_problem("zdt3")        # Disconnected front

# Many-objective
problem = get_problem("dtlz2", n_obj=5, n_var=12)
problem = get_problem("dtlz7", n_obj=4)
```

**See:** `references/problems.md` for complete test problem reference

## Genetic Operator Customization

### Standard operator configuration:
```python
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM

algorithm = GA(
    pop_size=100,
    crossover=SBX(prob=0.9, eta=15),
    mutation=PM(eta=20),
    eliminate_duplicates=True
)
```

### Operator selection by variable type:

**Continuous variables:**
- Crossover: SBX (Simulated Binary Crossover)
- Mutation: PM (Polynomial Mutation)

**Binary variables:**
- Crossover: TwoPointCrossover, UniformCrossover
- Mutation: BitflipMutation

**Permutations (TSP, scheduling):**
- Crossover: OrderCrossover (OX)
- Mutation: InversionMutation

**See:** `references/operators.md` for comprehensive operator reference

## Performance and Troubleshooting

### Common issues and solutions:

**Problem: Algorithm not converging**
- Increase population size
- Increase number of generations
- Check if problem is multimodal (try different algorithms)
- Verify constraints are correctly formulated

**Problem: Poor Pareto front distribution**
- For NSGA-III: Adjust reference directions
- Increase population size
- Check for duplicate elimination
- Verify problem scaling

**Problem: Few feasible solutions**
- Use constraint-as-objective approach
- Apply repair operators
- Try SRES/ISRES for constrained problems
- Check constraint formulation (should be g <= 0)

**Problem: High computational cost**
- Reduce population size
- Decrease number of generations
- Use simpler operators
- Enable parallel evaluation via `elementwise_runner` (see Workflow 8)

### Best practices:

1. **Normalize objectives** when scales differ significantly
2. **Set random seed** for reproducibility
3. **Save history** to analyze convergence: `save_history=True`
4. **Visualize results** to understand solution quality
5. **Compare with true Pareto front** when available
6. **Use appropriate termination criteria** (generations, evaluations, tolerance)
7. **Tune operator parameters** for problem characteristics

## Resources

This skill includes comprehensive reference documentation and executable examples:

### references/
Detailed documentation for in-depth understanding:

- **algorithms.md**: Complete algorithm reference with parameters, usage, and selection guidelines
- **problems.md**: Benchmark test problems (ZDT, DTLZ, WFG) with characteristics
- **operators.md**: Genetic operators (sampling, selection, crossover, mutation) with configuration
- **visualization.md**: All visualization types with examples and selection guide
- **constraints_mcdm.md**: Constraint handling techniques and multi-criteria decision making methods
- **parallelization.md**: Parallel evaluation with StarmapParallelization and JoblibParallelization

**Search patterns for references:**
- Algorithm details: `grep -r "NSGA-II\|NSGA-III\|MOEA/D" references/`
- Constraint methods: `grep -r "Feasibility First\|Penalty\|Repair" references/`
- Visualization types: `grep -r "Scatter\|PCP\|Petal" references/`

### scripts/
Executable examples demonstrating common workflows:

- **single_objective_example.py**: Basic single-objective optimization with GA
- **multi_objective_example.py**: Multi-objective optimization with NSGA-II, visualization
- **many_objective_example.py**: Many-objective optimization with NSGA-III, reference directions
- **custom_problem_example.py**: Defining custom problems (constrained and unconstrained)
- **decision_making_example.py**: Multi-criteria decision making with different preferences

**Run examples:**
```bash
python3 scripts/single_objective_example.py
python3 scripts/multi_objective_example.py
python3 scripts/many_objective_example.py
python3 scripts/custom_problem_example.py
python3 scripts/decision_making_example.py
```

## Additional Notes

**Common patterns:**
- Use `ElementwiseProblem` for custom problems (or `FunctionalProblem` for function-based definitions)
- Use `vars` dict with typed variables for mixed-variable problems
- Constraints formulated as `g(x) <= 0` and `h(x) = 0`
- Reference directions required for NSGA-III
- Normalize objectives before MCDM
- Use appropriate termination: `('n_gen', N)` or `get_termination("f_tol", tol=0.001)`

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/pymoo/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/algorithms.md`

# Pymoo Algorithms Reference

Comprehensive reference for optimization algorithms available in pymoo.

## Single-Objective Optimization Algorithms

### Genetic Algorithm (GA)
**Purpose:** General-purpose single-objective evolutionary optimization
**Best for:** Continuous, discrete, or mixed-variable problems
**Algorithm type:** (μ+λ) genetic algorithm

**Key parameters:**
- `pop_size`: Population size (default: 100)
- `sampling`: Initial population generation strategy
- `selection`: Parent selection mechanism (default: Tournament)
- `crossover`: Recombination operator (default: SBX)
- `mutation`: Variation operator (default: Polynomial)
- `eliminate_duplicates`: Remove redundant solutions (default: True)
- `n_offsprings`: Offspring per generation

**Usage:**
```python
from pymoo.algorithms.soo.nonconvex.ga import GA
algorithm = GA(pop_size=100, eliminate_duplicates=True)
```

### Differential Evolution (DE)
**Purpose:** Single-objective continuous optimization
**Best for:** Continuous parameter optimization with good global search
**Algorithm type:** Population-based differential evolution

**Variants:** Multiple DE strategies available (rand/1/bin, best/1/bin, etc.)

### Particle Swarm Optimization (PSO)
**Purpose:** Single-objective optimization through swarm intelligence
**Best for:** Continuous problems, fast convergence on smooth landscapes

### CMA-ES
**Purpose:** Covariance Matrix Adaptation Evolution Strategy
**Best for:** Continuous optimization, particularly for noisy or ill-conditioned problems

### Pattern Search
**Purpose:** Direct search method
**Best for:** Problems where gradient information is unavailable

### Nelder-Mead
**Purpose:** Simplex-based optimization
**Best for:** Local optimization of continuous functions

### MixedVariableGA
**Purpose:** Single-objective optimization with mixed variable types
**Best for:** Problems with continuous, integer, binary, and categorical variables

**Usage:**
```python
from pymoo.core.mixed import MixedVariableGA
from pymoo.core.variable import Real, Integer, Choice, Binary

# Define problem with vars dict (see mixed-variable docs)
algorithm = MixedVariableGA(pop_size=20)
```

For multi-objective mixed-variable problems, pass a survival operator:
```python
from pymoo.algorithms.moo.nsga2 import RankAndCrowdingSurvival
algorithm = MixedVariableGA(pop_size=20, survival=RankAndCrowdingSurvival())
```

### Optuna (Mixed-Variable SOO)
**Purpose:** Single-objective mixed-variable search via Optuna wrapper
**Best for:** Hyperparameter-style mixed search when Optuna's TPE/samplers are preferred

**Usage:**
```python
from pymoo.algorithms.soo.nonconvex.optuna import Optuna
algorithm = Optuna()
```

Requires Optuna installed separately: `uv pip install optuna`

## Multi-Objective Optimization Algorithms

### NSGA-II (Non-dominated Sorting Genetic Algorithm II)
**Purpose:** Multi-objective optimization with 2-3 objectives
**Best for:** Bi- and tri-objective problems requiring well-distributed Pareto fronts
**Selection strategy:** Non-dominated sorting + crowding distance

**Key features:**
- Fast non-dominated sorting
- Crowding distance for diversity
- Elitist approach
- Binary tournament mating selection

**Key parameters:**
- `pop_size`: Population size (default: 100)
- `sampling`: Initial population strategy
- `crossover`: Default SBX for continuous
- `mutation`: Default Polynomial Mutation
- `survival`: RankAndCrowding

**Usage:**
```python
from pymoo.algorithms.moo.nsga2 import NSGA2
algorithm = NSGA2(pop_size=100)
```

**When to use:**
- 2-3 objectives
- Need for distributed solutions across Pareto front
- Standard multi-objective benchmark

### SPEA2 (Strength Pareto Evolutionary Algorithm 2)
**Purpose:** Multi-objective optimization with external archive
**Best for:** Bi- and tri-objective problems; alternative to NSGA-II when archive-based selection is preferred
**Selection strategy:** Strength-based fitness + k-nearest-neighbor density estimation

**Key features:**
- External archive of non-dominated solutions
- Strength value measures how many solutions a point dominates
- Improved in pymoo 0.6.1.6

**Usage:**
```python
from pymoo.algorithms.moo.spea2 import SPEA2
algorithm = SPEA2(pop_size=100)
```

**When to use:**
- 2-3 objectives
- Prefer archive-based selection over crowding distance
- Compare against NSGA-II on benchmark problems

### NSGA-III
**Purpose:** Many-objective optimization (4+ objectives)
**Best for:** Problems with 4 or more objectives requiring uniform Pareto front coverage
**Selection strategy:** Reference direction-based diversity maintenance

**Key features:**
- Reference directions guide population
- Maintains diversity in high-dimensional objective spaces
- Niche preservation through reference points
- Underrepresented reference direction selection

**Key parameters:**
- `ref_dirs`: Reference directions (REQUIRED)
- `pop_size`: Defaults to number of reference directions
- `crossover`: Default SBX
- `mutation`: Default Polynomial Mutation

**Usage:**
```python
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.util.ref_dirs import get_reference_directions

ref_dirs = get_reference_directions("das-dennis", 4, n_partitions=12)  # n_dim is positional
algorithm = NSGA3(ref_dirs=ref_dirs)
```

**NSGA-II vs NSGA-III:**
- Use NSGA-II for 2-3 objectives
- Use NSGA-III for 4+ objectives
- NSGA-III provides more uniform distribution
- NSGA-II has lower computational overhead

### R-NSGA-II (Reference Point Based NSGA-II)
**Purpose:** Multi-objective optimization with preference articulation
**Best for:** When decision maker has preferred regions of Pareto front

### U-NSGA-III (Unified NSGA-III)
**Purpose:** Improved version handling various scenarios
**Best for:** Many-objective problems with additional robustness

### MOEA/D (Multi-Objective Evolutionary Algorithm based on Decomposition)
**Purpose:** Decomposition-based multi-objective optimization
**Best for:** Problems where decomposition into scalar subproblems is effective

### AGE-MOEA
**Purpose:** Adaptive geometry estimation
**Best for:** Multi and many-objective problems with adaptive mechanisms

### RVEA (Reference Vector guided Evolutionary Algorithm)
**Purpose:** Reference vector-based many-objective optimization
**Best for:** Many-objective problems with adaptive reference vectors

### SMS-EMOA
**Purpose:** S-Metric Selection Evolutionary Multi-objective Algorithm
**Best for:** Problems where hypervolume indicator is critical
**Selection:** Uses dominated hypervolume contribution

## Dynamic Multi-Objective Algorithms

### D-NSGA-II
**Purpose:** Dynamic multi-objective problems
**Best for:** Time-varying objective functions or constraints

### KGB-DMOEA
**Purpose:** Knowledge-guided dynamic multi-objective optimization
**Best for:** Dynamic problems leveraging historical information

## Constrained Optimization

### SRES (Stochastic Ranking Evolution Strategy)
**Purpose:** Single-objective constrained optimization
**Best for:** Heavily constrained problems

### ISRES (Improved SRES)
**Purpose:** Enhanced constrained optimization
**Best for:** Complex constraint landscapes

## Algorithm Selection Guidelines

**For single-objective problems:**
- Start with GA for general problems
- Use DE for continuous optimization
- Try PSO for faster convergence on smooth problems
- Use CMA-ES for difficult/noisy landscapes

**For multi-objective problems:**
- 2-3 objectives: NSGA-II or SPEA2
- 4+ objectives: NSGA-III
- Preference articulation: R-NSGA-II
- Decomposition-friendly: MOEA/D
- Hypervolume focus: SMS-EMOA

**For constrained problems:**
- Feasibility-based survival selection (works with most algorithms)
- Heavy constraints: SRES/ISRES
- Penalty methods for algorithm compatibility

**For dynamic problems:**
- Time-varying: D-NSGA-II
- Historical knowledge useful: KGB-DMOEA

### `references/constraints_mcdm.md`

# Pymoo Constraints and Decision Making Reference

Reference for constraint handling and multi-criteria decision making in pymoo.

## Constraint Handling

### Defining Constraints

Constraints are specified in the Problem definition:

```python
from pymoo.core.problem import ElementwiseProblem
import numpy as np

class ConstrainedProblem(ElementwiseProblem):
    def __init__(self):
        super().__init__(
            n_var=2,
            n_obj=2,
            n_ieq_constr=2,    # Number of inequality constraints
            n_eq_constr=1,      # Number of equality constraints
            xl=np.array([0, 0]),
            xu=np.array([5, 5])
        )

    def _evaluate(self, x, out, *args, **kwargs):
        # Objectives
        f1 = x[0]**2 + x[1]**2
        f2 = (x[0]-1)**2 + (x[1]-1)**2

        out["F"] = [f1, f2]

        # Inequality constraints (formulated as g(x) <= 0)
        g1 = x[0] + x[1] - 5  # x[0] + x[1] >= 5 → -(x[0] + x[1] - 5) <= 0
        g2 = x[0]**2 + x[1]**2 - 25  # x[0]^2 + x[1]^2 <= 25

        out["G"] = [g1, g2]

        # Equality constraints (formulated as h(x) = 0)
        h1 = x[0] - 2*x[1]

        out["H"] = [h1]
```

**Constraint formulation rules:**
- Inequality: `g(x) <= 0` (feasible when negative or zero)
- Equality: `h(x) = 0` (feasible when zero)
- Convert `g(x) >= 0` to `-g(x) <= 0`

### Constraint Handling Techniques

#### 1. Feasibility First (Default)
**Mechanism:** Always prefer feasible over infeasible solutions
**Comparison:**
1. Both feasible → compare by objective values
2. One feasible, one infeasible → feasible wins
3. Both infeasible → compare by constraint violation

**Usage:**
```python
from pymoo.algorithms.moo.nsga2 import NSGA2

# Feasibility first is default for most algorithms
algorithm = NSGA2(pop_size=100)
```

**Advantages:**
- Works with any sorting-based algorithm
- Simple and effective
- No parameter tuning

**Disadvantages:**
- May struggle with small feasible regions
- Can ignore good infeasible solutions

#### 2. Penalty Methods
**Mechanism:** Add penalty to objective based on constraint violation
**Formula:** `F_penalized = F + penalty_factor * violation`

**Usage:**
```python
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.constraints.as_penalty import ConstraintsAsPenalty

# Wrap problem with penalty
problem_with_penalty = ConstraintsAsPenalty(problem, penalty=1e6)

algorithm = GA(pop_size=100)
```

**Parameters:**
- `penalty`: Penalty coefficient (tune based on problem scale)

**Advantages:**
- Converts constrained to unconstrained problem
- Works with any optimization algorithm

**Disadvantages:**
- Penalty parameter sensitive
- May need problem-specific tuning

#### 3. Constraint as Objective
**Mechanism:** Treat constraint violation as additional objective
**Result:** Multi-objective problem with M+1 objectives (M original + constraint)

**Usage:**
```python
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.constraints.as_obj import ConstraintsAsObjective

# Add constraint violation as objective
problem_with_cv_obj = ConstraintsAsObjective(problem)

algorithm = NSGA2(pop_size=100)
```

**Advantages:**
- No parameter tuning
- Maintains infeasible solutions that may be useful
- Works well when feasible region is small

**Disadvantages:**
- Increases problem dimensionality
- More complex Pareto front analysis

#### 4. Epsilon-Constraint Handling
**Mechanism:** Dynamic feasibility threshold
**Concept:** Gradually tighten constraint tolerance over generations

**Advantages:**
- Smooth transition to feasible region
- Helps with difficult constraint landscapes

**Disadvantages:**
- Algorithm-specific implementation
- Requires parameter tuning

#### 5. Repair Operators
**Mechanism:** Modify infeasible solutions to satisfy constraints
**Application:** After crossover/mutation, repair offspring

**Usage:**
```python
from pymoo.core.repair import Repair

class MyRepair(Repair):
    def _do(self, problem, X, **kwargs):
        # Project X onto feasible region
        # Example: clip to bounds
        X = np.clip(X, problem.xl, problem.xu)
        return X

from pymoo.algorithms.soo.nonconvex.ga import GA

algorithm = GA(pop_size=100, repair=MyRepair())
```

**Advantages:**
- Maintains feasibility throughout optimization
- Can encode domain knowledge

**Disadvantages:**
- Requires problem-specific implementation
- May restrict search

### Constraint-Handling Algorithms

Some algorithms have built-in constraint handling:

#### SRES (Stochastic Ranking Evolution Strategy)
**Purpose:** Single-objective constrained optimization
**Mechanism:** Stochastic ranking balances objectives and constraints

**Usage:**
```python
from pymoo.algorithms.soo.nonconvex.sres import SRES

algorithm = SRES()
```

#### ISRES (Improved SRES)
**Purpose:** Enhanced constrained optimization
**Improvements:** Better parameter adaptation

**Usage:**
```python
from pymoo.algorithms.soo.nonconvex.isres import ISRES

algorithm = ISRES()
```

### Constraint Handling Guidelines

**Choose technique based on:**

| Problem Characteristic | Recommended Technique |
|------------------------|----------------------|
| Large feasible region | Feasibility First |
| Small feasible region | Constraint as Objective, Repair |
| Heavily constrained | SRES/ISRES, Epsilon-constraint |
| Linear constraints | Repair (projection) |
| Nonlinear constraints | Feasibility First, Penalty |
| Known feasible solutions | Biased initialization |

## Multi-Criteria Decision Making (MCDM)

After obtaining a Pareto front, MCDM helps select preferred solution(s).

### Decision Making Context

**Pareto front characteristics:**
- Multiple non-dominated solutions
- Each represents different trade-off
- No objectively "best" solution
- Requires decision maker preferences

### MCDM Methods in Pymoo

#### 1. Pseudo-Weights
**Concept:** Weight each objective, select solution minimizing weighted sum
**Formula:** `score = w1*f1 + w2*f2 + ... + wM*fM`

**Usage:**
```python
from pymoo.mcdm.pseudo_weights import PseudoWeights

# Define weights (must sum to 1)
weights = np.array([0.3, 0.7])  # 30% weight on f1, 70% on f2

dm = PseudoWeights(weights)
best_idx = dm.do(result.F)
best_solution = result.X[best_idx]
```

**When to use:**
- Clear preference articulation available
- Objectives commensurable
- Linear trade-offs acceptable

**Limitations:**
- Requires weight specification
- Linear assumption may not capture preferences
- Sensitive to objective scaling

#### 2. Compromise Programming
**Concept:** Select solution closest to ideal point
**Metric:** Distance to ideal (e.g., Euclidean, Tchebycheff)

**Usage:**
```python
from pymoo.mcdm.compromise_programming import CompromiseProgramming

dm = CompromiseProgramming()
best_idx = dm.do(result.F, ideal=ideal_point, nadir=nadir_point)
```

**When to use:**
- Ideal objective values known or estimable
- Balanced consideration of all objectives
- No clear weight preferences

#### 3. Interactive Decision Making
**Concept:** Iterative preference refinement
**Process:**
1. Show representative solutions to decision maker
2. Gather feedback on preferences
3. Focus search on preferred regions
4. Repeat until satisfactory solution found

**Approaches:**
- Reference point methods
- Trade-off analysis
- Progressive preference articulation

### Decision Making Workflow

**Step 1: Normalize objectives**
```python
# Normalize to [0, 1] for fair comparison
F_norm = (result.F - result.F.min(axis=0)) / (result.F.max(axis=0) - result.F.min(axis=0))
```

**Step 2: Analyze trade-offs**
```python
from pymoo.visualization.scatter import Scatter

plot = Scatter()
plot.add(result.F)
plot.show()

# Identify knee points, extreme solutions
```

**Step 3: Apply MCDM method**
```python
from pymoo.mcdm.pseudo_weights import PseudoWeights

weights = np.array([0.4, 0.6])  # Based on preferences
dm = PseudoWeights(weights)
selected = dm.do(F_norm)
```

**Step 4: Validate selection**
```python
# Visualize selected solution
from pymoo.visualization.petal import Petal

plot = Petal()
plot.add(result.F[selected], label="Selected")
# Add other candidates for comparison
plot.show()
```

### Advanced MCDM Techniques

#### Knee Point Detection
**Concept:** Solutions where small improvement in one objective causes large degradation in others

**Usage:**
```python
from pymoo.mcdm.knee import KneePoint

km = KneePoint()
knee_idx = km.do(result.F)
knee_solutions = result.X[knee_idx]
```

**When to use:**
- No clear preferences
- Balanced trade-offs desired
- Convex Pareto fronts

#### Hypervolume Contribution
**Concept:** Select solutions contributing most to hypervolume
**Use case:** Maintain diverse subset of solutions

**Usage:**
```python
from pymoo.indicators.hv import HV

hv = HV(ref_point=reference_point)
hv_contributions = hv.calc_contributions(result.F)

# Select top contributors
top_k = 5
top_indices = np.argsort(hv_contributions)[-top_k:]
selected_solutions = result.X[top_indices]
```

### Decision Making Guidelines

**When decision maker has:**

| Preference Information | Recommended Method |
|------------------------|-------------------|
| Clear objective weights | Pseudo-Weights |
| Ideal target values | Compromise Programming |
| No prior preferences | Knee Point, Visual inspection |
| Conflicting criteria | Interactive methods |
| Need diverse subset | Hypervolume contribution |

**Best practices:**
1. **Normalize objectives** before MCDM
2. **Visualize Pareto front** to understand trade-offs
3. **Consider multiple methods** for robust selection
4. **Validate results** with domain experts
5. **Document assumptions** and preference sources
6. **Perform sensitivity analysis** on weights/parameters

### Integration Example

Complete workflow with constraint handling and decision making:

```python
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.mcdm.pseudo_weights import PseudoWeights
import numpy as np

# Define constrained problem
problem = MyConstrainedProblem()

# Setup algorithm with feasibility-first constraint handling
algorithm = NSGA2(
    pop_size=100,
    eliminate_duplicates=True
)

# Optimize
result = minimize(
    problem,
    algorithm,
    ('n_gen', 200),
    seed=1,
    verbose=True
)

# Filter feasible solutions only
feasible_mask = result.CV[:, 0] == 0  # Constraint violation = 0
F_feasible = result.F[feasible_mask]
X_feasible = result.X[feasible_mask]

# Normalize objectives
F_norm = (F_feasible - F_feasible.min(axis=0)) / (F_feasible.max(axis=0) - F_feasible.min(axis=0))

# Apply MCDM
weights = np.array([0.5, 0.5])
dm = PseudoWeights(weights)
best_idx = dm.do(F_norm)

# Get final solution
best_solution = X_feasible[best_idx]
best_objectives = F_feasible[best_idx]

print(f"Selected solution: {best_solution}")
print(f"Objective values: {best_objectives}")
```

### `references/operators.md`

# Pymoo Genetic Operators Reference

Comprehensive reference for genetic operators in pymoo.

## Sampling Operators

Sampling operators initialize populations at the start of optimization.

### Random Sampling
**Purpose:** Generate random initial solutions
**Types:**
- `FloatRandomSampling`: Continuous variables
- `BinaryRandomSampling`: Binary variables
- `IntegerRandomSampling`: Integer variables
- `PermutationRandomSampling`: Permutation-based problems

**Usage:**
```python
from pymoo.operators.sampling.rnd import FloatRandomSampling
sampling = FloatRandomSampling()
```

### Latin Hypercube Sampling (LHS)
**Purpose:** Space-filling initial population
**Benefit:** Better coverage of search space than random
**Types:**
- `LHS`: Standard Latin Hypercube

**Usage:**
```python
from pymoo.operators.sampling.lhs import LHS
sampling = LHS()
```

### Custom Sampling
Provide initial population through Population object or NumPy array

## Selection Operators

Selection operators choose parents for reproduction.

### Tournament Selection
**Purpose:** Select parents through tournament competition
**Mechanism:** Randomly select k individuals, choose best
**Parameters:**
- `pressure`: Tournament size (default: 2)
- `func_comp`: Comparison function

**Usage:**
```python
from pymoo.operators.selection.tournament import TournamentSelection
selection = TournamentSelection(pressure=2)
```

### Random Selection
**Purpose:** Uniform random parent selection
**Use case:** Baseline or exploration-focused algorithms

**Usage:**
```python
from pymoo.operators.selection.rnd import RandomSelection
selection = RandomSelection()
```

## Crossover Operators

Crossover operators recombine parent solutions to create offspring.

### For Continuous Variables

#### Simulated Binary Crossover (SBX)
**Purpose:** Primary crossover for continuous optimization
**Mechanism:** Simulates single-point crossover of binary-encoded variables
**Parameters:**
- `prob`: Crossover probability (default: 0.9)
- `eta`: Distribution index (default: 15)
  - Higher eta → offspring closer to parents
  - Lower eta → more exploration

**Usage:**
```python
from pymoo.operators.crossover.sbx import SBX
crossover = SBX(prob=0.9, eta=15)
```

**String shorthand:** `"real_sbx"`

#### Differential Evolution Crossover
**Purpose:** DE-specific recombination
**Variants:**
- `DE/rand/1/bin`
- `DE/best/1/bin`
- `DE/current-to-best/1/bin`

**Parameters:**
- `CR`: Crossover rate
- `F`: Scaling factor

### For Binary Variables

#### Single Point Crossover
**Purpose:** Cut and swap at one point
**Usage:**
```python
from pymoo.operators.crossover.pntx import SinglePointCrossover
crossover = SinglePointCrossover()
```

#### Two Point Crossover
**Purpose:** Cut and swap between two points
**Usage:**
```python
from pymoo.operators.crossover.pntx import TwoPointCrossover
crossover = TwoPointCrossover()
```

#### K-Point Crossover
**Purpose:** Multiple cut points
**Parameters:**
- `n_points`: Number of crossover points

#### Uniform Crossover
**Purpose:** Each gene independently from either parent
**Parameters:**
- `prob`: Per-gene swap probability (default: 0.5)

**Usage:**
```python
from pymoo.operators.crossover.ux import UniformCrossover
crossover = UniformCrossover(prob=0.5)
```

#### Half Uniform Crossover (HUX)
**Purpose:** Exchange exactly half of differing genes
**Benefit:** Maintains genetic diversity

### For Permutations

#### Order Crossover (OX)
**Purpose:** Preserve relative order from parents
**Use case:** Traveling salesman, scheduling problems

**Usage:**
```python
from pymoo.operators.crossover.ox import OrderCrossover
crossover = OrderCrossover()
```

#### Edge Recombination Crossover (ERX)
**Purpose:** Preserve edge information from parents
**Use case:** Routing problems where edge connectivity matters

#### Partially Mapped Crossover (PMX)
**Purpose:** Exchange segments while maintaining permutation validity

## Mutation Operators

Mutation operators introduce variation to maintain diversity.

### For Continuous Variables

#### Polynomial Mutation (PM)
**Purpose:** Primary mutation for continuous optimization
**Mechanism:** Polynomial probability distribution
**Parameters:**
- `prob`: Per-variable mutation probability
- `eta`: Distribution index (default: 20)
  - Higher eta → smaller perturbations
  - Lower eta → larger perturbations

**Usage:**
```python
from pymoo.operators.mutation.pm import PM
mutation = PM(prob=None, eta=20)  # prob=None means 1/n_var
```

**String shorthand:** `"real_pm"`

**Probability guidelines:**
- `None` or `1/n_var`: Standard recommendation
- Higher for more exploration
- Lower for more exploitation

### For Binary Variables

#### Bitflip Mutation
**Purpose:** Flip bits with specified probability
**Parameters:**
- `prob`: Per-bit flip probability

**Usage:**
```python
from pymoo.operators.mutation.bitflip import BitflipMutation
mutation = BitflipMutation(prob=0.05)
```

### For Integer Variables

#### Integer Polynomial Mutation
**Purpose:** PM adapted for integers
**Ensures:** Valid integer values after mutation

### For Permutations

#### Inversion Mutation
**Purpose:** Reverse a segment of the permutation
**Use case:** Maintains some order structure

**Usage:**
```python
from pymoo.operators.mutation.inversion import InversionMutation
mutation = InversionMutation()
```

#### Scramble Mutation
**Purpose:** Randomly shuffle a segment

### Custom Mutation
Define custom mutation by extending `Mutation` class

## Repair Operators

Repair operators fix constraint violations or ensure solution feasibility.

### Rounding Repair
**Purpose:** Round to nearest valid value
**Use case:** Integer/discrete variables with bound constraints

### Bounce Back Repair
**Purpose:** Reflect out-of-bounds values back into feasible region
**Use case:** Box-constrained continuous problems

### Projection Repair
**Purpose:** Project infeasible solutions onto feasible region
**Use case:** Linear constraints

### Custom Repair
**Purpose:** Domain-specific constraint handling
**Implementation:** Extend `Repair` class

**Example:**
```python
from pymoo.core.repair import Repair

class MyRepair(Repair):
    def _do(self, problem, X, **kwargs):
        # Modify X to satisfy constraints
        # Return repaired X
        return X
```

## Operator Configuration Guidelines

### Parameter Tuning

**Crossover probability:**
- High (0.8-0.95): Standard for most problems
- Lower: More emphasis on mutation

**Mutation probability:**
- `1/n_var`: Standard recommendation
- Higher: More exploration, slower convergence
- Lower: Faster convergence, risk of premature convergence

**Distribution indices (eta):**
- Crossover eta (15-30): Higher for local search
- Mutation eta (20-50): Higher for exploitation

### Problem-Specific Selection

**Continuous problems:**
- Crossover: SBX
- Mutation: Polynomial Mutation
- Selection: Tournament

**Binary problems:**
- Crossover: Two-point or Uniform
- Mutation: Bitflip
- Selection: Tournament

**Permutation problems:**
- Crossover: Order Crossover (OX)
- Mutation: Inversion or Scramble
- Selection: Tournament

**Mixed-variable problems:**
- Use appropriate operators per variable type
- Ensure operator compatibility

### String-Based Configuration

Pymoo supports convenient string-based operator specification:

```python
from pymoo.algorithms.soo.nonconvex.ga import GA

algorithm = GA(
    pop_size=100,
    sampling="real_random",
    crossover="real_sbx",
    mutation="real_pm"
)
```

**Available strings:**
- Sampling: `"real_random"`, `"real_lhs"`, `"bin_random"`, `"perm_random"`
- Crossover: `"real_sbx"`, `"real_de"`, `"int_sbx"`, `"bin_ux"`, `"bin_hux"`
- Mutation: `"real_pm"`, `"int_pm"`, `"bin_bitflip"`, `"perm_inv"`

## Operator Combination Examples

### Standard Continuous GA:
```python
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.selection.tournament import TournamentSelection

sampling = FloatRandomSampling()
crossover = SBX(prob=0.9, eta=15)
mutation = PM(eta=20)
selection = TournamentSelection()
```

### Binary GA:
```python
from pymoo.operators.sampling.rnd import BinaryRandomSampling
from pymoo.operators.crossover.pntx import TwoPointCrossover
from pymoo.operators.mutation.bitflip import BitflipMutation

sampling = BinaryRandomSampling()
crossover = TwoPointCrossover()
mutation = BitflipMutation(prob=0.05)
```

### Permutation GA (TSP):
```python
from pymoo.operators.sampling.rnd import PermutationRandomSampling
from pymoo.operators.crossover.ox import OrderCrossover
from pymoo.operators.mutation.inversion import InversionMutation

sampling = PermutationRandomSampling()
crossover = OrderCrossover()
mutation = InversionMutation()
```

### `references/parallelization.md`

# Pymoo Parallelization Reference

Reference for parallel evaluation of expensive `ElementwiseProblem` instances.

## When to Use

Use parallelization when `_evaluate` is the bottleneck (simulations, ML inference, external solvers). Pymoo evaluates one solution per `_evaluate` call for `ElementwiseProblem`; pass a runner to evaluate multiple solutions concurrently.

**Requirements:**
- Subclass `ElementwiseProblem` (not vectorized `Problem`)
- Set `elementwise_evaluation=True` (default for `ElementwiseProblem`)
- Pass `elementwise_runner` to the problem constructor

## Starmap Interface (Threads or Processes)

Uses Python's `multiprocessing.Pool.starmap` interface via `StarmapParallelization`.

```python
import multiprocessing
from multiprocessing.pool import ThreadPool

from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.core.problem import ElementwiseProblem
from pymoo.optimize import minimize
from pymoo.parallelization.starmap import StarmapParallelization


class MyProblem(ElementwiseProblem):
    def __init__(self, elementwise_runner=None, **kwargs):
        super().__init__(
            n_var=10, n_obj=1, xl=-5, xu=5,
            elementwise_runner=elementwise_runner,
            **kwargs,
        )

    def _evaluate(self, x, out, *args, **kwargs):
        out["F"] = (x ** 2).sum()


# Thread pool (shared memory; good for I/O-bound evaluation)
n_threads = 4
pool = ThreadPool(n_threads)
runner = StarmapParallelization(pool.starmap)
problem = MyProblem(elementwise_runner=runner)

result = minimize(problem, GA(), ("n_gen", 50), seed=1)
pool.close()

# Process pool (separate memory; good for CPU-bound evaluation)
n_processes = 4
pool = multiprocessing.Pool(n_processes)
runner = StarmapParallelization(pool.starmap)
problem = MyProblem(elementwise_runner=runner)

result = minimize(problem, GA(), ("n_gen", 50), seed=1)
pool.close()
```

## Joblib Interface

Alternative using the joblib library:

```python
from joblib import Parallel, delayed
from pymoo.parallelization.joblib import JoblibParallelization

runner = JoblibParallelization(lambda func, X: Parallel(n_jobs=4)(delayed(func)(x) for x in X))
problem = MyProblem(elementwise_runner=runner)
```

Install joblib if needed: `uv pip install joblib`

## Notes

- Always close the pool after `minimize()` completes
- Process pools require picklable problem definitions (avoid lambdas in class bodies)
- Parallelization speedup depends on evaluation cost vs. overhead
- For vectorized problems (`Problem` subclass evaluating batches), implement batching inside `_evaluate` instead

**Documentation:** https://pymoo.org/parallelization/starmap.html

### `references/problems.md`

# Pymoo Test Problems Reference

Comprehensive reference for benchmark optimization problems in pymoo.

## Single-Objective Test Problems

### Ackley Function
**Characteristics:**
- Highly multimodal
- Many local optima
- Tests algorithm's ability to escape local minima
- Continuous variables

### Griewank Function
**Characteristics:**
- Multimodal with regularly distributed local minima
- Product term introduces interdependencies between variables
- Global minimum at origin

### Rastrigin Function
**Characteristics:**
- Highly multimodal with regularly spaced local minima
- Challenging for gradient-based methods
- Tests global search capability

### Rosenbrock Function
**Characteristics:**
- Unimodal but narrow valley to global optimum
- Tests algorithm's convergence in difficult landscape
- Classic benchmark for continuous optimization

### Zakharov Function
**Characteristics:**
- Unimodal
- Single global minimum
- Tests basic convergence capability

## Multi-Objective Test Problems (2-3 objectives)

### ZDT Test Suite
**Purpose:** Standard benchmark for bi-objective optimization
**Construction:** f₂(x) = g(x) · h(f₁(x), g(x)) where g(x) = 1 at Pareto-optimal solutions

#### ZDT1
- **Variables:** 30 continuous
- **Bounds:** [0, 1]
- **Pareto front:** Convex
- **Purpose:** Basic convergence and diversity test

#### ZDT2
- **Variables:** 30 continuous
- **Bounds:** [0, 1]
- **Pareto front:** Non-convex (concave)
- **Purpose:** Tests handling of non-convex fronts

#### ZDT3
- **Variables:** 30 continuous
- **Bounds:** [0, 1]
- **Pareto front:** Disconnected (5 separate regions)
- **Purpose:** Tests diversity maintenance across discontinuous front

#### ZDT4
- **Variables:** 10 continuous (x₁ ∈ [0,1], x₂₋₁₀ ∈ [-10,10])
- **Pareto front:** Convex
- **Difficulty:** 21⁹ local Pareto fronts
- **Purpose:** Tests global search with many local optima

#### ZDT5
- **Variables:** 11 discrete (bitstring)
- **Encoding:** x₁ uses 30 bits, x₂₋₁₁ use 5 bits each
- **Pareto front:** Convex
- **Purpose:** Tests discrete optimization and deceptive landscapes

#### ZDT6
- **Variables:** 10 continuous
- **Bounds:** [0, 1]
- **Pareto front:** Non-convex with non-uniform density
- **Purpose:** Tests handling of biased solution distributions

**Usage:**
```python
from pymoo.problems.multi import ZDT1, ZDT2, ZDT3, ZDT4, ZDT5, ZDT6
problem = ZDT1()  # or ZDT2(), ZDT3(), etc.
```

### BNH (Binh and Korn)
**Characteristics:**
- 2 objectives
- 2 variables
- Constrained problem
- Tests constraint handling in multi-objective context

### OSY (Osyczka and Kundu)
**Characteristics:**
- 6 objectives
- 6 variables
- Multiple constraints
- Real-world inspired

### TNK (Tanaka)
**Characteristics:**
- 2 objectives
- 2 variables
- Disconnected feasible region
- Tests handling of disjoint search spaces

### Truss2D
**Characteristics:**
- Structural engineering problem
- Bi-objective (weight vs displacement)
- Practical application test

### Welded Beam
**Characteristics:**
- Engineering design problem
- Multiple constraints
- Practical optimization scenario

### Omni-test
**Characteristics:**
- Configurable test problem
- Various difficulty levels
- Systematic testing

### SYM-PART
**Characteristics:**
- Symmetric problem structure
- Tests specific algorithmic behaviors

## Many-Objective Test Problems (4+ objectives)

### DTLZ Test Suite
**Purpose:** Scalable many-objective benchmarks
**Objectives:** Configurable (typically 3-15)
**Variables:** Scalable

#### DTLZ1
- **Pareto front:** Linear (hyperplane)
- **Difficulty:** 11^k local Pareto fronts
- **Purpose:** Tests convergence with many local optima

#### DTLZ2
- **Pareto front:** Spherical (concave)
- **Difficulty:** Straightforward convergence
- **Purpose:** Basic many-objective diversity test

#### DTLZ3
- **Pareto front:** Spherical
- **Difficulty:** 3^k local Pareto fronts
- **Purpose:** Combines DTLZ1's multimodality with DTLZ2's geometry

#### DTLZ4
- **Pareto front:** Spherical with biased density
- **Difficulty:** Non-uniform solution distribution
- **Purpose:** Tests diversity maintenance with bias

#### DTLZ5
- **Pareto front:** Degenerate (curve in M-dimensional space)
- **Purpose:** Tests handling of degenerate fronts

#### DTLZ6
- **Pareto front:** Degenerate curve
- **Difficulty:** Harder convergence than DTLZ5
- **Purpose:** Challenging degenerate front

#### DTLZ7
- **Pareto front:** Disconnected regions
- **Difficulty:** 2^(M-1) disconnected regions
- **Purpose:** Tests diversity across disconnected fronts

**Usage:**
```python
from pymoo.problems.many import DTLZ1, DTLZ2
problem = DTLZ1(n_var=7, n_obj=3)  # 7 variables, 3 objectives
```

### WFG Test Suite
**Purpose:** Walking Fish Group scalable benchmarks
**Features:** More complex than DTLZ, various front shapes and difficulties

**Variants:** WFG1-WFG9 with different characteristics
- Non-separable
- Deceptive
- Multimodal
- Biased
- Scaled fronts

## Constrained Multi-Objective Problems

### MW Test Suite
**Purpose:** Multi-objective problems with various constraint types
**Features:** Different constraint difficulty levels

### DAS-CMOP
**Purpose:** Difficulty-adjustable and scalable constrained multi-objective problems
**Features:** Tunable constraint difficulty

### MODAct
**Purpose:** Multi-objective optimization with active constraints
**Features:** Realistic constraint scenarios

## Dynamic Multi-Objective Problems

### DF Test Suite
**Purpose:** CEC2018 Competition dynamic multi-objective benchmarks
**Features:**
- Time-varying objectives
- Changing Pareto fronts
- Tests algorithm adaptability

**Variants:** DF1-DF14 with different dynamics

## Custom Problem Definition

Define custom problems by extending base classes:

```python
from pymoo.core.problem import ElementwiseProblem
import numpy as np

class MyProblem(ElementwiseProblem):
    def __init__(self):
        super().__init__(
            n_var=2,           # number of variables
            n_obj=2,           # number of objectives
            n_ieq_constr=0,    # inequality constraints
            n_eq_constr=0,     # equality constraints
            xl=np.array([0, 0]),   # lower bounds
            xu=np.array([1, 1])    # upper bounds
        )

    def _evaluate(self, x, out, *args, **kwargs):
        # Define objectives
        f1 = x[0]**2 + x[1]**2
        f2 = (x[0]-1)**2 + x[1]**2

        out["F"] = [f1, f2]

        # Optional: constraints
        # out["G"] = constraint_values  # <= 0
        # out["H"] = equality_constraints  # == 0
```

## Problem Selection Guidelines

**For algorithm development:**
- Simple convergence: DTLZ2, ZDT1
- Multimodal: ZDT4, DTLZ1, DTLZ3
- Non-convex: ZDT2
- Disconnected: ZDT3, DTLZ7

**For comprehensive testing:**
- ZDT suite for bi-objective
- DTLZ suite for many-objective
- WFG for complex landscapes
- MW/DAS-CMOP for constraints

**For real-world validation:**
- Engineering problems (Truss2D, Welded Beam)
- Match problem characteristics to application domain

**Variable types:**
- Continuous: Most problems
- Discrete: ZDT5
- Mixed: Define custom problem

### `references/quick_start_workflows.md`

# Quick Start Workflows

Nine runnable workflows: single-objective, multi-objective (2-3 objectives),
many-objective (4+), custom problem definition, constraint handling, decision making from
a Pareto front, visualization, parallel evaluation, and mixed-variable optimization.

## Quick Start Workflows

### Workflow 1: Single-Objective Optimization

**When:** Optimizing one objective function

**Steps:**
1. Define or select problem
2. Choose single-objective algorithm (GA, DE, PSO, CMA-ES)
3. Configure termination criteria
4. Run optimization
5. Extract best solution

**Example:**
```python
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.problems import get_problem
from pymoo.optimize import minimize

# Built-in problem
problem = get_problem("rastrigin", n_var=10)

# Configure Genetic Algorithm
algorithm = GA(
    pop_size=100,
    eliminate_duplicates=True
)

# Optimize
result = minimize(
    problem,
    algorithm,
    ('n_gen', 200),
    seed=1,
    verbose=True
)

print(f"Best solution: {result.X}")
print(f"Best objective: {result.F[0]}")
```

**See:** `scripts/single_objective_example.py` for complete example

### Workflow 2: Multi-Objective Optimization (2-3 objectives)

**When:** Optimizing 2-3 conflicting objectives, need Pareto front

**Algorithm choice:** NSGA-II (standard for bi/tri-objective)

**Steps:**
1. Define multi-objective problem
2. Configure NSGA-II
3. Run optimization to obtain Pareto front
4. Visualize trade-offs
5. Apply decision making (optional)

**Example:**
```python
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.problems import get_problem
from pymoo.optimize import minimize
from pymoo.visualization.scatter import Scatter

# Bi-objective benchmark problem
problem = get_problem("zdt1")

# NSGA-II algorithm
algorithm = NSGA2(pop_size=100)

# Optimize
result = minimize(problem, algorithm, ('n_gen', 200), seed=1)

# Visualize Pareto front
plot = Scatter()
plot.add(result.F, label="Obtained Front")
plot.add(problem.pareto_front(), label="True Front", alpha=0.3)
plot.show()

print(f"Found {len(result.F)} Pareto-optimal solutions")
```

**See:** `scripts/multi_objective_example.py` for complete example

### Workflow 3: Many-Objective Optimization (4+ objectives)

**When:** Optimizing 4 or more objectives

**Algorithm choice:** NSGA-III (designed for many objectives)

**Key difference:** Must provide reference directions for population guidance

**Steps:**
1. Define many-objective problem
2. Generate reference directions
3. Configure NSGA-III with reference directions
4. Run optimization
5. Visualize using Parallel Coordinate Plot

**Example:**
```python
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.problems import get_problem
from pymoo.optimize import minimize
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.visualization.pcp import PCP

# Many-objective problem (5 objectives)
problem = get_problem("dtlz2", n_obj=5)

# Generate reference directions (required for NSGA-III)
ref_dirs = get_reference_directions("das-dennis", 5, n_partitions=12)  # n_dim is positional

# Configure NSGA-III
algorithm = NSGA3(ref_dirs=ref_dirs)

# Optimize
result = minimize(problem, algorithm, ('n_gen', 300), seed=1)

# Visualize with Parallel Coordinates
plot = PCP(labels=[f"f{i+1}" for i in range(5)])
plot.add(result.F, alpha=0.3)
plot.show()
```

**See:** `scripts/many_objective_example.py` for complete example

### Workflow 4: Custom Problem Definition

**When:** Solving domain-specific optimization problem

**Steps:**
1. Extend `ElementwiseProblem` class
2. Define `__init__` with problem dimensions and bounds
3. Implement `_evaluate` method for objectives (and constraints)
4. Use with any algorithm

**Unconstrained example:**
```python
from pymoo.core.problem import ElementwiseProblem
import numpy as np

class MyProblem(ElementwiseProblem):
    def __init__(self):
        super().__init__(
            n_var=2,              # Number of variables
            n_obj=2,              # Number of objectives
            xl=np.array([0, 0]),  # Lower bounds
            xu=np.array([5, 5])   # Upper bounds
        )

    def _evaluate(self, x, out, *args, **kwargs):
        # Define objectives
        f1 = x[0]**2 + x[1]**2
        f2 = (x[0]-1)**2 + (x[1]-1)**2

        out["F"] = [f1, f2]
```

**Constrained example:**
```python
class ConstrainedProblem(ElementwiseProblem):
    def __init__(self):
        super().__init__(
            n_var=2,
            n_obj=2,
            n_ieq_constr=2,        # Inequality constraints
            n_eq_constr=1,         # Equality constraints
            xl=np.array([0, 0]),
            xu=np.array([5, 5])
        )

    def _evaluate(self, x, out, *args, **kwargs):
        # Objectives
        out["F"] = [f1, f2]

        # Inequality constraints (g <= 0)
        out["G"] = [g1, g2]

        # Equality constraints (h = 0)
        out["H"] = [h1]
```

**Constraint formulation rules:**
- Inequality: Express as `g(x) <= 0` (feasible when ≤ 0)
- Equality: Express as `h(x) = 0` (feasible when = 0)
- Convert `g(x) >= b` to `-(g(x) - b) <= 0`

**See:** `scripts/custom_problem_example.py` for complete examples

### Workflow 5: Constraint Handling

**When:** Problem has feasibility constraints

**Approach options:**

**1. Feasibility First (Default - Recommended)**
```python
from pymoo.algorithms.moo.nsga2 import NSGA2

# Works automatically with constrained problems
algorithm = NSGA2(pop_size=100)
result = minimize(problem, algorithm, termination)

# Check feasibility
feasible = result.CV[:, 0] == 0  # CV = constraint violation
print(f"Feasible solutions: {np.sum(feasible)}")
```

**2. Penalty Method**
```python
from pymoo.constraints.as_penalty import ConstraintsAsPenalty

# Wrap problem to convert constraints to penalties
problem_penalized = ConstraintsAsPenalty(problem, penalty=1e6)
```

**3. Constraint as Objective**
```python
from pymoo.constraints.as_obj import ConstraintsAsObjective

# Treat constraint violation as additional objective
problem_with_cv = ConstraintsAsObjective(problem)
```

**4. Specialized Algorithms**
```python
from pymoo.algorithms.soo.nonconvex.sres import SRES

# SRES has built-in constraint handling
algorithm = SRES()
```

**See:** `references/constraints_mcdm.md` for comprehensive constraint handling guide

### Workflow 6: Decision Making from Pareto Front

**When:** Have Pareto front, need to select preferred solution(s)

**Steps:**
1. Run multi-objective optimization
2. Normalize objectives to [0, 1]
3. Define preference weights
4. Apply MCDM method
5. Visualize selected solution

**Example using Pseudo-Weights:**
```python
from pymoo.mcdm.pseudo_weights import PseudoWeights
import numpy as np

# After obtaining result from multi-objective optimization
# Normalize objectives
F_norm = (result.F - result.F.min(axis=0)) / (result.F.max(axis=0) - result.F.min(axis=0))

# Define preferences (must sum to 1)
weights = np.array([0.3, 0.7])  # 30% f1, 70% f2

# Apply decision making
dm = PseudoWeights(weights)
selected_idx = dm.do(F_norm)

# Get selected solution
best_solution = result.X[selected_idx]
best_objectives = result.F[selected_idx]

print(f"Selected solution: {best_solution}")
print(f"Objective values: {best_objectives}")
```

**Other MCDM methods:**
- Compromise Programming: Select closest to ideal point
- Knee Point: Find balanced trade-off solutions
- Hypervolume Contribution: Select most diverse subset

**See:**
- `scripts/decision_making_example.py` for complete example
- `references/constraints_mcdm.md` for detailed MCDM methods

### Workflow 7: Visualization

**Choose visualization based on number of objectives:**

**2 objectives: Scatter Plot**
```python
from pymoo.visualization.scatter import Scatter

plot = Scatter(title="Bi-objective Results")
plot.add(result.F, color="blue", alpha=0.7)
plot.show()
```

**3 objectives: 3D Scatter**
```python
plot = Scatter(title="Tri-objective Results")
plot.add(result.F)  # Automatically renders in 3D
plot.show()
```

**4+ objectives: Parallel Coordinate Plot**
```python
from pymoo.visualization.pcp import PCP

plot = PCP(
    labels=[f"f{i+1}" for i in range(n_obj)],
    normalize_each_axis=True
)
plot.add(result.F, alpha=0.3)
plot.show()
```

**Solution comparison: Petal Diagram**
```python
from pymoo.visualization.petal import Petal

plot = Petal(
    bounds=[result.F.min(axis=0), result.F.max(axis=0)],
    labels=["Cost", "Weight", "Efficiency"]
)
plot.add(solution_A, label="Design A")
plot.add(solution_B, label="Design B")
plot.show()
```

**See:** `references/visualization.md` for all visualization types and usage

### Workflow 8: Parallel Evaluation

**When:** Each `_evaluate` call is expensive (simulations, ML models, external solvers)

**Approach:** Pass an `elementwise_runner` to `ElementwiseProblem` using `StarmapParallelization` or `JoblibParallelization`.

**Example (thread pool):**
```python
from multiprocessing.pool import ThreadPool
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.core.problem import ElementwiseProblem
from pymoo.optimize import minimize
from pymoo.parallelization.starmap import StarmapParallelization

class MyProblem(ElementwiseProblem):
    def __init__(self, elementwise_runner=None, **kwargs):
        super().__init__(
            n_var=10, n_obj=1, xl=-5, xu=5,
            elementwise_runner=elementwise_runner, **kwargs,
        )

    def _evaluate(self, x, out, *args, **kwargs):
        out["F"] = (x ** 2).sum()  # Replace with expensive evaluation

pool = ThreadPool(4)
runner = StarmapParallelization(pool.starmap)
problem = MyProblem(elementwise_runner=runner)

result = minimize(problem, GA(), ("n_gen", 50), seed=1)
pool.close()
```

**See:** `references/parallelization.md` for process pools, joblib, and pickling notes

### Workflow 9: Mixed-Variable Optimization

**When:** Decision variables include continuous, integer, binary, and/or categorical types

**Approach:** Define a `vars` dict with typed variables; use `MixedVariableGA` (SOO) or add MOO survival.

**Example:**
```python
from pymoo.core.problem import ElementwiseProblem
from pymoo.core.variable import Real, Integer, Choice, Binary
from pymoo.core.mixed import MixedVariableGA
from pymoo.optimize import minimize

class MixedProblem(ElementwiseProblem):
    def __init__(self, **kwargs):
        vars = {
            "b": Binary(),
            "x": Choice(options=["nothing", "multiply"]),
            "y": Integer(bounds=(0, 2)),
            "z": Real(bounds=(0, 5)),
        }
        super().__init__(vars=vars, n_obj=1, **kwargs)

    def _evaluate(self, X, out, *args, **kwargs):
        b, x, z, y = X["b"], X["x"], X["z"], X["y"]
        f = z + y
        if b:
            f = 100 * f
        if x == "multiply":
            f = 10 * f
        out["F"] = f

algorithm = MixedVariableGA(pop_size=20)
result = minimize(MixedProblem(), algorithm, ("n_evals", 1000), seed=1)
```

For multi-objective mixed-variable problems, use `MixedVariableGA(pop_size=20, survival=RankAndCrowdingSurvival())`. For single-objective mixed search, pymoo also wraps [Optuna](https://optuna.org) via `pymoo.algorithms.soo.nonconvex.optuna.Optuna`.

**See:** `references/algorithms.md` for MixedVariableGA and Optuna details

### `references/visualization.md`

# Pymoo Visualization Reference

Comprehensive reference for visualization capabilities in pymoo.

## Overview

Pymoo provides eight visualization types for analyzing multi-objective optimization results. All plots wrap matplotlib and accept standard matplotlib keyword arguments for customization.

## Core Visualization Types

### 1. Scatter Plots
**Purpose:** Visualize objective space for 2D, 3D, or higher dimensions
**Best for:** Pareto fronts, solution distributions, algorithm comparisons

**Usage:**
```python
from pymoo.visualization.scatter import Scatter

# 2D scatter plot
plot = Scatter()
plot.add(result.F, color="red", label="Algorithm A")
plot.add(ref_pareto_front, color="black", alpha=0.3, label="True PF")
plot.show()

# 3D scatter plot
plot = Scatter(title="3D Pareto Front")
plot.add(result.F)
plot.show()
```

**Parameters:**
- `title`: Plot title
- `figsize`: Figure size tuple (width, height)
- `legend`: Show legend (default: True)
- `labels`: Axis labels list

**Add method parameters:**
- `color`: Color specification
- `alpha`: Transparency (0-1)
- `s`: Marker size
- `marker`: Marker style
- `label`: Legend label

**N-dimensional projection:**
For >3 objectives, automatically creates scatter plot matrix

### 2. Parallel Coordinate Plots (PCP)
**Purpose:** Compare multiple solutions across many objectives
**Best for:** Many-objective problems, comparing algorithm performance

**Mechanism:** Each vertical axis represents one objective, lines connect objective values for each solution

**Usage:**
```python
from pymoo.visualization.pcp import PCP

plot = PCP()
plot.add(result.F, color="blue", alpha=0.5)
plot.add(reference_set, color="red", alpha=0.8)
plot.show()
```

**Parameters:**
- `title`: Plot title
- `figsize`: Figure size
- `labels`: Objective labels
- `bounds`: Normalization bounds (min, max) per objective
- `normalize_each_axis`: Normalize to [0,1] per axis (default: True)

**Best practices:**
- Normalize for different objective scales
- Use transparency for overlapping lines
- Limit number of solutions for clarity (<1000)

### 3. Heatmap
**Purpose:** Show solution density and distribution patterns
**Best for:** Understanding solution clustering, identifying gaps

**Usage:**
```python
from pymoo.visualization.heatmap import Heatmap

plot = Heatmap(title="Solution Density")
plot.add(result.F)
plot.show()
```

**Parameters:**
- `bins`: Number of bins per dimension (default: 20)
- `cmap`: Colormap name (e.g., "viridis", "plasma", "hot")
- `norm`: Normalization method

**Interpretation:**
- Bright regions: High solution density
- Dark regions: Few or no solutions
- Reveals distribution uniformity

### 4. Petal Diagram
**Purpose:** Radial representation of multiple objectives
**Best for:** Comparing individual solutions across objectives

**Structure:** Each "petal" represents one objective, length indicates objective value

**Usage:**
```python
from pymoo.visualization.petal import Petal

plot = Petal(title="Solution Comparison", bounds=[min_vals, max_vals])
plot.add(result.F[0], color="blue", label="Solution 1")
plot.add(result.F[1], color="red", label="Solution 2")
plot.show()
```

**Parameters:**
- `bounds`: [min, max] per objective for normalization
- `labels`: Objective names
- `reverse`: Reverse specific objectives (for minimization display)

**Use cases:**
- Decision making between few solutions
- Presenting trade-offs to stakeholders

### 5. Radar Charts
**Purpose:** Multi-criteria performance profiles
**Best for:** Comparing solution characteristics

**Similar to:** Petal diagram but with connected vertices

**Usage:**
```python
from pymoo.visualization.radar import Radar

plot = Radar(bounds=[min_vals, max_vals])
plot.add(solution_A, label="Design A")
plot.add(solution_B, label="Design B")
plot.show()
```

### 6. Radviz
**Purpose:** Dimensional reduction for visualization
**Best for:** High-dimensional data exploration, pattern recognition

**Mechanism:** Projects high-dimensional points onto 2D circle, dimension anchors on perimeter

**Usage:**
```python
from pymoo.visualization.radviz import Radviz

plot = Radviz(title="High-dimensional Solution Space")
plot.add(result.F, color="blue", s=30)
plot.show()
```

**Parameters:**
- `endpoint_style`: Anchor point visualization
- `labels`: Dimension labels

**Interpretation:**
- Points near anchor: High value in that dimension
- Central points: Balanced across dimensions
- Clusters: Similar solutions

### 7. Star Coordinates
**Purpose:** Alternative high-dimensional visualization
**Best for:** Comparing multi-dimensional datasets

**Mechanism:** Each dimension as axis from origin, points plotted based on values

**Usage:**
```python
from pymoo.visualization.star_coordinate import StarCoordinate

plot = StarCoordinate()
plot.add(result.F)
plot.show()
```

**Parameters:**
- `axis_style`: Axis appearance
- `axis_extension`: Axis length beyond max value
- `labels`: Dimension labels

### 8. Video/Animation
**Purpose:** Show optimization progress over time
**Best for:** Understanding convergence behavior, presentations

**Usage:**
```python
from pymoo.visualization.video import Video

# Create animation from algorithm history
anim = Video(result.algorithm)
anim.save("optimization_progress.mp4")
```

**Requirements:**
- Algorithm must store history (use `save_history=True` in minimize)
- ffmpeg installed for video export

**Customization:**
- Frame rate
- Plot type per frame
- Overlay information (generation, hypervolume, etc.)

## Advanced Features

### Multiple Dataset Overlay

All plot types support adding multiple datasets:

```python
plot = Scatter(title="Algorithm Comparison")
plot.add(nsga2_result.F, color="red", alpha=0.5, label="NSGA-II")
plot.add(nsga3_result.F, color="blue", alpha=0.5, label="NSGA-III")
plot.add(true_pareto_front, color="black", linewidth=2, label="True PF")
plot.show()
```

### Custom Styling

Pass matplotlib kwargs directly:

```python
plot = Scatter(
    title="My Results",
    figsize=(10, 8),
    tight_layout=True
)
plot.add(
    result.F,
    color="red",
    marker="o",
    s=50,
    alpha=0.7,
    edgecolors="black",
    linewidth=0.5
)
```

### Normalization

Normalize objectives to [0,1] for fair comparison:

```python
plot = PCP(normalize_each_axis=True, bounds=[min_bounds, max_bounds])
```

### Save to File

Save plots instead of displaying:

```python
plot = Scatter()
plot.add(result.F)
plot.save("my_plot.png", dpi=300)
```

## Visualization Selection Guide

**Choose visualization based on:**

| Problem Type | Primary Plot | Secondary Plot |
|--------------|--------------|----------------|
| 2-objective | Scatter | Heatmap |
| 3-objective | 3D Scatter | Parallel Coordinates |
| Many-objective (4-10) | Parallel Coordinates | Radviz |
| Many-objective (>10) | Radviz | Star Coordinates |
| Solution comparison | Petal/Radar | Parallel Coordinates |
| Algorithm convergence | Video | Scatter (final) |
| Distribution analysis | Heatmap | Scatter |

**Combinations:**
- Scatter + Heatmap: Overall distribution + density
- PCP + Petal: Population overview + individual solutions
- Scatter + Video: Final result + convergence process

## Common Visualization Workflows

### 1. Algorithm Comparison
```python
from pymoo.visualization.scatter import Scatter

plot = Scatter(title="Algorithm Comparison on ZDT1")
plot.add(ga_result.F, color="blue", label="GA", alpha=0.6)
plot.add(nsga2_result.F, color="red", label="NSGA-II", alpha=0.6)
plot.add(zdt1.pareto_front(), color="black", label="True PF")
plot.show()
```

### 2. Many-objective Analysis
```python
from pymoo.visualization.pcp import PCP

plot = PCP(
    title="5-objective DTLZ2 Results",
    labels=["f1", "f2", "f3", "f4", "f5"],
    normalize_each_axis=True
)
plot.add(result.F, alpha=0.3)
plot.show()
```

### 3. Decision Making
```python
from pymoo.visualization.petal import Petal

# Compare top 3 solutions
candidates = result.F[:3]

plot = Petal(
    title="Top 3 Solutions",
    bounds=[result.F.min(axis=0), result.F.max(axis=0)],
    labels=["Cost", "Weight", "Efficiency", "Safety"]
)
for i, sol in enumerate(candidates):
    plot.add(sol, label=f"Solution {i+1}")
plot.show()
```

### 4. Convergence Visualization
```python
from pymoo.optimize import minimize

# Enable history
result = minimize(
    problem,
    algorithm,
    ('n_gen', 200),
    seed=1,
    save_history=True,
    verbose=False
)

# Create convergence plot
from pymoo.visualization.scatter import Scatter

plot = Scatter(title="Convergence Over Generations")
for gen in [0, 50, 100, 150, 200]:
    F = result.history[gen].opt.get("F")
    plot.add(F, alpha=0.5, label=f"Gen {gen}")
plot.show()
```

## Tips and Best Practices

1. **Use appropriate alpha:** For overlapping points, use `alpha=0.3-0.7`
2. **Normalize objectives:** Different scales? Normalize for fair visualization
3. **Label clearly:** Always provide meaningful labels and legends
4. **Limit data points:** >10000 points? Sample or use heatmap
5. **Color schemes:** Use colorblind-friendly palettes
6. **Save high-res:** Use `dpi=300` for publications
7. **Interactive exploration:** Consider plotly for interactive plots
8. **Combine views:** Show multiple perspectives for comprehensive analysis

### `scripts/custom_problem_example.py`

```python
"""
Custom problem definition example using pymoo.

This script demonstrates how to define a custom optimization problem
and solve it using pymoo.
"""

from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.visualization.scatter import Scatter
import numpy as np


class MyBiObjectiveProblem(ElementwiseProblem):
    """
    Custom bi-objective optimization problem.

    Minimize:
        f1(x) = x1^2 + x2^2
        f2(x) = (x1-1)^2 + (x2-1)^2

    Subject to:
        0 <= x1 <= 5
        0 <= x2 <= 5
    """

    def __init__(self):
        super().__init__(
            n_var=2,                    # Number of decision variables
            n_obj=2,                    # Number of objectives
            n_ieq_constr=0,            # Number of inequality constraints
            n_eq_constr=0,             # Number of equality constraints
            xl=np.array([0, 0]),       # Lower bounds
            xu=np.array([5, 5])        # Upper bounds
        )

    def _evaluate(self, x, out, *args, **kwargs):
        """Evaluate objectives for a single solution."""
        # Objective 1: Distance from origin
        f1 = x[0]**2 + x[1]**2

        # Objective 2: Distance from (1, 1)
        f2 = (x[0] - 1)**2 + (x[1] - 1)**2

        # Return objectives
        out["F"] = [f1, f2]


class ConstrainedProblem(ElementwiseProblem):
    """
    Custom constrained bi-objective problem.

    Minimize:
        f1(x) = x1
        f2(x) = (1 + x2) / x1

    Subject to:
        x2 + 9*x1 >= 6          (g1 <= 0)
        -x2 + 9*x1 >= 1         (g2 <= 0)
        0.1 <= x1 <= 1
        0 <= x2 <= 5
    """

    def __init__(self):
        super().__init__(
            n_var=2,
            n_obj=2,
            n_ieq_constr=2,            # Two inequality constraints
            xl=np.array([0.1, 0.0]),
            xu=np.array([1.0, 5.0])
        )

    def _evaluate(self, x, out, *args, **kwargs):
        """Evaluate objectives and constraints."""
        # Objectives
        f1 = x[0]
        f2 = (1 + x[1]) / x[0]

        out["F"] = [f1, f2]

        # Inequality constraints (g <= 0)
        # Convert g1: x2 + 9*x1 >= 6  →  -(x2 + 9*x1 - 6) <= 0
        g1 = -(x[1] + 9 * x[0] - 6)

        # Convert g2: -x2 + 9*x1 >= 1  →  -(-x2 + 9*x1 - 1) <= 0
        g2 = -(-x[1] + 9 * x[0] - 1)

        out["G"] = [g1, g2]


def solve_custom_problem():
    """Solve custom bi-objective problem."""

    print("="*60)
    print("CUSTOM PROBLEM - UNCONSTRAINED")
    print("="*60)

    # Define custom problem
    problem = MyBiObjectiveProblem()

    # Configure algorithm
    algorithm = NSGA2(pop_size=100)

    # Solve
    result = minimize(
        problem,
        algorithm,
        ('n_gen', 200),
        seed=1,
        verbose=False
    )

    print(f"Number of solutions: {len(result.F)}")
    print(f"Objective space range:")
    print(f"  f1: [{result.F[:, 0].min():.3f}, {result.F[:, 0].max():.3f}]")
    print(f"  f2: [{result.F[:, 1].min():.3f}, {result.F[:, 1].max():.3f}]")

    # Visualize
    plot = Scatter(title="Custom Bi-Objective Problem")
    plot.add(result.F, color="blue", alpha=0.7)
    plot.show()

    return result


def solve_constrained_problem():
    """Solve custom constrained problem."""

    print("\n" + "="*60)
    print("CUSTOM PROBLEM - CONSTRAINED")
    print("="*60)

    # Define constrained problem
    problem = ConstrainedProblem()

    # Configure algorithm
    algorithm = NSGA2(pop_size=100)

    # Solve
    result = minimize(
        problem,
        algorithm,
        ('n_gen', 200),
        seed=1,
        verbose=False
    )

    # Check feasibility
    feasible = result.CV[:, 0] == 0  # Constraint violation = 0

    print(f"Total solutions: {len(result.F)}")
    print(f"Feasible solutions: {np.sum(feasible)}")
    print(f"Infeasible solutions: {np.sum(~feasible)}")

    if np.any(feasible):
        F_feasible = result.F[feasible]
        print(f"\nFeasible objective space range:")
        print(f"  f1: [{F_feasible[:, 0].min():.3f}, {F_feasible[:, 0].max():.3f}]")
        print(f"  f2: [{F_feasible[:, 1].min():.3f}, {F_feasible[:, 1].max():.3f}]")

        # Visualize feasible solutions
        plot = Scatter(title="Constrained Problem - Feasible Solutions")
        plot.add(F_feasible, color="green", alpha=0.7, label="Feasible")

        if np.any(~feasible):
            plot.add(result.F[~feasible], color="red", alpha=0.3, s=10, label="Infeasible")

        plot.show()

    return result


if __name__ == "__main__":
    # Run both examples
    result1 = solve_custom_problem()
    result2 = solve_constrained_problem()

    print("\n" + "="*60)
    print("EXAMPLES COMPLETED")
    print("="*60)
```

### `scripts/decision_making_example.py`

```python
"""
Multi-criteria decision making example using pymoo.

This script demonstrates how to select preferred solutions from
a Pareto front using various MCDM methods.
"""

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.problems import get_problem
from pymoo.optimize import minimize
from pymoo.mcdm.pseudo_weights import PseudoWeights
from pymoo.visualization.scatter import Scatter
from pymoo.visualization.petal import Petal
import numpy as np


def run_optimization_for_decision_making():
    """Run optimization to obtain Pareto front."""

    print("Running optimization to obtain Pareto front...")

    # Solve ZDT1 problem
    problem = get_problem("zdt1")
    algorithm = NSGA2(pop_size=100)

    result = minimize(
        problem,
        algorithm,
        ('n_gen', 200),
        seed=1,
        verbose=False
    )

    print(f"Obtained {len(result.F)} solutions in Pareto front\n")

    return problem, result


def apply_pseudo_weights(result, weights):
    """Apply pseudo-weights MCDM method."""

    print(f"Applying Pseudo-Weights with weights: {weights}")

    # Normalize objectives to [0, 1]
    F_norm = (result.F - result.F.min(axis=0)) / (result.F.max(axis=0) - result.F.min(axis=0))

    # Apply MCDM
    dm = PseudoWeights(weights)
    selected_idx = dm.do(F_norm)

    selected_x = result.X[selected_idx]
    selected_f = result.F[selected_idx]

    print(f"Selected solution (decision variables): {selected_x}")
    print(f"Selected solution (objectives): {selected_f}")
    print()

    return selected_idx, selected_x, selected_f


def compare_different_preferences(result):
    """Compare selections with different preference weights."""

    print("="*60)
    print("COMPARING DIFFERENT PREFERENCE WEIGHTS")
    print("="*60 + "\n")

    # Define different preference scenarios
    scenarios = [
        ("Equal preference", np.array([0.5, 0.5])),
        ("Prefer f1", np.array([0.8, 0.2])),
        ("Prefer f2", np.array([0.2, 0.8])),
    ]

    selections = {}

    for name, weights in scenarios:
        print(f"Scenario: {name}")
        idx, x, f = apply_pseudo_weights(result, weights)
        selections[name] = (idx, f)

    # Visualize all selections
    plot = Scatter(title="Decision Making - Different Preferences")
    plot.add(result.F, color="lightgray", alpha=0.5, s=20, label="Pareto Front")

    colors = ["red", "blue", "green"]
    for (name, (idx, f)), color in zip(selections.items(), colors):
        plot.add(f, color=color, s=100, marker="*", label=name)

    plot.show()

    return selections


def visualize_selected_solutions(result, selections):
    """Visualize selected solutions using petal diagram."""

    # Get objective bounds for normalization
    f_min = result.F.min(axis=0)
    f_max = result.F.max(axis=0)

    plot = Petal(
        title="Selected Solutions Comparison",
        bounds=[f_min, f_max],
        labels=["f1", "f2"]
    )

    colors = ["red", "blue", "green"]
    for (name, (idx, f)), color in zip(selections.items(), colors):
        plot.add(f, color=color, label=name)

    plot.show()


def find_extreme_solutions(result):
    """Find extreme solutions (best in each objective)."""

    print("\n" + "="*60)
    print("EXTREME SOLUTIONS")
    print("="*60 + "\n")

    # Best f1 (minimize f1)
    best_f1_idx = np.argmin(result.F[:, 0])
    print(f"Best f1 solution: {result.F[best_f1_idx]}")
    print(f"  Decision variables: {result.X[best_f1_idx]}\n")

    # Best f2 (minimize f2)
    best_f2_idx = np.argmin(result.F[:, 1])
    print(f"Best f2 solution: {result.F[best_f2_idx]}")
    print(f"  Decision variables: {result.X[best_f2_idx]}\n")

    return best_f1_idx, best_f2_idx


def main():
    """Main execution function."""

    # Step 1: Run optimization
    problem, result = run_optimization_for_decision_making()

    # Step 2: Find extreme solutions
    best_f1_idx, best_f2_idx = find_extreme_solutions(result)

    # Step 3: Compare different preference weights
    selections = compare_different_preferences(result)

    # Step 4: Visualize selections with petal diagram
    visualize_selected_solutions(result, selections)

    print("="*60)
    print("DECISION MAKING EXAMPLE COMPLETED")
    print("="*60)
    print("\nKey Takeaways:")
    print("1. Different weights lead to different selected solutions")
    print("2. Higher weight on an objective selects solutions better in that objective")
    print("3. Visualization helps understand trade-offs")
    print("4. MCDM methods help formalize decision maker preferences")


if __name__ == "__main__":
    main()
```

### `scripts/many_objective_example.py`

```python
"""
Many-objective optimization example using pymoo.

This script demonstrates many-objective optimization (4+ objectives)
using NSGA-III on the DTLZ2 benchmark problem.
"""

from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.problems import get_problem
from pymoo.optimize import minimize
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.visualization.pcp import PCP
import numpy as np


def run_many_objective_optimization():
    """Run many-objective optimization example."""

    # Define the problem - DTLZ2 with 5 objectives
    n_obj = 5
    problem = get_problem("dtlz2", n_obj=n_obj)

    # Generate reference directions for NSGA-III
    # Das-Dennis method for uniform distribution.
    # The dimension is positional: the factory's first argument is n_dim, and
    # passing it as n_obj= raises TypeError.
    ref_dirs = get_reference_directions("das-dennis", n_obj, n_partitions=12)

    print(f"Number of reference directions: {len(ref_dirs)}")

    # Configure NSGA-III algorithm
    algorithm = NSGA3(
        ref_dirs=ref_dirs,
        eliminate_duplicates=True
    )

    # Run optimization
    result = minimize(
        problem,
        algorithm,
        ('n_gen', 300),
        seed=1,
        verbose=True
    )

    # Print results summary
    print("\n" + "="*60)
    print("MANY-OBJECTIVE OPTIMIZATION RESULTS")
    print("="*60)
    print(f"Number of objectives: {n_obj}")
    print(f"Number of solutions: {len(result.F)}")
    print(f"Number of generations: {result.algorithm.n_gen}")
    print(f"Number of function evaluations: {result.algorithm.evaluator.n_eval}")

    # Show objective space statistics
    print("\nObjective space statistics:")
    print(f"Minimum values per objective: {result.F.min(axis=0)}")
    print(f"Maximum values per objective: {result.F.max(axis=0)}")
    print("="*60)

    # Visualize using Parallel Coordinate Plot
    plot = PCP(
        title=f"DTLZ2 ({n_obj} objectives) - NSGA-III Results",
        labels=[f"f{i+1}" for i in range(n_obj)],
        normalize_each_axis=True
    )
    plot.add(result.F, alpha=0.3, color="blue")
    plot.show()

    return result


if __name__ == "__main__":
    result = run_many_objective_optimization()
```

### `scripts/multi_objective_example.py`

```python
"""
Multi-objective optimization example using pymoo.

This script demonstrates multi-objective optimization using
NSGA-II on the ZDT1 benchmark problem.
"""

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.problems import get_problem
from pymoo.optimize import minimize
from pymoo.visualization.scatter import Scatter
import matplotlib.pyplot as plt


def run_multi_objective_optimization():
    """Run multi-objective optimization example."""

    # Define the problem - ZDT1 (bi-objective)
    problem = get_problem("zdt1")

    # Configure NSGA-II algorithm
    algorithm = NSGA2(
        pop_size=100,
        eliminate_duplicates=True
    )

    # Run optimization
    result = minimize(
        problem,
        algorithm,
        ('n_gen', 200),
        seed=1,
        verbose=True
    )

    # Print results summary
    print("\n" + "="*60)
    print("MULTI-OBJECTIVE OPTIMIZATION RESULTS")
    print("="*60)
    print(f"Number of solutions in Pareto front: {len(result.F)}")
    print(f"Number of generations: {result.algorithm.n_gen}")
    print(f"Number of function evaluations: {result.algorithm.evaluator.n_eval}")
    print("\nFirst 5 solutions (decision variables):")
    print(result.X[:5])
    print("\nFirst 5 solutions (objective values):")
    print(result.F[:5])
    print("="*60)

    # Visualize results
    plot = Scatter(title="ZDT1 - NSGA-II Results")
    plot.add(result.F, color="red", alpha=0.7, s=30, label="Obtained Pareto Front")

    # Add true Pareto front for comparison
    pf = problem.pareto_front()
    plot.add(pf, color="black", alpha=0.3, label="True Pareto Front")

    plot.show()

    return result


if __name__ == "__main__":
    result = run_multi_objective_optimization()
```

### `scripts/single_objective_example.py`

```python
"""
Single-objective optimization example using pymoo.

This script demonstrates basic single-objective optimization
using the Genetic Algorithm on the Sphere function.
"""

from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.problems import get_problem
from pymoo.optimize import minimize
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.termination import get_termination
import numpy as np


def run_single_objective_optimization():
    """Run single-objective optimization example."""

    # Define the problem - Sphere function (sum of squares)
    problem = get_problem("sphere", n_var=10)

    # Configure the algorithm
    algorithm = GA(
        pop_size=100,
        sampling=FloatRandomSampling(),
        crossover=SBX(prob=0.9, eta=15),
        mutation=PM(eta=20),
        eliminate_duplicates=True
    )

    # Define termination criteria
    termination = get_termination("n_gen", 100)

    # Run optimization
    result = minimize(
        problem,
        algorithm,
        termination,
        seed=1,
        verbose=True
    )

    # Print results
    print("\n" + "="*60)
    print("OPTIMIZATION RESULTS")
    print("="*60)
    print(f"Best solution: {result.X}")
    print(f"Best objective value: {result.F[0]:.6f}")
    print(f"Number of generations: {result.algorithm.n_gen}")
    print(f"Number of function evaluations: {result.algorithm.evaluator.n_eval}")
    print("="*60)

    return result


if __name__ == "__main__":
    result = run_single_objective_optimization()
```
