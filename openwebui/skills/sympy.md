---
name: sympy
description: Use when you need exact symbolic math in Python — algebra, calculus, equation solving, symbolic linear algebra, or code generation via lambdify/LaTeX. Prefer NumPy or SciPy when floating-point approximations are sufficient.
---

# SymPy - Symbolic Mathematics in Python

## Overview

SymPy is a Python library for symbolic mathematics that enables exact computation using mathematical symbols rather than numerical approximations. This skill provides comprehensive guidance for performing symbolic algebra, calculus, linear algebra, equation solving, physics calculations, and code generation using SymPy.

## Installation

Tested against **SymPy 1.14.0** (stable; April 2025). Requires **Python 3.9+**.

```bash
# Install SymPy using uv
uv pip install "sympy>=1.14"

# Optional: for lambdify and plotting examples
uv pip install numpy scipy matplotlib
```

Check your version:

```python
import sympy
print(sympy.__version__)
```

## When to Use This Skill

Use this skill when:
- Solving equations symbolically (algebraic, differential, systems of equations)
- Performing calculus operations (derivatives, integrals, limits, series)
- Manipulating and simplifying algebraic expressions
- Working with matrices and linear algebra symbolically
- Doing physics calculations (mechanics, quantum mechanics, vector analysis)
- Number theory computations (primes, factorization, modular arithmetic)
- Geometric calculations (2D/3D geometry, analytic geometry)
- Converting mathematical expressions to executable code (Python, C, Fortran)
- Generating LaTeX or other formatted mathematical output
- Needing exact mathematical results (e.g., `sqrt(2)` not `1.414...`)

## Core Capabilities

Seven capability areas are documented in
[references/core_capabilities.md](references/core_capabilities.md):

1. **Symbolic computation basics** — symbols, expressions, simplification, substitution.
2. **Calculus** — differentiation, integration, limits, series.
3. **Equation solving** — `solve`, `solveset`, linear and nonlinear systems, ODEs.
4. **Matrices and linear algebra** — see
   [references/matrices-linear-algebra.md](references/matrices-linear-algebra.md).
5. **Physics and mechanics** — see
   [references/physics-mechanics.md](references/physics-mechanics.md).
6. **Advanced mathematics** — see
   [references/advanced-topics.md](references/advanced-topics.md).
7. **Code generation and output** — see
   [references/code-generation-printing.md](references/code-generation-printing.md).

Deeper treatment of the first three is in
[references/core-capabilities.md](references/core-capabilities.md).

## Working with SymPy: Best Practices

### 1. Always Define Symbols First

```python
from sympy import symbols
x, y, z = symbols('x y z')
# Now x, y, z can be used in expressions
```

### 2. Use Assumptions for Better Simplification

```python
x = symbols('x', positive=True, real=True)
sqrt(x**2)  # Returns x (not Abs(x)) due to positive assumption
```

Common assumptions: `real`, `positive`, `negative`, `integer`, `rational`, `complex`, `even`, `odd`

### 3. Use Exact Arithmetic

```python
from sympy import Rational, S
# Correct (exact):
expr = Rational(1, 2) * x
expr = S(1)/2 * x

# Incorrect (floating-point):
expr = 0.5 * x  # Creates approximate value
```

### 4. Numerical Evaluation When Needed

```python
from sympy import pi, sqrt
result = sqrt(8) + pi
result.evalf()    # 5.96371554103586
result.evalf(50)  # 50 digits of precision
```

### 5. Convert to NumPy for Performance

```python
# Slow for many evaluations:
for x_val in range(1000):
    result = expr.subs(x, x_val).evalf()

# Fast:
f = lambdify(x, expr, 'numpy')
results = f(np.arange(1000))
```

### 6. Use Appropriate Solvers

- `solveset`: Algebraic equations (primary)
- `linsolve`: Linear systems
- `nonlinsolve`: Nonlinear systems
- `dsolve`: Differential equations
- `solve`: General purpose (legacy, but flexible)

## Reference Files Structure

This skill uses modular reference files for different capabilities:

1. **`core-capabilities.md`**: Symbols, algebra, calculus, simplification, equation solving
   - Load when: Basic symbolic computation, calculus, or solving equations

2. **`matrices-linear-algebra.md`**: Matrix operations, eigenvalues, linear systems
   - Load when: Working with matrices or linear algebra problems

3. **`physics-mechanics.md`**: Classical mechanics, quantum mechanics, vectors, units
   - Load when: Physics calculations or mechanics problems

4. **`advanced-topics.md`**: Geometry, number theory, combinatorics, logic, statistics
   - Load when: Advanced mathematical topics beyond basic algebra and calculus

5. **`code-generation-printing.md`**: Lambdify, codegen, LaTeX output, printing
   - Load when: Converting expressions to code or generating formatted output

## Common Use Case Patterns

### Pattern 1: Solve and Verify

```python
from sympy import symbols, solve, simplify
x = symbols('x')

# Solve equation
equation = x**2 - 5*x + 6
solutions = solve(equation, x)  # [2, 3]

# Verify solutions
for sol in solutions:
    result = simplify(equation.subs(x, sol))
    assert result == 0
```

### Pattern 2: Symbolic to Numeric Pipeline

```python
# 1. Define symbolic problem
x, y = symbols('x y')
expr = sin(x) + cos(y)

# 2. Manipulate symbolically
simplified = simplify(expr)
derivative = diff(simplified, x)

# 3. Convert to numerical function
f = lambdify((x, y), derivative, 'numpy')

# 4. Evaluate numerically
results = f(x_data, y_data)
```

### Pattern 3: Document Mathematical Results

```python
# Compute result symbolically
integral_expr = Integral(x**2, (x, 0, 1))
result = integral_expr.doit()

# Generate documentation
print(f"LaTeX: {latex(integral_expr)} = {latex(result)}")
print(f"Pretty: {pretty(integral_expr)} = {pretty(result)}")
print(f"Numerical: {result.evalf()}")
```

## Integration with Scientific Workflows

### With NumPy

```python
import numpy as np
from sympy import symbols, lambdify

x = symbols('x')
expr = x**2 + 2*x + 1

f = lambdify(x, expr, 'numpy')
x_array = np.linspace(-5, 5, 100)
y_array = f(x_array)
```

### With Matplotlib

```python
import matplotlib.pyplot as plt
import numpy as np
from sympy import symbols, lambdify, sin

x = symbols('x')
expr = sin(x) / x

f = lambdify(x, expr, 'numpy')
x_vals = np.linspace(-10, 10, 1000)
y_vals = f(x_vals)

plt.plot(x_vals, y_vals)
plt.show()
```

### With SciPy

```python
from scipy.optimize import fsolve
from sympy import symbols, lambdify

# Define equation symbolically
x = symbols('x')
equation = x**3 - 2*x - 5

# Convert to numerical function
f = lambdify(x, equation, 'numpy')

# Solve numerically with initial guess
solution = fsolve(f, 2)
```

## Quick Reference: Most Common Functions

```python
# Symbols
from sympy import symbols, Symbol
x, y = symbols('x y')

# Basic operations
from sympy import simplify, expand, factor, collect, cancel
from sympy import sqrt, exp, log, sin, cos, tan, pi, E, I, oo

# Calculus
from sympy import diff, integrate, limit, series, Derivative, Integral

# Solving
from sympy import solve, solveset, linsolve, nonlinsolve, dsolve

# Matrices
from sympy import Matrix, eye, zeros, ones, diag

# Logic and sets
from sympy import And, Or, Not, Implies, FiniteSet, Interval, Union

# Output
from sympy import latex, pprint, lambdify, init_printing

# Utilities
from sympy import evalf, N, nsimplify
```

## Getting Started Examples

### Example 1: Solve Quadratic Equation
```python
from sympy import symbols, solve, sqrt
x = symbols('x')
solution = solve(x**2 - 5*x + 6, x)
# [2, 3]
```

### Example 2: Calculate Derivative
```python
from sympy import symbols, diff, sin
x = symbols('x')
f = sin(x**2)
df_dx = diff(f, x)
# 2*x*cos(x**2)
```

### Example 3: Evaluate Integral
```python
from sympy import symbols, integrate, exp
x = symbols('x')
integral = integrate(x * exp(-x**2), (x, 0, oo))
# 1/2
```

### Example 4: Matrix Eigenvalues
```python
from sympy import Matrix
M = Matrix([[1, 2], [2, 1]])
eigenvals = M.eigenvals()
# {3: 1, -1: 1}
```

### Example 5: Generate Python Function
```python
from sympy import symbols, lambdify
import numpy as np
x = symbols('x')
expr = x**2 + 2*x + 1
f = lambdify(x, expr, 'numpy')
f(np.array([1, 2, 3]))
# array([ 4,  9, 16])
```

## Troubleshooting Common Issues

1. **"NameError: name 'x' is not defined"**
   - Solution: Always define symbols using `symbols()` before use

2. **Unexpected numerical results**
   - Issue: Using floating-point numbers like `0.5` instead of `Rational(1, 2)`
   - Solution: Use `Rational()` or `S()` for exact arithmetic

3. **Slow performance in loops**
   - Issue: Using `subs()` and `evalf()` repeatedly
   - Solution: Use `lambdify()` to create a fast numerical function

4. **"Can't solve this equation"**
   - Try different solvers: `solve`, `solveset`, `nsolve` (numerical)
   - Check if the equation is solvable algebraically
   - Use numerical methods if no closed-form solution exists

5. **Simplification not working as expected**
   - Try different simplification functions: `simplify`, `factor`, `expand`, `trigsimp`
   - Add assumptions to symbols (e.g., `positive=True`)
   - Use `simplify(expr, force=True)` for aggressive simplification

## Additional Resources

- Official Documentation: https://docs.sympy.org/
- Tutorial: https://docs.sympy.org/latest/tutorials/intro-tutorial/index.html
- API Reference: https://docs.sympy.org/latest/reference/index.html
- Examples: https://github.com/sympy/sympy/tree/master/examples

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/sympy/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/advanced-topics.md`

# SymPy Advanced Topics

This document covers SymPy's advanced mathematical capabilities including geometry, number theory, combinatorics, logic and sets, statistics, polynomials, and special functions.

## Geometry

### 2D Geometry

```python
from sympy.geometry import Point, Line, Circle, Triangle, Polygon

# Points
p1 = Point(0, 0)
p2 = Point(1, 1)
p3 = Point(1, 0)

# Distance between points
dist = p1.distance(p2)

# Lines
line = Line(p1, p2)
line_from_eq = Line(Point(0, 0), slope=2)

# Line properties
line.slope       # Slope
line.equation()  # Equation of line
line.length      # oo (infinite for lines)

# Line segment
from sympy.geometry import Segment
seg = Segment(p1, p2)
seg.length       # Finite length
seg.midpoint     # Midpoint

# Intersection
line2 = Line(Point(0, 1), Point(1, 0))
intersection = line.intersection(line2)  # [Point(1/2, 1/2)]

# Circles
circle = Circle(Point(0, 0), 5)  # Center, radius
circle.area           # 25*pi
circle.circumference  # 10*pi

# Triangles
tri = Triangle(p1, p2, p3)
tri.area       # Area
tri.perimeter  # Perimeter
tri.angles     # Dictionary of angles
tri.vertices   # Tuple of vertices

# Polygons
poly = Polygon(Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1))
poly.area
poly.perimeter
poly.vertices
```

### Geometric Queries

```python
# Check if point is on line/curve
point = Point(0.5, 0.5)
line.contains(point)

# Check if parallel/perpendicular
line1 = Line(Point(0, 0), Point(1, 1))
line2 = Line(Point(0, 1), Point(1, 2))
line1.is_parallel(line2)  # True
line1.is_perpendicular(line2)  # False

# Tangent lines
from sympy.geometry import Circle, Point
circle = Circle(Point(0, 0), 5)
point = Point(5, 0)
tangents = circle.tangent_lines(point)
```

### 3D Geometry

```python
from sympy.geometry import Point3D, Line3D, Plane

# 3D Points
p1 = Point3D(0, 0, 0)
p2 = Point3D(1, 1, 1)
p3 = Point3D(1, 0, 0)

# 3D Lines
line = Line3D(p1, p2)

# Planes
plane = Plane(p1, p2, p3)  # From 3 points
plane = Plane(Point3D(0, 0, 0), normal_vector=(1, 0, 0))  # From point and normal

# Plane equation
plane.equation()

# Distance from point to plane
point = Point3D(2, 3, 4)
dist = plane.distance(point)

# Intersection of plane and line
intersection = plane.intersection(line)
```

### Curves and Ellipses

```python
from sympy.geometry import Ellipse, Curve
from sympy import sin, cos, pi

# Ellipse
ellipse = Ellipse(Point(0, 0), hradius=3, vradius=2)
ellipse.area          # 6*pi
ellipse.eccentricity  # Eccentricity

# Parametric curves
from sympy.abc import t
curve = Curve((cos(t), sin(t)), (t, 0, 2*pi))  # Circle
```

## Number Theory

### Prime Numbers

```python
from sympy.ntheory import isprime, primerange, prime, nextprime, prevprime

# Check if prime
isprime(7)    # True
isprime(10)   # False

# Generate primes in range
list(primerange(10, 50))  # [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

# nth prime
prime(10)     # 29 (10th prime)

# Next and previous primes
nextprime(10)  # 11
prevprime(10)  # 7
```

### Prime Factorization

```python
from sympy import factorint, primefactors, divisors

# Prime factorization
factorint(60)  # {2: 2, 3: 1, 5: 1} means 2^2 * 3^1 * 5^1

# List of prime factors
primefactors(60)  # [2, 3, 5]

# All divisors
divisors(60)  # [1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60]
```

### GCD and LCM

```python
from sympy import gcd, lcm, igcd, ilcm

# Greatest common divisor
gcd(60, 48)   # 12
igcd(60, 48)  # 12 (integer version)

# Least common multiple
lcm(60, 48)   # 240
ilcm(60, 48)  # 240 (integer version)

# Multiple arguments
gcd(60, 48, 36)  # 12
```

### Modular Arithmetic

```python
from sympy.ntheory import mod_inverse, totient, is_primitive_root

# Modular inverse (find x such that a*x ≡ 1 (mod m))
mod_inverse(3, 7)  # 5 (because 3*5 = 15 ≡ 1 (mod 7))

# Euler's totient function
totient(10)  # 4 (numbers less than 10 coprime to 10: 1,3,7,9)

# Primitive roots
is_primitive_root(2, 5)  # True
```

### Diophantine Equations

```python
from sympy.solvers.diophantine import diophantine
from sympy.abc import x, y, z

# Linear Diophantine: ax + by = c
diophantine(3*x + 4*y - 5)  # {(4*t_0 - 5, -3*t_0 + 5)}

# Quadratic forms
diophantine(x**2 + y**2 - 25)  # Pythagorean-type equations

# More complex equations
diophantine(x**2 - 4*x*y + 8*y**2 - 3*x + 7*y - 5)
```

### Continued Fractions

```python
from sympy import nsimplify, continued_fraction_iterator
from sympy import Rational, pi

# Convert to continued fraction
cf = continued_fraction_iterator(Rational(415, 93))
list(cf)  # [4, 2, 6, 7]

# Approximate irrational numbers
cf_pi = continued_fraction_iterator(pi.evalf(20))
```

## Combinatorics

### Permutations and Combinations

```python
from sympy import factorial, binomial, factorial2
from sympy.functions.combinatorial.numbers import nC, nP

# Factorial
factorial(5)  # 120

# Binomial coefficient (n choose k)
binomial(5, 2)  # 10

# Permutations nPk = n!/(n-k)!
nP(5, 2)  # 20

# Combinations nCk = n!/(k!(n-k)!)
nC(5, 2)  # 10

# Double factorial n!!
factorial2(5)  # 15 (5*3*1)
factorial2(6)  # 48 (6*4*2)
```

### Permutation Objects

```python
from sympy.combinatorics import Permutation

# Create permutation (cycle notation)
p = Permutation([1, 2, 0, 3])  # Sends 0->1, 1->2, 2->0, 3->3
p = Permutation(0, 1, 2)(3)    # Cycle notation: (0 1 2)(3)

# Permutation operations
p.order()       # Order of permutation
p.is_even       # True if even permutation
p.inversions()  # Number of inversions

# Compose permutations
q = Permutation([2, 0, 1, 3])
r = p * q       # Composition
```

### Partitions

```python
from sympy.utilities.iterables import partitions
from sympy.functions.combinatorial.numbers import partition

# Number of integer partitions
partition(5)  # 7 (5, 4+1, 3+2, 3+1+1, 2+2+1, 2+1+1+1, 1+1+1+1+1)

# Generate all partitions
list(partitions(4))
# {4: 1}, {3: 1, 1: 1}, {2: 2}, {2: 1, 1: 2}, {1: 4}
```

### Catalan and Fibonacci Numbers

```python
from sympy import catalan, fibonacci, lucas

# Catalan numbers
catalan(5)  # 42

# Fibonacci numbers
fibonacci(10)  # 55
lucas(10)      # 123 (Lucas numbers)
```

### Group Theory

```python
from sympy.combinatorics import PermutationGroup, Permutation

# Create permutation group
p1 = Permutation([1, 0, 2])
p2 = Permutation([0, 2, 1])
G = PermutationGroup(p1, p2)

# Group properties
G.order()        # Order of group
G.is_abelian     # Check if abelian
G.is_cyclic()    # Check if cyclic
G.elements       # All group elements
```

## Logic and Sets

### Boolean Logic

```python
from sympy import symbols, And, Or, Not, Xor, Implies, Equivalent
from sympy.logic.boolalg import truth_table, simplify_logic

# Define boolean variables
x, y, z = symbols('x y z', bool=True)

# Logical operations
expr = And(x, Or(y, Not(z)))
expr = Implies(x, y)  # x -> y
expr = Equivalent(x, y)  # x <-> y
expr = Xor(x, y)  # Exclusive OR

# Simplification
expr = (x & y) | (x & ~y)
simplified = simplify_logic(expr)  # Returns x

# Truth table
expr = Implies(x, y)
print(truth_table(expr, [x, y]))
```

### Sets

```python
from sympy import FiniteSet, Interval, Union, Intersection, Complement
from sympy import S  # For special sets

# Finite sets
A = FiniteSet(1, 2, 3, 4)
B = FiniteSet(3, 4, 5, 6)

# Set operations
union = Union(A, B)              # {1, 2, 3, 4, 5, 6}
intersection = Intersection(A, B)  # {3, 4}
difference = Complement(A, B)     # {1, 2}

# Intervals
I = Interval(0, 1)              # [0, 1]
I_open = Interval.open(0, 1)    # (0, 1)
I_lopen = Interval.Lopen(0, 1)  # (0, 1]
I_ropen = Interval.Ropen(0, 1)  # [0, 1)

# Special sets
S.Reals        # All real numbers
S.Integers     # All integers
S.Naturals     # Natural numbers
S.EmptySet     # Empty set
S.Complexes    # Complex numbers

# Set membership
3 in A  # True
7 in A  # False

# Subset and superset
A.is_subset(B)    # False
A.is_superset(B)  # False
```

### Set Theory Operations

```python
from sympy import ImageSet, Lambda
from sympy.abc import x

# Image set (set of function values)
squares = ImageSet(Lambda(x, x**2), S.Integers)
# {x^2 | x ∈ ℤ}

# Power set
from sympy.sets import FiniteSet
A = FiniteSet(1, 2, 3)
# Note: SymPy doesn't have direct powerset, but can generate
```

## Polynomials

### Polynomial Manipulation

```python
from sympy import Poly, symbols, factor, expand, roots
x, y = symbols('x y')

# Create polynomial
p = Poly(x**2 + 2*x + 1, x)

# Polynomial properties
p.degree()       # 2
p.coeffs()       # [1, 2, 1]
p.as_expr()      # Convert back to expression

# Arithmetic
p1 = Poly(x**2 + 1, x)
p2 = Poly(x + 1, x)
p3 = p1 + p2
p4 = p1 * p2
q, r = div(p1, p2)  # Quotient and remainder
```

### Polynomial Roots

```python
from sympy import roots, real_roots, count_roots

p = Poly(x**3 - 6*x**2 + 11*x - 6, x)

# All roots
r = roots(p)  # {1: 1, 2: 1, 3: 1}

# Real roots only
r = real_roots(p)

# Count roots in interval
count_roots(p, a, b)  # Number of roots in [a, b]
```

### Polynomial GCD and Factorization

```python
from sympy import gcd, lcm, factor, factor_list

p1 = Poly(x**2 - 1, x)
p2 = Poly(x**2 - 2*x + 1, x)

# GCD and LCM
g = gcd(p1, p2)
l = lcm(p1, p2)

# Factorization
f = factor(x**3 - x**2 + x - 1)  # (x - 1)*(x**2 + 1)
factors = factor_list(x**3 - x**2 + x - 1)  # List form
```

### Groebner Bases

```python
from sympy import groebner, symbols

x, y, z = symbols('x y z')
polynomials = [x**2 + y**2 + z**2 - 1, x*y - z]

# Compute Groebner basis
gb = groebner(polynomials, x, y, z)
```

## Statistics

### Random Variables

```python
from sympy.stats import (
    Normal, Uniform, Exponential, Poisson, Binomial,
    P, E, variance, density, sample
)

# Define random variables
X = Normal('X', 0, 1)  # Normal(mean, std)
Y = Uniform('Y', 0, 1)  # Uniform(a, b)
Z = Exponential('Z', 1)  # Exponential(rate)

# Probability
P(X > 0)  # 1/2
P((X > 0) & (X < 1))

# Expected value
E(X)  # 0
E(X**2)  # 1

# Variance
variance(X)  # 1

# Density function
density(X)(x)  # sqrt(2)*exp(-x**2/2)/(2*sqrt(pi))
```

### Discrete Distributions

```python
from sympy.stats import Die, Bernoulli, Binomial, Poisson

# Die
D = Die('D', 6)
P(D > 3)  # 1/2

# Bernoulli
B = Bernoulli('B', 0.5)
P(B)  # 1/2

# Binomial
X = Binomial('X', 10, 0.5)
P(X == 5)  # Probability of exactly 5 successes in 10 trials

# Poisson
Y = Poisson('Y', 3)
P(Y < 2)  # Probability of less than 2 events
```

### Joint Distributions

```python
from sympy.stats import Normal, P, E
from sympy import symbols

# Independent random variables
X = Normal('X', 0, 1)
Y = Normal('Y', 0, 1)

# Joint probability
P((X > 0) & (Y > 0))  # 1/4

# Covariance
from sympy.stats import covariance
covariance(X, Y)  # 0 (independent)
```

## Special Functions

### Common Special Functions

```python
from sympy import (
    gamma,      # Gamma function
    beta,       # Beta function
    erf,        # Error function
    besselj,    # Bessel function of first kind
    bessely,    # Bessel function of second kind
    hermite,    # Hermite polynomial
    legendre,   # Legendre polynomial
    laguerre,   # Laguerre polynomial
    chebyshevt, # Chebyshev polynomial (first kind)
    zeta        # Riemann zeta function
)

# Gamma function
gamma(5)  # 24 (equivalent to 4!)
gamma(1/2)  # sqrt(pi)

# Bessel functions
besselj(0, x)  # J_0(x)
bessely(1, x)  # Y_1(x)

# Orthogonal polynomials
hermite(3, x)    # 8*x**3 - 12*x
legendre(2, x)   # (3*x**2 - 1)/2
laguerre(2, x)   # x**2/2 - 2*x + 1
chebyshevt(3, x) # 4*x**3 - 3*x
```

### Hypergeometric Functions

```python
from sympy import hyper, meijerg

# Hypergeometric function
hyper([1, 2], [3], x)

# Meijer G-function
meijerg([[1, 1], []], [[1], [0]], x)
```

## Common Patterns

### Pattern 1: Symbolic Geometry Problem

```python
from sympy.geometry import Point, Triangle
from sympy import symbols

# Define symbolic triangle
a, b = symbols('a b', positive=True)
tri = Triangle(Point(0, 0), Point(a, 0), Point(0, b))

# Compute properties symbolically
area = tri.area  # a*b/2
perimeter = tri.perimeter  # a + b + sqrt(a**2 + b**2)
```

### Pattern 2: Number Theory Calculation

```python
from sympy.ntheory import factorint, totient, isprime

# Factor and analyze
n = 12345
factors = factorint(n)
phi = totient(n)
is_prime = isprime(n)
```

### Pattern 3: Combinatorial Generation

```python
from sympy.utilities.iterables import multiset_permutations, combinations

# Generate all permutations
perms = list(multiset_permutations([1, 2, 3]))

# Generate combinations
combs = list(combinations([1, 2, 3, 4], 2))
```

### Pattern 4: Probability Calculation

```python
from sympy.stats import Normal, P, E, variance

X = Normal('X', mu, sigma)

# Compute statistics
mean = E(X)
var = variance(X)
prob = P(X > a)
```

## Important Notes

1. **Assumptions:** Many operations benefit from symbol assumptions (e.g., `positive=True`, `integer=True`).

2. **Symbolic vs Numeric:** These operations are symbolic. Use `evalf()` for numerical results.

3. **Performance:** Complex symbolic operations can be slow. Consider numerical methods for large-scale computations.

4. **Exact arithmetic:** SymPy maintains exact representations (e.g., `sqrt(2)` instead of `1.414...`).

### `references/code-generation-printing.md`

# SymPy Code Generation and Printing

This document covers SymPy's capabilities for generating executable code in various languages, converting expressions to different output formats, and customizing printing behavior.

## Code Generation

### Converting to NumPy Functions

```python
from sympy import symbols, sin, cos, lambdify
import numpy as np

x, y = symbols('x y')
expr = sin(x) + cos(y)

# Create NumPy function
f = lambdify((x, y), expr, 'numpy')

# Use with NumPy arrays
x_vals = np.linspace(0, 2*np.pi, 100)
y_vals = np.linspace(0, 2*np.pi, 100)
result = f(x_vals, y_vals)
```

### Lambdify Options

```python
from sympy import lambdify, exp, sqrt

# Different backends
f_numpy = lambdify(x, expr, 'numpy')      # NumPy
f_scipy = lambdify(x, expr, 'scipy')      # SciPy
f_mpmath = lambdify(x, expr, 'mpmath')    # mpmath (arbitrary precision)
f_math = lambdify(x, expr, 'math')        # Python math module

# Custom function mapping
custom_funcs = {'sin': lambda x: x}  # Replace sin with identity
f = lambdify(x, sin(x), modules=[custom_funcs, 'numpy'])

# Multiple expressions
exprs = [x**2, x**3, x**4]
f = lambdify(x, exprs, 'numpy')
# Returns tuple of results
```

### Generating C/C++ Code

```python
from sympy.utilities.codegen import codegen
from sympy import symbols

x, y = symbols('x y')
expr = x**2 + y**2

# Generate C code
[(c_name, c_code), (h_name, h_header)] = codegen(
    ('distance_squared', expr),
    'C',
    header=False,
    empty=False
)

print(c_code)
# Outputs valid C function
```

### Generating Fortran Code

```python
from sympy.utilities.codegen import codegen

[(f_name, f_code), (h_name, h_interface)] = codegen(
    ('my_function', expr),
    'F95',  # Fortran 95
    header=False
)

print(f_code)
```

### Advanced Code Generation

```python
from sympy.utilities.codegen import CCodeGen, make_routine
from sympy import MatrixSymbol, Matrix

# Matrix operations
A = MatrixSymbol('A', 3, 3)
expr = A + A.T

# Create routine
routine = make_routine('matrix_sum', expr)

# Generate code
gen = CCodeGen()
code = gen.write([routine], prefix='my_module')
```

### Code Printers

```python
from sympy.printing.c import C99CodePrinter, C89CodePrinter
from sympy.printing.fortran import FCodePrinter
from sympy.printing.cxx import CXX11CodePrinter

# C code
c_printer = C99CodePrinter()
c_code = c_printer.doprint(expr)

# Fortran code
f_printer = FCodePrinter()
f_code = f_printer.doprint(expr)

# C++ code
cxx_printer = CXX11CodePrinter()
cxx_code = cxx_printer.doprint(expr)
```

## Printing and Output Formats

### Pretty Printing

```python
from sympy import init_printing, pprint, pretty, symbols
from sympy import Integral, sqrt, pi

# Initialize pretty printing (for Jupyter notebooks and terminal)
init_printing()

x = symbols('x')
expr = Integral(sqrt(1/x), (x, 0, pi))

# Pretty print to terminal
pprint(expr)
#   π
#   ⌠
#   ⎮   1
#   ⎮  ───  dx
#   ⎮  √x
#   ⌡
#   0

# Get pretty string
s = pretty(expr)
print(s)
```

### LaTeX Output

```python
from sympy import latex, symbols, Integral, sin, sqrt

x, y = symbols('x y')
expr = Integral(sin(x)**2, (x, 0, pi))

# Convert to LaTeX
latex_str = latex(expr)
print(latex_str)
# \int\limits_{0}^{\pi} \sin^{2}{\left(x \right)}\, dx

# Custom LaTeX formatting
latex_str = latex(expr, mode='equation')  # Wrapped in equation environment
latex_str = latex(expr, mode='inline')    # Inline math

# For matrices
from sympy import Matrix
M = Matrix([[1, 2], [3, 4]])
latex(M)  # \left[\begin{matrix}1 & 2\\3 & 4\end{matrix}\right]
```

### MathML Output

```python
from sympy.printing.mathml import mathml, print_mathml
from sympy import sin, pi

expr = sin(pi/4)

# Content MathML
mathml_str = mathml(expr)

# Presentation MathML
mathml_str = mathml(expr, printer='presentation')

# Print to console
print_mathml(expr)
```

### String Representations

```python
from sympy import symbols, sin, pi, srepr, sstr

x = symbols('x')
expr = sin(x)**2

# Standard string (what you see in Python)
str(expr)  # 'sin(x)**2'

# String representation (prettier)
sstr(expr)  # 'sin(x)**2'

# Reproducible representation
srepr(expr)  # "Pow(sin(Symbol('x')), Integer(2))"

# Reconstruct from srepr via sympify (supported round-trip pattern)
from sympy import sympify
restored = sympify(srepr(expr))
```

### Custom Printing

```python
from sympy.printing.str import StrPrinter

class MyPrinter(StrPrinter):
    def _print_Symbol(self, expr):
        return f"<{expr.name}>"

    def _print_Add(self, expr):
        return " PLUS ".join(self._print(arg) for arg in expr.args)

printer = MyPrinter()
x, y = symbols('x y')
print(printer.doprint(x + y))  # "<x> PLUS <y>"
```

## Python Code Generation

### autowrap - Compile and Import

```python
from sympy.utilities.autowrap import autowrap
from sympy import symbols

x, y = symbols('x y')
expr = x**2 + y**2

# Automatically compile C code and create Python wrapper
f = autowrap(expr, backend='cython')
# or backend='f2py' for Fortran

# Use like a regular function
result = f(3, 4)  # 25
```

### ufuncify - Create NumPy ufuncs

```python
from sympy.utilities.autowrap import ufuncify
import numpy as np

x, y = symbols('x y')
expr = x**2 + y**2

# Create universal function
f = ufuncify((x, y), expr)

# Works with NumPy broadcasting
x_arr = np.array([1, 2, 3])
y_arr = np.array([4, 5, 6])
result = f(x_arr, y_arr)  # [17, 29, 45]
```

## Expression Tree Manipulation

### Walking Expression Trees

```python
from sympy import symbols, sin, cos, preorder_traversal, postorder_traversal

x, y = symbols('x y')
expr = sin(x) + cos(y)

# Preorder traversal (parent before children)
for arg in preorder_traversal(expr):
    print(arg)

# Postorder traversal (children before parent)
for arg in postorder_traversal(expr):
    print(arg)

# Get all subexpressions
subexprs = list(preorder_traversal(expr))
```

### Expression Substitution in Trees

```python
from sympy import Wild, symbols, sin, cos

x, y = symbols('x y')
a = Wild('a')

expr = sin(x) + cos(y)

# Pattern matching and replacement
new_expr = expr.replace(sin(a), a**2)  # sin(x) -> x**2
```

## Jupyter Notebook Integration

### Display Math

```python
from sympy import init_printing, display
from IPython.display import display as ipy_display

# Initialize printing for Jupyter
init_printing(use_latex='mathjax')  # or 'png', 'svg'

# Display expressions beautifully
expr = Integral(sin(x)**2, x)
display(expr)  # Renders as LaTeX in notebook

# Multiple outputs
ipy_display(expr1, expr2, expr3)
```

### Interactive Widgets

```python
from sympy import symbols, sin
from IPython.display import display
from ipywidgets import interact, FloatSlider
import matplotlib.pyplot as plt
import numpy as np

x = symbols('x')
expr = sin(x)

@interact(a=FloatSlider(min=0, max=10, step=0.1, value=1))
def plot_expr(a):
    f = lambdify(x, a * expr, 'numpy')
    x_vals = np.linspace(-np.pi, np.pi, 100)
    plt.plot(x_vals, f(x_vals))
    plt.show()
```

## Converting Between Representations

### Parsing untrusted input

**Security warning:** `parse_expr()` uses `eval` internally and must not be called on unsanitized user input. See the [SymPy parsing docs](https://docs.sympy.org/latest/modules/parsing.html). Prefer building expressions from typed values (`symbols()`, `Integer()`, operators) or a validated grammar. Never use Python `eval()` on `srepr()` output or parsed strings.

For trusted/local strings only, use restricted parsing:

```python
from sympy.parsing.sympy_parser import parse_expr, standard_transformations
from sympy import symbols

x, y = symbols('x y')
local_dict = {'x': x, 'y': y}

# Restrict to standard_transformations only (no 'all' or implicit multiplication)
expr = parse_expr('x**2 + 2*x + 1', local_dict=local_dict,
                  transformations=standard_transformations)
```

If you must accept interactive input, validate first: limit length, allow only math characters, and reject strings containing `__`, `import`, `=`, or assignment syntax.

### String to SymPy

```python
from sympy.parsing.sympy_parser import parse_expr, standard_transformations
from sympy import symbols

x, y = symbols('x y')
local_dict = {'x': x, 'y': y}

# Parse trusted string literals (not raw user input)
expr = parse_expr('x**2 + 2*x + 1', local_dict=local_dict,
                  transformations=standard_transformations)
expr = parse_expr('sin(x) + cos(y)', local_dict=local_dict,
                  transformations=standard_transformations)

# Implicit multiplication — trusted input only
from sympy.parsing.sympy_parser import implicit_multiplication_application

transformations = standard_transformations + (implicit_multiplication_application,)
expr = parse_expr('2x', local_dict={'x': x}, transformations=transformations)
```

### LaTeX to SymPy

```python
from sympy.parsing.latex import parse_latex

# Parse LaTeX
expr = parse_latex(r'\frac{x^2}{y}')
# Returns: x**2/y

expr = parse_latex(r'\int_0^\pi \sin(x) dx')
```

### Mathematica to SymPy

```python
from sympy.parsing.mathematica import parse_mathematica

# Parse Mathematica code
expr = parse_mathematica('Sin[x]^2 + Cos[y]^2')
# Returns SymPy expression
```

## Exporting Results

### Export to File

```python
from sympy import symbols, sin
import json

x = symbols('x')
expr = sin(x)**2

# Export as LaTeX to file
with open('output.tex', 'w') as f:
    f.write(latex(expr))

# Export as string
with open('output.txt', 'w') as f:
    f.write(str(expr))

# Export as Python code
with open('output.py', 'w') as f:
    f.write(f"from numpy import sin\n")
    f.write(f"def f(x):\n")
    f.write(f"    return {lambdify(x, expr, 'numpy')}\n")
```

### Pickle SymPy Objects

```python
import pickle
from sympy import symbols, sin

x = symbols('x')
expr = sin(x)**2 + x

# Save
with open('expr.pkl', 'wb') as f:
    pickle.dump(expr, f)

# Load
with open('expr.pkl', 'rb') as f:
    loaded_expr = pickle.load(f)
```

## Numerical Evaluation and Precision

### High-Precision Evaluation

```python
from sympy import symbols, pi, sqrt, E, exp, sin
from mpmath import mp

x = symbols('x')

# Standard precision
pi.evalf()  # 3.14159265358979

# High precision (1000 digits)
pi.evalf(1000)

# Set global precision with mpmath
mp.dps = 50  # 50 decimal places
expr = exp(pi * sqrt(163))
float(expr.evalf())

# For expressions
result = (sqrt(2) + sqrt(3)).evalf(100)
```

### Numerical Substitution

```python
from sympy import symbols, sin, cos

x, y = symbols('x y')
expr = sin(x) + cos(y)

# Numerical evaluation
result = expr.evalf(subs={x: 1.5, y: 2.3})

# With units
from sympy.physics.units import meter, second
distance = 100 * meter
time = 10 * second
speed = distance / time
speed.evalf()
```

## Common Patterns

### Pattern 1: Generate and Execute Code

```python
from sympy import symbols, lambdify
import numpy as np

# 1. Define symbolic expression
x, y = symbols('x y')
expr = x**2 + y**2

# 2. Generate function
f = lambdify((x, y), expr, 'numpy')

# 3. Execute with numerical data
data_x = np.random.rand(1000)
data_y = np.random.rand(1000)
results = f(data_x, data_y)
```

### Pattern 2: Create LaTeX Documentation

```python
from sympy import symbols, Integral, latex
from sympy.abc import x

# Define mathematical content
expr = Integral(x**2, (x, 0, 1))
result = expr.doit()

# Generate LaTeX document
latex_doc = f"""
\\documentclass{{article}}
\\usepackage{{amsmath}}
\\begin{{document}}

We compute the integral:
\\begin{{equation}}
{latex(expr)} = {latex(result)}
\\end{{equation}}

\\end{{document}}
"""

with open('document.tex', 'w') as f:
    f.write(latex_doc)
```

### Pattern 3: Interactive Computation (trusted input only)

```python
import re
from sympy import symbols, simplify, expand, latex
from sympy.parsing.sympy_parser import parse_expr, standard_transformations

x, y = symbols('x y')
local_dict = {'x': x, 'y': y}

def parse_trusted_expr(s: str):
    """Validate and parse a restricted math expression."""
    if len(s) > 200 or re.search(r'__|import|=|\(', s):
        raise ValueError("Invalid expression")
    return parse_expr(s, local_dict=local_dict,
                      transformations=standard_transformations)

# Trusted local example (do not pass raw user input without validation)
expr = parse_trusted_expr('x**2 + 2*x + 1')

simplified = simplify(expr)
expanded = expand(expr)

print(f"Simplified: {simplified}")
print(f"Expanded: {expanded}")
print(f"LaTeX: {latex(expr)}")
```

### Pattern 4: Batch Code Generation

```python
from sympy import symbols, lambdify
from sympy.utilities.codegen import codegen

# Multiple functions
x = symbols('x')
functions = {
    'f1': x**2,
    'f2': x**3,
    'f3': x**4
}

# Generate C code for all
for name, expr in functions.items():
    [(c_name, c_code), _] = codegen((name, expr), 'C')
    with open(f'{name}.c', 'w') as f:
        f.write(c_code)
```

### Pattern 5: Performance Optimization

```python
from sympy import symbols, sin, cos, cse
import numpy as np

x, y = symbols('x y')

# Complex expression with repeated subexpressions
expr = sin(x + y)**2 + cos(x + y)**2 + sin(x + y)

# Common subexpression elimination
replacements, reduced = cse(expr)
# replacements: [(x0, sin(x + y)), (x1, cos(x + y))]
# reduced: [x0**2 + x1**2 + x0]

# Generate optimized code
for var, subexpr in replacements:
    print(f"{var} = {subexpr}")
print(f"result = {reduced[0]}")
```

## Important Notes

1. **NumPy compatibility:** When using `lambdify` with NumPy, ensure your expression uses functions available in NumPy.

2. **Performance:** For numerical work, always use `lambdify` or code generation rather than `subs()` + `evalf()` in loops.

3. **Precision:** Use `mpmath` for arbitrary precision arithmetic when needed.

4. **Code generation caveats:** Generated code may not handle all edge cases. Test thoroughly.

5. **Compilation:** `autowrap` and `ufuncify` require a C/Fortran compiler and may need configuration on your system.

6. **Parsing security:** `parse_expr()` calls `eval` internally — never use it on unsanitized input. Use `local_dict` with pre-defined symbols, restrict to `standard_transformations`, validate input (length, charset, reject `__` and assignment syntax), and reconstruct expressions with `sympify(srepr(expr))` instead of `eval()`. See [SymPy parsing docs](https://docs.sympy.org/latest/modules/parsing.html).

7. **Jupyter:** For best results in Jupyter notebooks, call `init_printing()` at the start of your session.

### `references/core-capabilities.md`

# SymPy Core Capabilities

This document covers SymPy's fundamental operations: symbolic computation basics, algebra, calculus, simplification, and equation solving.

## Creating Symbols and Basic Operations

### Symbol Creation

**Single symbols:**
```python
from sympy import symbols, Symbol
x = Symbol('x')
# or more commonly:
x, y, z = symbols('x y z')
```

**With assumptions:**
```python
x = symbols('x', real=True, positive=True)
n = symbols('n', integer=True)
```

Common assumptions: `real`, `positive`, `negative`, `integer`, `rational`, `prime`, `even`, `odd`, `complex`

### Basic Arithmetic

SymPy supports standard Python operators for symbolic expressions:
- Addition: `x + y`
- Subtraction: `x - y`
- Multiplication: `x * y`
- Division: `x / y`
- Exponentiation: `x**y`

**Important gotcha:** Use `sympy.Rational()` or `S()` for exact rational numbers:
```python
from sympy import Rational, S
expr = Rational(1, 2) * x  # Correct: exact 1/2
expr = S(1)/2 * x          # Correct: exact 1/2
expr = 0.5 * x             # Creates floating-point approximation
```

### Substitution and Evaluation

**Substitute values:**
```python
expr = x**2 + 2*x + 1
expr.subs(x, 3)  # Returns 16
expr.subs({x: 2, y: 3})  # Multiple substitutions
```

**Numerical evaluation:**
```python
from sympy import pi, sqrt
expr = sqrt(8)
expr.evalf()      # 2.82842712474619
expr.evalf(20)    # 2.8284271247461900976 (20 digits)
pi.evalf(100)     # 100 digits of pi
```

## Simplification

SymPy provides multiple simplification functions, each with different strategies:

### General Simplification

```python
from sympy import simplify, expand, factor, collect, cancel, trigsimp

# General simplification (tries multiple methods)
simplify(sin(x)**2 + cos(x)**2)  # Returns 1

# Expand products and powers
expand((x + 1)**3)  # x**3 + 3*x**2 + 3*x + 1

# Factor polynomials
factor(x**3 - x**2 + x - 1)  # (x - 1)*(x**2 + 1)

# Collect terms by variable
collect(x*y + x - 3 + 2*x**2 - z*x**2 + x**3, x)

# Cancel common factors in rational expressions
cancel((x**2 + 2*x + 1)/(x**2 + x))  # (x + 1)/x
```

### Trigonometric Simplification

```python
from sympy import sin, cos, tan, trigsimp, expand_trig

# Simplify trig expressions
trigsimp(sin(x)**2 + cos(x)**2)  # 1
trigsimp(sin(x)/cos(x))          # tan(x)

# Expand trig functions
expand_trig(sin(x + y))  # sin(x)*cos(y) + sin(y)*cos(x)
```

### Power and Logarithm Simplification

```python
from sympy import powsimp, powdenest, log, expand_log, logcombine

# Simplify powers
powsimp(x**a * x**b)  # x**(a + b)

# Expand logarithms
expand_log(log(x*y))  # log(x) + log(y)

# Combine logarithms
logcombine(log(x) + log(y))  # log(x*y)
```

## Calculus

### Derivatives

```python
from sympy import diff, Derivative

# First derivative
diff(x**2, x)  # 2*x

# Higher derivatives
diff(x**4, x, x, x)  # 24*x (third derivative)
diff(x**4, x, 3)     # 24*x (same as above)

# Partial derivatives
diff(x**2*y**3, x, y)  # 6*x*y**2

# Unevaluated derivative (for display)
d = Derivative(x**2, x)
d.doit()  # Evaluates to 2*x
```

### Integrals

**Indefinite integrals:**
```python
from sympy import integrate

integrate(x**2, x)           # x**3/3
integrate(exp(x)*sin(x), x)  # exp(x)*sin(x)/2 - exp(x)*cos(x)/2
integrate(1/x, x)            # log(x)
```

**Note:** SymPy does not include the constant of integration. Add `+ C` manually if needed.

**Definite integrals:**
```python
from sympy import oo, pi, exp, sin

integrate(x**2, (x, 0, 1))    # 1/3
integrate(exp(-x), (x, 0, oo)) # 1
integrate(sin(x), (x, 0, pi))  # 2
```

**Multiple integrals:**
```python
integrate(x*y, (x, 0, 1), (y, 0, x))  # 1/12
```

**Numerical integration (when symbolic fails):**
```python
integrate(x**x, (x, 0, 1)).evalf()  # 0.783430510712134
```

### Limits

```python
from sympy import limit, oo, sin

# Basic limits
limit(sin(x)/x, x, 0)  # 1
limit(1/x, x, oo)      # 0

# One-sided limits
limit(1/x, x, 0, '+')  # oo
limit(1/x, x, 0, '-')  # -oo

# Use limit() for singularities (not subs())
limit((x**2 - 1)/(x - 1), x, 1)  # 2
```

**Important:** Use `limit()` instead of `subs()` at singularities because infinity objects don't reliably track growth rates.

### Series Expansion

```python
from sympy import series, sin, exp, cos

# Taylor series expansion
expr = sin(x)
expr.series(x, 0, 6)  # x - x**3/6 + x**5/120 + O(x**6)

# Expansion around a point
exp(x).series(x, 1, 4)  # Expands around x=1

# Remove O() term
series(exp(x), x, 0, 4).removeO()  # 1 + x + x**2/2 + x**3/6
```

### Finite Differences (Numerical Derivatives)

```python
from sympy import Function, differentiate_finite
f = Function('f')

# Approximate derivative using finite differences
differentiate_finite(f(x), x)
f(x).as_finite_difference()
```

## Equation Solving

### Algebraic Equations - solveset

**Primary function:** `solveset(equation, variable, domain)`

```python
from sympy import solveset, Eq, S

# Basic solving (assumes equation = 0)
solveset(x**2 - 1, x)  # {-1, 1}
solveset(x**2 + 1, x)  # {-I, I} (complex solutions)

# Using explicit equation
solveset(Eq(x**2, 4), x)  # {-2, 2}

# Specify domain
solveset(x**2 - 1, x, domain=S.Reals)  # {-1, 1}
solveset(x**2 + 1, x, domain=S.Reals)  # EmptySet (no real solutions)
```

**Return types:** Finite sets, intervals, or image sets

### Systems of Equations

**Linear systems - linsolve:**
```python
from sympy import linsolve, Matrix

# From equations
linsolve([x + y - 2, x - y], x, y)  # {(1, 1)}

# From augmented matrix
linsolve(Matrix([[1, 1, 2], [1, -1, 0]]), x, y)

# From A*x = b form
A = Matrix([[1, 1], [1, -1]])
b = Matrix([2, 0])
linsolve((A, b), x, y)
```

**Nonlinear systems - nonlinsolve:**
```python
from sympy import nonlinsolve

nonlinsolve([x**2 + y - 2, x + y**2 - 3], x, y)
```

**Note:** Currently nonlinsolve doesn't return solutions in form of LambertW.

### Polynomial Roots

```python
from sympy import roots, solve

# Get roots with multiplicities
roots(x**3 - 6*x**2 + 9*x, x)  # {0: 1, 3: 2}
# Means x=0 (multiplicity 1), x=3 (multiplicity 2)
```

### General Solver - solve

More flexible alternative for transcendental equations:
```python
from sympy import solve, exp, log

solve(exp(x) - 3, x)     # [log(3)]
solve(x**2 - 4, x)       # [-2, 2]
solve([x + y - 1, x - y + 1], [x, y])  # {x: 0, y: 1}
```

### Differential Equations - dsolve

```python
from sympy import Function, dsolve, Derivative, Eq

# Define function
f = symbols('f', cls=Function)

# Solve ODE
dsolve(Derivative(f(x), x) - f(x), f(x))
# Returns: Eq(f(x), C1*exp(x))

# With initial conditions
dsolve(Derivative(f(x), x) - f(x), f(x), ics={f(0): 1})
# Returns: Eq(f(x), exp(x))

# Second-order ODE
dsolve(Derivative(f(x), x, 2) + f(x), f(x))
# Returns: Eq(f(x), C1*sin(x) + C2*cos(x))
```

## Common Patterns and Best Practices

### Pattern 1: Building Complex Expressions Incrementally
```python
from sympy import symbols, simplify
x, y = symbols('x y')

# Build step by step
expr = x**2
expr = expr + 2*x + 1
expr = simplify(expr)
```

### Pattern 2: Working with Assumptions
```python
# Define symbols with physical constraints
x = symbols('x', positive=True, real=True)
y = symbols('y', real=True)

# SymPy can use these for simplification
sqrt(x**2)  # Returns x (not Abs(x)) due to positive assumption
```

### Pattern 3: Converting to Numerical Functions
```python
from sympy import lambdify
import numpy as np

expr = x**2 + 2*x + 1
f = lambdify(x, expr, 'numpy')

# Now can use with numpy arrays
x_vals = np.linspace(0, 10, 100)
y_vals = f(x_vals)
```

### Pattern 4: Pretty Printing
```python
from sympy import init_printing, pprint
init_printing()  # Enable pretty printing in terminal/notebook

expr = Integral(sqrt(1/x), x)
pprint(expr)  # Displays nicely formatted output
```

### `references/core_capabilities.md`

# Core Capabilities

Symbolic computation basics, calculus, equation solving, matrices and linear algebra,
physics and mechanics, advanced mathematics, and code generation and output. Per-topic
detail is in the other reference files in this directory.

## Core Capabilities

### 1. Symbolic Computation Basics

**Creating symbols and expressions:**
```python
from sympy import symbols, Symbol
x, y, z = symbols('x y z')
expr = x**2 + 2*x + 1

# With assumptions
x = symbols('x', real=True, positive=True)
n = symbols('n', integer=True)
```

**Simplification and manipulation:**
```python
from sympy import simplify, expand, factor, cancel
simplify(sin(x)**2 + cos(x)**2)  # Returns 1
expand((x + 1)**3)  # x**3 + 3*x**2 + 3*x + 1
factor(x**2 - 1)    # (x - 1)*(x + 1)
```

**For detailed basics:** See `references/core-capabilities.md`

### 2. Calculus

**Derivatives:**
```python
from sympy import diff
diff(x**2, x)        # 2*x
diff(x**4, x, 3)     # 24*x (third derivative)
diff(x**2*y**3, x, y)  # 6*x*y**2 (partial derivatives)
```

**Integrals:**
```python
from sympy import integrate, oo
integrate(x**2, x)              # x**3/3 (indefinite)
integrate(x**2, (x, 0, 1))      # 1/3 (definite)
integrate(exp(-x), (x, 0, oo))  # 1 (improper)
```

**Limits and Series:**
```python
from sympy import limit, series
limit(sin(x)/x, x, 0)  # 1
series(exp(x), x, 0, 6)  # 1 + x + x**2/2 + x**3/6 + x**4/24 + x**5/120 + O(x**6)
```

**For detailed calculus operations:** See `references/core-capabilities.md`

### 3. Equation Solving

**Algebraic equations:**
```python
from sympy import solveset, solve, Eq
solveset(x**2 - 4, x)  # {-2, 2}
solve(Eq(x**2, 4), x)  # [-2, 2]
```

**Systems of equations:**
```python
from sympy import linsolve, nonlinsolve
linsolve([x + y - 2, x - y], x, y)  # {(1, 1)} (linear)
nonlinsolve([x**2 + y - 2, x + y**2 - 3], x, y)  # (nonlinear)
```

**Differential equations:**
```python
from sympy import Function, dsolve, Derivative
f = symbols('f', cls=Function)
dsolve(Derivative(f(x), x) - f(x), f(x))  # Eq(f(x), C1*exp(x))
```

**For detailed solving methods:** See `references/core-capabilities.md`

### 4. Matrices and Linear Algebra

**Matrix creation and operations:**
```python
from sympy import Matrix, eye, zeros
M = Matrix([[1, 2], [3, 4]])
M_inv = M**-1  # Inverse
M.det()        # Determinant
M.T            # Transpose
```

**Eigenvalues and eigenvectors:**
```python
eigenvals = M.eigenvals()  # {eigenvalue: multiplicity}
eigenvects = M.eigenvects()  # [(eigenval, mult, [eigenvectors])]
P, D = M.diagonalize()  # M = P*D*P^-1
```

**Solving linear systems:**
```python
A = Matrix([[1, 2], [3, 4]])
b = Matrix([5, 6])
x = A.solve(b)  # Solve Ax = b
```

**For comprehensive linear algebra:** See `references/matrices-linear-algebra.md`

### 5. Physics and Mechanics

**Classical mechanics:**
```python
from sympy.physics.mechanics import dynamicsymbols, LagrangesMethod
from sympy import symbols

# Define system
q = dynamicsymbols('q')
m, g, l = symbols('m g l')

# Lagrangian (T - V)
L = m*(l*q.diff())**2/2 - m*g*l*(1 - cos(q))

# Apply Lagrange's method
LM = LagrangesMethod(L, [q])
```

**Vector analysis:**
```python
from sympy.physics.vector import ReferenceFrame, dot, cross
N = ReferenceFrame('N')
v1 = 3*N.x + 4*N.y
v2 = 1*N.x + 2*N.z
dot(v1, v2)  # Dot product
cross(v1, v2)  # Cross product
```

**Quantum mechanics:**
```python
from sympy.physics.quantum import Ket, Bra, Operator, Commutator
A, B = Operator('A'), Operator('B')
psi = Ket('psi')
comm = Commutator(A, B).doit()
```

**For detailed physics capabilities:** See `references/physics-mechanics.md`

### 6. Advanced Mathematics

The skill includes comprehensive support for:

- **Geometry:** 2D/3D analytic geometry, points, lines, circles, polygons, transformations
- **Number Theory:** Primes, factorization, GCD/LCM, modular arithmetic, Diophantine equations
- **Combinatorics:** Permutations, combinations, partitions, group theory
- **Logic and Sets:** Boolean logic, set theory, finite and infinite sets
- **Statistics:** Probability distributions, random variables, expectation, variance
- **Special Functions:** Gamma, Bessel, orthogonal polynomials, hypergeometric functions
- **Polynomials:** Polynomial algebra, roots, factorization, Groebner bases

**For detailed advanced topics:** See `references/advanced-topics.md`

### 7. Code Generation and Output

**Convert to executable functions:**
```python
from sympy import lambdify
import numpy as np

expr = x**2 + 2*x + 1
f = lambdify(x, expr, 'numpy')  # Create NumPy function
x_vals = np.linspace(0, 10, 100)
y_vals = f(x_vals)  # Fast numerical evaluation
```

**Generate C/Fortran code:**
```python
from sympy.utilities.codegen import codegen
[(c_name, c_code), (h_name, h_header)] = codegen(
    ('my_func', expr), 'C'
)
```

**LaTeX output:**
```python
from sympy import latex
latex_str = latex(expr)  # Convert to LaTeX for documents
```

**For comprehensive code generation:** See `references/code-generation-printing.md`

### `references/matrices-linear-algebra.md`

# SymPy Matrices and Linear Algebra

This document covers SymPy's matrix operations, linear algebra capabilities, and solving systems of linear equations.

## Matrix Creation

### Basic Matrix Construction

```python
from sympy import Matrix, eye, zeros, ones, diag

# From list of rows
M = Matrix([[1, 2], [3, 4]])
M = Matrix([
    [1, 2, 3],
    [4, 5, 6]
])

# Column vector
v = Matrix([1, 2, 3])

# Row vector
v = Matrix([[1, 2, 3]])
```

### Special Matrices

```python
# Identity matrix
I = eye(3)  # 3x3 identity
# [[1, 0, 0],
#  [0, 1, 0],
#  [0, 0, 1]]

# Zero matrix
Z = zeros(2, 3)  # 2 rows, 3 columns of zeros

# Ones matrix
O = ones(3, 2)   # 3 rows, 2 columns of ones

# Diagonal matrix
D = diag(1, 2, 3)
# [[1, 0, 0],
#  [0, 2, 0],
#  [0, 0, 3]]

# Block diagonal
from sympy import BlockDiagMatrix
A = Matrix([[1, 2], [3, 4]])
B = Matrix([[5, 6], [7, 8]])
BD = BlockDiagMatrix(A, B)
```

## Matrix Properties and Access

### Shape and Dimensions

```python
M = Matrix([[1, 2, 3], [4, 5, 6]])

M.shape  # (2, 3) - returns tuple (rows, cols)
M.rows   # 2
M.cols   # 3
```

### Accessing Elements

```python
M = Matrix([[1, 2, 3], [4, 5, 6]])

# Single element
M[0, 0]  # 1 (zero-indexed)
M[1, 2]  # 6

# Row access
M[0, :]   # Matrix([[1, 2, 3]])
M.row(0)  # Same as above

# Column access
M[:, 1]   # Matrix([[2], [5]])
M.col(1)  # Same as above

# Slicing
M[0:2, 0:2]  # Top-left 2x2 submatrix
```

### Modification

```python
M = Matrix([[1, 2], [3, 4]])

# Insert row
M = M.row_insert(1, Matrix([[5, 6]]))
# [[1, 2],
#  [5, 6],
#  [3, 4]]

# Insert column
M = M.col_insert(1, Matrix([7, 8]))

# Delete row
M = M.row_del(0)

# Delete column
M = M.col_del(1)
```

## Basic Matrix Operations

### Arithmetic Operations

```python
from sympy import Matrix

A = Matrix([[1, 2], [3, 4]])
B = Matrix([[5, 6], [7, 8]])

# Addition
C = A + B

# Subtraction
C = A - B

# Scalar multiplication
C = 2 * A

# Matrix multiplication
C = A * B

# Element-wise multiplication (Hadamard product)
C = A.multiply_elementwise(B)

# Power
C = A**2  # Same as A * A
C = A**3  # A * A * A
```

### Transpose and Conjugate

```python
M = Matrix([[1, 2], [3, 4]])

# Transpose
M.T
# [[1, 3],
#  [2, 4]]

# Conjugate (for complex matrices)
M.conjugate()

# Conjugate transpose (Hermitian transpose)
M.H  # Same as M.conjugate().T
```

### Inverse

```python
M = Matrix([[1, 2], [3, 4]])

# Inverse
M_inv = M**-1
M_inv = M.inv()

# Verify
M * M_inv  # Returns identity matrix

# Check if invertible
M.is_invertible()  # True or False
```

## Advanced Linear Algebra

### Determinant

```python
M = Matrix([[1, 2], [3, 4]])
M.det()  # -2

# For symbolic matrices
from sympy import symbols
a, b, c, d = symbols('a b c d')
M = Matrix([[a, b], [c, d]])
M.det()  # a*d - b*c
```

### Trace

```python
M = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
M.trace()  # 1 + 5 + 9 = 15
```

### Row Echelon Form

```python
M = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

# Reduced Row Echelon Form
rref_M, pivot_cols = M.rref()
# rref_M is the RREF matrix
# pivot_cols is tuple of pivot column indices
```

### Rank

```python
M = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
M.rank()  # 2 (this matrix is rank-deficient)
```

### Nullspace and Column Space

```python
M = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

# Nullspace (kernel)
null = M.nullspace()
# Returns list of basis vectors for nullspace

# Column space
col = M.columnspace()
# Returns list of basis vectors for column space

# Row space
row = M.rowspace()
# Returns list of basis vectors for row space
```

### Orthogonalization

```python
# Gram-Schmidt orthogonalization
vectors = [Matrix([1, 2, 3]), Matrix([4, 5, 6])]
ortho = Matrix.orthogonalize(*vectors)

# With normalization
ortho_norm = Matrix.orthogonalize(*vectors, normalize=True)
```

## Eigenvalues and Eigenvectors

### Computing Eigenvalues

```python
M = Matrix([[1, 2], [2, 1]])

# Eigenvalues with multiplicities
eigenvals = M.eigenvals()
# Returns dict: {eigenvalue: multiplicity}
# Example: {3: 1, -1: 1}

# Just the eigenvalues as a list
eigs = list(M.eigenvals().keys())
```

### Computing Eigenvectors

```python
M = Matrix([[1, 2], [2, 1]])

# Eigenvectors with eigenvalues
eigenvects = M.eigenvects()
# Returns list of tuples: (eigenvalue, multiplicity, [eigenvectors])
# Example: [(3, 1, [Matrix([1, 1])]), (-1, 1, [Matrix([1, -1])])]

# Access individual eigenvectors
for eigenval, multiplicity, eigenvecs in M.eigenvects():
    print(f"Eigenvalue: {eigenval}")
    print(f"Eigenvectors: {eigenvecs}")
```

### Diagonalization

```python
M = Matrix([[1, 2], [2, 1]])

# Check if diagonalizable
M.is_diagonalizable()  # True or False

# Diagonalize (M = P*D*P^-1)
P, D = M.diagonalize()
# P: matrix of eigenvectors
# D: diagonal matrix of eigenvalues

# Verify
P * D * P**-1 == M  # True
```

### Characteristic Polynomial

```python
from sympy import symbols
lam = symbols('lambda')

M = Matrix([[1, 2], [2, 1]])
charpoly = M.charpoly(lam)
# Returns characteristic polynomial
```

### Jordan Normal Form

```python
M = Matrix([[2, 1, 0], [0, 2, 1], [0, 0, 2]])

# Jordan form (for non-diagonalizable matrices)
P, J = M.jordan_form()
# J is the Jordan normal form
# P is the transformation matrix
```

## Matrix Decompositions

### LU Decomposition

```python
M = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 10]])

# LU decomposition
L, U, perm = M.LUdecomposition()
# L: lower triangular
# U: upper triangular
# perm: permutation indices
```

### QR Decomposition

```python
M = Matrix([[1, 2], [3, 4], [5, 6]])

# QR decomposition
Q, R = M.QRdecomposition()
# Q: orthogonal matrix
# R: upper triangular matrix
```

### Cholesky Decomposition

```python
# For positive definite symmetric matrices
M = Matrix([[4, 2], [2, 3]])

L = M.cholesky()
# L is lower triangular such that M = L*L.T
```

### Singular Value Decomposition (SVD)

```python
M = Matrix([[1, 2], [3, 4], [5, 6]])

# SVD (note: may require numerical evaluation)
U, S, V = M.singular_value_decomposition()
# M = U * S * V
```

## Solving Linear Systems

### Using Matrix Equations

```python
# Solve Ax = b
A = Matrix([[1, 2], [3, 4]])
b = Matrix([5, 6])

# Solution
x = A.solve(b)  # or A**-1 * b

# Least squares (for overdetermined systems)
x = A.solve_least_squares(b)
```

### Using linsolve

```python
from sympy import linsolve, symbols

x, y = symbols('x y')

# Method 1: List of equations
eqs = [x + y - 5, 2*x - y - 1]
sol = linsolve(eqs, [x, y])
# {(2, 3)}

# Method 2: Augmented matrix
M = Matrix([[1, 1, 5], [2, -1, 1]])
sol = linsolve(M, [x, y])

# Method 3: A*x = b form
A = Matrix([[1, 1], [2, -1]])
b = Matrix([5, 1])
sol = linsolve((A, b), [x, y])
```

### Underdetermined and Overdetermined Systems

```python
# Underdetermined (infinite solutions)
A = Matrix([[1, 2, 3]])
b = Matrix([6])
sol = A.solve(b)  # Returns parametric solution

# Overdetermined (least squares)
A = Matrix([[1, 2], [3, 4], [5, 6]])
b = Matrix([1, 2, 3])
sol = A.solve_least_squares(b)
```

## Symbolic Matrices

### Working with Symbolic Entries

```python
from sympy import symbols, Matrix

a, b, c, d = symbols('a b c d')
M = Matrix([[a, b], [c, d]])

# All operations work symbolically
M.det()  # a*d - b*c
M.inv()  # Matrix([[d/(a*d - b*c), -b/(a*d - b*c)], ...])
M.eigenvals()  # Symbolic eigenvalues
```

### Matrix Functions

```python
from sympy import exp, sin, cos, Matrix

M = Matrix([[0, 1], [-1, 0]])

# Matrix exponential
exp(M)

# Trigonometric functions
sin(M)
cos(M)
```

## Mutable vs Immutable Matrices

```python
from sympy import Matrix, ImmutableMatrix

# Mutable (default)
M = Matrix([[1, 2], [3, 4]])
M[0, 0] = 5  # Allowed

# Immutable (for use as dictionary keys, etc.)
I = ImmutableMatrix([[1, 2], [3, 4]])
# I[0, 0] = 5  # Error: ImmutableMatrix cannot be modified
```

## Sparse Matrices

For large matrices with many zero entries:

```python
from sympy import SparseMatrix

# Create sparse matrix
S = SparseMatrix(1000, 1000, {(0, 0): 1, (100, 100): 2})
# Only stores non-zero elements

# Convert dense to sparse
M = Matrix([[1, 0, 0], [0, 2, 0]])
S = SparseMatrix(M)
```

## Common Linear Algebra Patterns

### Pattern 1: Solving Ax = b for Multiple b Vectors

```python
A = Matrix([[1, 2], [3, 4]])
A_inv = A.inv()

b1 = Matrix([5, 6])
b2 = Matrix([7, 8])

x1 = A_inv * b1
x2 = A_inv * b2
```

### Pattern 2: Change of Basis

```python
# Given vectors in old basis, convert to new basis
old_basis = [Matrix([1, 0]), Matrix([0, 1])]
new_basis = [Matrix([1, 1]), Matrix([1, -1])]

# Change of basis matrix
P = Matrix.hstack(*new_basis)
P_inv = P.inv()

# Convert vector v from old to new basis
v = Matrix([3, 4])
v_new = P_inv * v
```

### Pattern 3: Matrix Condition Number

```python
# Estimate condition number (ratio of largest to smallest singular value)
M = Matrix([[1, 2], [3, 4]])
eigenvals = M.eigenvals()
cond = max(eigenvals.keys()) / min(eigenvals.keys())
```

### Pattern 4: Projection Matrices

```python
# Project onto column space of A
A = Matrix([[1, 0], [0, 1], [1, 1]])
P = A * (A.T * A).inv() * A.T
# P is projection matrix onto column space of A
```

## Important Notes

1. **Zero-testing:** SymPy's symbolic zero-testing can affect accuracy. For numerical work, consider using `evalf()` or numerical libraries.

2. **Performance:** For large numerical matrices, consider converting to NumPy using `lambdify` or using numerical linear algebra libraries directly.

3. **Symbolic computation:** Matrix operations with symbolic entries can be computationally expensive for large matrices.

4. **Assumptions:** Use symbol assumptions (e.g., `real=True`, `positive=True`) to help SymPy simplify matrix expressions correctly.

### `references/physics-mechanics.md`

# SymPy Physics and Mechanics

This document covers SymPy's physics modules including classical mechanics, quantum mechanics, vector analysis, units, optics, continuum mechanics, and control systems.

## Vector Analysis

### Creating Reference Frames and Vectors

```python
from sympy.physics.vector import ReferenceFrame, dynamicsymbols

# Create reference frames
N = ReferenceFrame('N')  # Inertial frame
B = ReferenceFrame('B')  # Body frame

# Create vectors
v = 3*N.x + 4*N.y + 5*N.z

# Time-varying quantities
t = dynamicsymbols._t
x = dynamicsymbols('x')  # Function of time
v = x.diff(t) * N.x  # Velocity vector
```

### Vector Operations

```python
from sympy.physics.vector import dot, cross

v1 = 3*N.x + 4*N.y
v2 = 1*N.x + 2*N.y + 3*N.z

# Dot product
d = dot(v1, v2)

# Cross product
c = cross(v1, v2)

# Magnitude
mag = v1.magnitude()

# Normalize
v1_norm = v1.normalize()
```

### Frame Orientation

```python
# Rotate frame B relative to N
from sympy import symbols, cos, sin
theta = symbols('theta')

# Simple rotation about z-axis
B.orient(N, 'Axis', [theta, N.z])

# Direction cosine matrix (DCM)
dcm = N.dcm(B)

# Angular velocity of B in N
omega = B.ang_vel_in(N)
```

### Points and Kinematics

```python
from sympy.physics.vector import Point

# Create points
O = Point('O')  # Origin
P = Point('P')

# Set position
P.set_pos(O, 3*N.x + 4*N.y)

# Set velocity
P.set_vel(N, 5*N.x + 2*N.y)

# Get velocity of P in frame N
v = P.vel(N)

# Get acceleration
a = P.acc(N)
```

## Classical Mechanics

### Lagrangian Mechanics

```python
from sympy import symbols, Function
from sympy.physics.mechanics import dynamicsymbols, LagrangesMethod

# Define generalized coordinates
q = dynamicsymbols('q')
qd = dynamicsymbols('q', 1)  # q dot (velocity)

# Define Lagrangian (L = T - V)
from sympy import Rational
m, g, l = symbols('m g l')
T = Rational(1, 2) * m * (l * qd)**2  # Kinetic energy
V = m * g * l * (1 - cos(q))           # Potential energy
L = T - V

# Apply Lagrange's method
LM = LagrangesMethod(L, [q])
LM.form_lagranges_equations()
eqs = LM.rhs()  # Right-hand side of equations of motion
```

### Kane's Method

```python
from sympy.physics.mechanics import KanesMethod, ReferenceFrame, Point
from sympy.physics.vector import dynamicsymbols

# Define system
N = ReferenceFrame('N')
q = dynamicsymbols('q')
u = dynamicsymbols('u')  # Generalized speed

# Create Kane's equations
kd = [u - q.diff()]  # Kinematic differential equations
KM = KanesMethod(N, [q], [u], kd)

# Define forces and bodies
# ... (define particles, forces, etc.)
# KM.kanes_equations(bodies, loads)
```

### System Bodies and Inertias

```python
from sympy.physics.mechanics import RigidBody, Inertia, Point, ReferenceFrame
from sympy import symbols

# Mass and inertia parameters
m = symbols('m')
Ixx, Iyy, Izz = symbols('I_xx I_yy I_zz')

# Create reference frame and mass center
A = ReferenceFrame('A')
P = Point('P')

# Define inertia dyadic
I = Inertia(A, Ixx, Iyy, Izz)

# Create rigid body
body = RigidBody('Body', P, A, m, (I, P))
```

### Joints Framework

```python
from sympy.physics.mechanics import Body, PinJoint, PrismaticJoint

# Create bodies
parent = Body('P')
child = Body('C')

# Create pin (revolute) joint
pin = PinJoint('pin', parent, child)

# Create prismatic (sliding) joint
slider = PrismaticJoint('slider', parent, child, axis=parent.frame.z)
```

### Linearization

```python
# Linearize equations of motion about an equilibrium
operating_point = {q: 0, u: 0}  # Equilibrium point
A, B = KM.linearize(q_ind=[q], u_ind=[u],
                     A_and_B=True,
                     op_point=operating_point)
# A: state matrix, B: input matrix
```

## Quantum Mechanics

### States and Operators

```python
from sympy.physics.quantum import Ket, Bra, Operator, Dagger

# Define states
psi = Ket('psi')
phi = Ket('phi')

# Bra states
bra_psi = Bra('psi')

# Operators
A = Operator('A')
B = Operator('B')

# Hermitian conjugate
A_dag = Dagger(A)

# Inner product
inner = bra_psi * psi
```

### Commutators and Anti-commutators

```python
from sympy.physics.quantum import Commutator, AntiCommutator

# Commutator [A, B] = AB - BA
comm = Commutator(A, B)
comm.doit()

# Anti-commutator {A, B} = AB + BA
anti = AntiCommutator(A, B)
anti.doit()
```

### Quantum Harmonic Oscillator

```python
from sympy.physics.quantum.qho_1d import RaisingOp, LoweringOp, NumberOp

# Creation and annihilation operators
a_dag = RaisingOp('a')  # Creation operator
a = LoweringOp('a')      # Annihilation operator
N = NumberOp('N')        # Number operator

# Number states
from sympy.physics.quantum.qho_1d import Ket as QHOKet
n = QHOKet('n')
```

### Spin Systems

```python
from sympy.physics.quantum.spin import (
    JzKet, JxKet, JyKet,  # Spin states
    Jz, Jx, Jy,            # Spin operators
    J2                     # Total angular momentum squared
)

# Spin-1/2 state
from sympy import Rational
psi = JzKet(Rational(1, 2), Rational(1, 2))  # |1/2, 1/2⟩

# Apply operator
result = Jz * psi
```

### Quantum Gates

```python
from sympy.physics.quantum.gate import (
    H,      # Hadamard gate
    X, Y, Z,  # Pauli gates
    CNOT,    # Controlled-NOT
    SWAP     # Swap gate
)

# Apply gate to quantum state
from sympy.physics.quantum.qubit import Qubit
q = Qubit('01')
result = H(0) * q  # Apply Hadamard to qubit 0
```

### Quantum Algorithms

```python
from sympy.physics.quantum.grover import grover_iteration, OracleGate

# Grover's algorithm components available
# from sympy.physics.quantum.shor import <components>
# Shor's algorithm components available
```

## Units and Dimensions

### Working with Units

```python
from sympy.physics.units import (
    meter, kilogram, second,
    newton, joule, watt,
    convert_to
)

# Define quantities
distance = 5 * meter
mass = 10 * kilogram
time = 2 * second

# Calculate force
force = mass * distance / time**2

# Convert units
force_in_newtons = convert_to(force, newton)
```

### Unit Systems

```python
from sympy.physics.units import SI, gravitational_constant, speed_of_light

# SI units
print(SI._base_units)  # Base SI units

# Physical constants
G = gravitational_constant
c = speed_of_light
```

### Custom Units

```python
from sympy.physics.units import Quantity, meter, second

# Define custom unit
parsec = Quantity('parsec')
parsec.set_global_relative_scale_factor(3.0857e16 * meter, meter)
```

### Dimensional Analysis

```python
from sympy.physics.units import Dimension, length, time, mass

# Check dimensions
from sympy.physics.units import convert_to, meter, second
velocity = 10 * meter / second
print(velocity.dimension)  # Dimension(length/time)
```

## Optics

### Gaussian Optics

```python
from sympy.physics.optics import (
    BeamParameter,
    FreeSpace,
    FlatRefraction,
    CurvedRefraction,
    ThinLens
)

# Gaussian beam parameter
q = BeamParameter(wavelen=532e-9, z=0, w=1e-3)

# Propagation through free space
q_new = FreeSpace(1) * q

# Thin lens
q_focused = ThinLens(f=0.1) * q
```

### Waves and Polarization

```python
from sympy.physics.optics import TWave

# Plane wave
wave = TWave(amplitude=1, frequency=5e14, phase=0)

# Medium properties (refractive index, etc.)
from sympy.physics.optics import Medium
medium = Medium('glass', permittivity=2.25)
```

## Continuum Mechanics

### Beam Analysis

```python
from sympy.physics.continuum_mechanics.beam import Beam
from sympy import symbols

# Define beam
E, I = symbols('E I', positive=True)  # Young's modulus, moment of inertia
length = 10

beam = Beam(length, E, I)

# Apply loads
from sympy.physics.continuum_mechanics.beam import Beam
beam.apply_load(-1000, 5, -1)  # Point load of -1000 at x=5

# Calculate reactions
beam.solve_for_reaction_loads()

# Get shear force, bending moment, deflection
x = symbols('x')
shear = beam.shear_force()
moment = beam.bending_moment()
deflection = beam.deflection()
```

### Truss Analysis

```python
from sympy.physics.continuum_mechanics.truss import Truss

# Create truss
truss = Truss()

# Add nodes
truss.add_node(('A', 0, 0), ('B', 4, 0), ('C', 2, 3))

# Add members
truss.add_member(('AB', 'A', 'B'), ('BC', 'B', 'C'))

# Apply loads
truss.apply_load(('C', 1000, 270))  # 1000 N at 270° at node C

# Solve
truss.solve()
```

### Cable Analysis

```python
from sympy.physics.continuum_mechanics.cable import Cable

# Create cable
cable = Cable(('A', 0, 10), ('B', 10, 10))

# Apply loads
cable.apply_load(-1, 5)  # Distributed load

# Solve for tension and shape
cable.solve()
```

## Control Systems

### Transfer Functions and State Space

```python
from sympy.physics.control import TransferFunction, StateSpace
from sympy.abc import s

# Transfer function
tf = TransferFunction(s + 1, s**2 + 2*s + 1, s)

# State-space representation
A = [[0, 1], [-1, -2]]
B = [[0], [1]]
C = [[1, 0]]
D = [[0]]

ss = StateSpace(A, B, C, D)

# Convert between representations
ss_from_tf = tf.to_statespace()
tf_from_ss = ss.to_TransferFunction()
```

### System Analysis

```python
# Poles and zeros
poles = tf.poles()
zeros = tf.zeros()

# Stability
is_stable = tf.is_stable()

# Step response, impulse response, etc.
# (Often requires numerical evaluation)
```

## Biomechanics

### Musculotendon Models

```python
from sympy.physics.biomechanics import (
    MusculotendonDeGroote2016,
    FirstOrderActivationDeGroote2016
)

# Create musculotendon model
mt = MusculotendonDeGroote2016('muscle')

# Activation dynamics
activation = FirstOrderActivationDeGroote2016('muscle_activation')
```

## High Energy Physics

### Particle Physics

```python
# Gamma matrices and Dirac equations
from sympy.physics.hep.gamma_matrices import GammaMatrix

gamma0 = GammaMatrix(0)
gamma1 = GammaMatrix(1)
```

## Common Physics Patterns

### Pattern 1: Setting Up a Mechanics Problem

```python
from sympy.physics.mechanics import dynamicsymbols, ReferenceFrame, Point
from sympy import symbols

# 1. Define reference frame
N = ReferenceFrame('N')

# 2. Define generalized coordinates
q = dynamicsymbols('q')
q_dot = dynamicsymbols('q', 1)

# 3. Define points and vectors
O = Point('O')
P = Point('P')

# 4. Set kinematics
P.set_pos(O, length * N.x)
P.set_vel(N, length * q_dot * N.x)

# 5. Define forces and apply Lagrange or Kane method
```

### Pattern 2: Quantum State Manipulation

```python
from sympy.physics.quantum import Ket, Operator, qapply

# Define state
psi = Ket('psi')

# Define operator
H = Operator('H')  # Hamiltonian

# Apply operator
result = qapply(H * psi)
```

### Pattern 3: Unit Conversion Workflow

```python
from sympy.physics.units import convert_to, meter, foot, second, minute

# Define quantity with units
distance = 100 * meter
time = 5 * minute

# Perform calculation
speed = distance / time

# Convert to desired units
speed_m_per_s = convert_to(speed, meter/second)
speed_ft_per_min = convert_to(speed, foot/minute)
```

### Pattern 4: Beam Deflection Analysis

```python
from sympy.physics.continuum_mechanics.beam import Beam
from sympy import symbols

E, I = symbols('E I', positive=True, real=True)
beam = Beam(10, E, I)

# Apply boundary conditions
beam.apply_support(0, 'pin')
beam.apply_support(10, 'roller')

# Apply loads
beam.apply_load(-1000, 5, -1)  # Point load
beam.apply_load(-50, 0, 0, 10)  # Distributed load

# Solve
beam.solve_for_reaction_loads()

# Get results at specific locations
x = 5
deflection_at_mid = beam.deflection().subs(symbols('x'), x)
```

## Important Notes

1. **Time-dependent variables:** Use `dynamicsymbols()` for time-varying quantities in mechanics problems.

2. **Units:** Always specify units explicitly using the `sympy.physics.units` module for physics calculations.

3. **Reference frames:** Clearly define reference frames and their relative orientations for vector analysis.

4. **Numerical evaluation:** Many physics calculations require numerical evaluation. Use `evalf()` or convert to NumPy for numerical work.

5. **Assumptions:** Use appropriate assumptions for symbols (e.g., `positive=True`, `real=True`) to help SymPy simplify physics expressions correctly.
