---
name: vaex
description: Use this skill for processing and analyzing large tabular datasets (billions of rows) that exceed available RAM. Vaex excels at out-of-core DataFrame operations, lazy evaluation, fast aggregations, efficient visualization of big data, and machine learning on large datasets. Apply when users need to work with large CSV/HDF5/Arrow/Parquet files, perform fast statistics on massive datasets, create visualizations of big data, or build ML pipelines that do not fit in memory.
---

# Vaex

## Overview

Vaex is a high-performance Python library designed for lazy, out-of-core DataFrames to process and visualize tabular datasets that are too large to fit into RAM. Vaex can process over a billion rows per second, enabling interactive data exploration and analysis on datasets with billions of rows.

## Installation

Install the full meta-package (recommended):

```bash
uv pip install vaex
```

Minimal install (pick only what you need):

```bash
uv pip install vaex-core vaex-viz vaex-hdf5 vaex-ml
```

The `vaex` package is a meta-package that pulls in `vaex-core`, `vaex-viz`, `vaex-hdf5`, `vaex-ml`, and other sub-packages. Arrow support is built into `vaex-core` (the separate `vaex-arrow` package is deprecated). `vaex-distributed` is deprecated in favor of vaex-enterprise.

**Version notes (vaex 4.19.0+):** Python 3.12 and NumPy v2 require vaex >= 4.19.0. On Windows, you may need Python dev headers to build the `annoy` dependency.

## When to Use This Skill

Use Vaex when:
- Processing tabular datasets larger than available RAM (gigabytes to terabytes)
- Performing fast statistical aggregations on massive datasets
- Creating visualizations and heatmaps of large datasets
- Building machine learning pipelines on big data
- Converting between data formats (CSV, HDF5, Arrow, Parquet)
- Needing lazy evaluation and virtual columns to avoid memory overhead
- Working with astronomical data, financial time series, or other large-scale scientific datasets

**Vaex vs alternatives:** Use **polars** when data fits in RAM and you need maximum in-memory speed. Use **dask** when you need distributed pandas/NumPy across a cluster. Use **vaex** for single-machine, out-of-core analytics on tabular data that exceeds RAM via memory-mapped HDF5/Arrow files.

## Core Capabilities

Vaex provides six primary capability areas, each documented in detail in the references directory:

### 1. DataFrames and Data Loading

Load and create Vaex DataFrames from various sources including files (HDF5, CSV, Arrow, Parquet), pandas DataFrames, NumPy arrays, and dictionaries. Reference `references/core_dataframes.md` for:
- Opening large files efficiently
- Converting from pandas/NumPy/Arrow
- Working with example datasets
- Understanding DataFrame structure

### 2. Data Processing and Manipulation

Perform filtering, create virtual columns, use expressions, and aggregate data without loading everything into memory. Reference `references/data_processing.md` for:
- Filtering and selections
- Virtual columns and expressions
- Groupby operations and aggregations
- String operations and datetime handling
- Working with missing data

### 3. Performance and Optimization

Leverage Vaex's lazy evaluation, caching strategies, and memory-efficient operations. Reference `references/performance.md` for:
- Understanding lazy evaluation
- Using `delay=True` for batching operations
- Materializing columns when needed
- Caching strategies
- Asynchronous operations

### 4. Data Visualization

Create interactive visualizations of large datasets including heatmaps, histograms, and scatter plots. Reference `references/visualization.md` for:
- Creating 1D and 2D plots
- Heatmap visualizations
- Working with selections
- Customizing plots and subplots

### 5. Machine Learning Integration

Build ML pipelines with transformers, encoders, and integration with scikit-learn, XGBoost, and other frameworks. Reference `references/machine_learning.md` for:
- Feature scaling and encoding
- PCA and dimensionality reduction
- K-means clustering
- Integration with scikit-learn/XGBoost/CatBoost
- Model serialization and deployment

### 6. I/O Operations

Efficiently read and write data in various formats with optimal performance. Reference `references/io_operations.md` for:
- File format recommendations
- Export strategies
- Working with Apache Arrow
- CSV handling for large files
- Server and remote data access

## Quick Start Pattern

For most Vaex tasks, follow this pattern:

```python
import vaex

# 1. Open or create DataFrame
df = vaex.open('large_file.hdf5')  # or .csv, .arrow, .parquet
# OR
df = vaex.from_pandas(pandas_df)

# 2. Explore the data
print(df)  # Shows first/last rows and column info
df.describe()  # Statistical summary

# 3. Create virtual columns (no memory overhead)
df['new_column'] = df.x ** 2 + df.y

# 4. Filter with selections
df_filtered = df[df.age > 25]

# 5. Compute statistics (fast, lazy evaluation)
mean_val = df.x.mean()
stats = df.groupby('category').agg({'value': 'sum'})

# 6. Visualize (df.viz is the recommended accessor since vaex 4.0)
df.viz.heatmap(df.x, df.y, limits='99.7%', show=True)
# Legacy: df.plot1d() and df.plot() still work on the DataFrame

# 7. Export if needed
df.export_hdf5('output.hdf5')
```

## Working with References

The reference files contain detailed information about each capability area. Load references into context based on the specific task:

- **Basic operations**: Start with `references/core_dataframes.md` and `references/data_processing.md`
- **Performance issues**: Check `references/performance.md`
- **Visualization tasks**: Use `references/visualization.md`
- **ML pipelines**: Reference `references/machine_learning.md`
- **File I/O**: Consult `references/io_operations.md`

## Best Practices

1. **Use HDF5 or Apache Arrow formats** for optimal performance with large datasets
2. **Leverage virtual columns** instead of materializing data to save memory
3. **Batch operations** using `delay=True` when performing multiple calculations
4. **Export to efficient formats** rather than keeping data in CSV
5. **Use expressions** for complex calculations without intermediate storage
6. **Profile with `df.describe()` and `df.nbytes`** to understand data shape and memory usage

## Common Patterns

### Pattern: Converting Large CSV to HDF5
```python
import vaex

# Open large CSV lazily (vaex 4.14+), or use from_csv to convert to HDF5
df = vaex.open('large_file.csv')
# df = vaex.from_csv('large_file.csv', convert='large_file.hdf5')

# Export to HDF5 for faster future access
df.export_hdf5('large_file.hdf5')

# Future loads are instant
df = vaex.open('large_file.hdf5')
```

### Pattern: Efficient Aggregations
```python
# Use delay=True to batch multiple operations
mean_x = df.x.mean(delay=True)
std_y = df.y.std(delay=True)
sum_z = df.z.sum(delay=True)

# Execute all at once
results = vaex.execute([mean_x, std_y, sum_z])
```

### Pattern: Virtual Columns for Feature Engineering
```python
# No memory overhead - computed on the fly
df['age_squared'] = df.age ** 2
df['full_name'] = df.first_name + ' ' + df.last_name
df['is_adult'] = df.age >= 18
```

## Resources

This skill includes reference documentation in the `references/` directory:

- `core_dataframes.md` - DataFrame creation, loading, and basic structure
- `data_processing.md` - Filtering, expressions, aggregations, and transformations
- `performance.md` - Optimization strategies and lazy evaluation
- `visualization.md` - Plotting and interactive visualizations
- `machine_learning.md` - ML pipelines and model integration
- `io_operations.md` - File formats and data import/export

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/vaex/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/core_dataframes.md`

# Core DataFrames and Data Loading

This reference covers Vaex DataFrame basics, loading data from various sources, and understanding the DataFrame structure.

## DataFrame Fundamentals

A Vaex DataFrame is the central data structure for working with large tabular datasets. Unlike pandas, Vaex DataFrames:
- Use **lazy evaluation** - operations are not executed until needed
- Work **out-of-core** - data doesn't need to fit in RAM
- Support **virtual columns** - computed columns with no memory overhead
- Enable **billion-row-per-second** processing through optimized C++ backend

## Opening Existing Files

### Primary Method: `vaex.open()`

The most common way to load data:

```python
import vaex

# Works with multiple formats
df = vaex.open('data.hdf5')     # HDF5 (recommended)
df = vaex.open('data.arrow')    # Apache Arrow (recommended)
df = vaex.open('data.parquet')  # Parquet
df = vaex.open('data.csv')      # CSV (lazy since 4.14; convert to HDF5 for repeated use)
df = vaex.open('data.fits')     # FITS (astronomy)

# Can open multiple files as one DataFrame
df = vaex.open('data_*.hdf5')   # Wildcards supported
```

**Key characteristics:**
- **Instant for HDF5/Arrow** - Memory-maps files, no loading time
- **Lazy CSV (4.14+)** - `vaex.open('file.csv')` reads CSV lazily without loading all data into RAM
- **Returns immediately** - Lazy evaluation means no computation until needed

### Format-Specific Loaders

```python
# Lazy CSV (preferred for exploration since vaex 4.14)
df = vaex.open('large_file.csv')

# CSV with conversion to HDF5 (preferred for repeated use)
df = vaex.from_csv(
    'large_file.csv',
    convert='large_file.hdf5',  # or convert=True
    chunk_size=5_000_000,       # Process in chunks during conversion
    copy_index=False            # Don't copy pandas index if present
)

# To load entire CSV into memory instead of lazy open:
# df = vaex.from_csv('large_file.csv')

# Apache Arrow
df = vaex.open('data.arrow')    # Native support, very fast

# HDF5 (optimal format)
df = vaex.open('data.hdf5')     # Instant loading via memory mapping
```

## Creating DataFrames from Other Sources

### From Pandas

```python
import pandas as pd
import vaex

# Convert pandas DataFrame
pdf = pd.read_csv('data.csv')
df = vaex.from_pandas(pdf, copy_index=False)

# Warning: This loads entire pandas DataFrame into memory
# For large data, prefer vaex.from_csv() directly
```

### From NumPy Arrays

```python
import numpy as np
import vaex

# Single array
x = np.random.rand(1_000_000)
df = vaex.from_arrays(x=x)

# Multiple arrays
x = np.random.rand(1_000_000)
y = np.random.rand(1_000_000)
df = vaex.from_arrays(x=x, y=y)
```

### From Dictionaries

```python
import vaex

# Dictionary of lists/arrays
data = {
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'salary': [50000, 60000, 70000]
}
df = vaex.from_dict(data)
```

### From Arrow Tables

```python
import pyarrow as pa
import vaex

# From Arrow Table
arrow_table = pa.table({
    'x': [1, 2, 3],
    'y': [4, 5, 6]
})
df = vaex.from_arrow_table(arrow_table)
```

## Example Datasets

Vaex provides built-in example datasets for testing:

```python
import vaex

# NYC taxi dataset (~1GB, 11 million rows)
df = vaex.example()

# Smaller datasets
df = vaex.datasets.titanic()
df = vaex.datasets.iris()
```

## Inspecting DataFrames

### Basic Information

```python
# Display first and last rows
print(df)

# Shape (rows, columns)
print(df.shape)  # Returns (row_count, column_count)
print(len(df))   # Row count

# Column names
print(df.columns)
print(df.column_names)

# Data types
print(df.dtypes)

# Memory usage (for materialized columns)
df.byte_size()
```

### Statistical Summary

```python
# Quick statistics for all numeric columns
df.describe()

# Single column statistics
df.x.mean()
df.x.std()
df.x.min()
df.x.max()
df.x.sum()
df.x.count()

# Quantiles
df.x.quantile(0.5)   # Median
df.x.quantile([0.25, 0.5, 0.75])  # Multiple quantiles
```

### Viewing Data

```python
# First/last rows (returns pandas DataFrame)
df.head(10)
df.tail(10)

# Random sample
df.sample(n=100)

# Convert to pandas (careful with large data!)
pdf = df.to_pandas_df()

# Convert specific columns only
pdf = df[['x', 'y']].to_pandas_df()
```

## DataFrame Structure

### Columns

```python
# Access columns as expressions
x_column = df.x
y_column = df['y']

# Column operations return expressions (lazy)
sum_column = df.x + df.y    # Not computed yet

# List all columns
print(df.get_column_names())

# Check column types
print(df.dtypes)

# Virtual vs materialized columns
print(df.get_column_names(virtual=False))  # Materialized only
print(df.get_column_names(virtual=True))   # All columns
```

### Rows

```python
# Row count
row_count = len(df)
row_count = df.count()

# Single row (returns dict)
row = df.row(0)
print(row['column_name'])

# Note: Iterating over rows is NOT recommended in Vaex
# Use vectorized operations instead
```

## Working with Expressions

Expressions are Vaex's way of representing computations that haven't been executed yet:

```python
# Create expressions (no computation)
expr = df.x ** 2 + df.y

# Expressions can be used in many contexts
mean_of_expr = expr.mean()          # Still lazy
df['new_col'] = expr                # Virtual column
filtered = df[expr > 10]            # Selection

# Force evaluation
result = expr.values  # Returns NumPy array (use carefully!)
```

## DataFrame Operations

### Copying

```python
# Shallow copy (shares data)
df_copy = df.copy()

# Deep copy (independent data)
df_deep = df.copy(deep=True)
```

### Trimming/Slicing

```python
# Select row range
df_subset = df[1000:2000]      # Rows 1000-2000
df_subset = df[:1000]          # First 1000 rows
df_subset = df[-1000:]         # Last 1000 rows

# Note: This creates a view, not a copy (efficient)
```

### Concatenating

```python
# Vertical concatenation (combine rows)
df_combined = vaex.concat([df1, df2, df3])

# Horizontal concatenation (combine columns)
# Use join or simply assign columns
df['new_col'] = other_df.some_column
```

## Best Practices

1. **Prefer HDF5 or Arrow formats** - Instant loading, optimal performance
2. **Convert large CSVs to HDF5** - One-time conversion for repeated use
3. **Avoid `.to_pandas_df()` on large data** - Defeats Vaex's purpose
4. **Use expressions instead of `.values`** - Keep operations lazy
5. **Check data types** - Ensure numeric columns aren't string type
6. **Use virtual columns** - Zero memory overhead for derived data

## Common Patterns

### Pattern: One-time CSV to HDF5 Conversion

```python
# Initial conversion (do once)
df = vaex.from_csv('large_data.csv', convert='large_data.hdf5')

# Future loads (instant)
df = vaex.open('large_data.hdf5')
```

### Pattern: Inspecting Large Datasets

```python
import vaex

df = vaex.open('large_file.hdf5')

# Quick overview
print(df)                    # First/last rows
print(df.shape)             # Dimensions
print(df.describe())        # Statistics

# Sample for detailed inspection
sample = df.sample(1000).to_pandas_df()
print(sample.head())
```

### Pattern: Loading Multiple Files

```python
# Load multiple files as one DataFrame
df = vaex.open('data_part*.hdf5')

# Or explicitly concatenate
df1 = vaex.open('data_2020.hdf5')
df2 = vaex.open('data_2021.hdf5')
df_all = vaex.concat([df1, df2])
```

## Common Issues and Solutions

### Issue: CSV Loading is Slow

```python
# Solution: Convert to HDF5 first
df = vaex.from_csv('large.csv', convert='large.hdf5')
# Future loads: df = vaex.open('large.hdf5')
```

### Issue: Column Shows as String Type

```python
# Check type
print(df.dtypes)

# Convert to numeric (creates virtual column)
df['age_numeric'] = df.age.astype('int64')
```

### Issue: Out of Memory on Small Operations

```python
# Likely using .values or .to_pandas_df()
# Solution: Use lazy operations

# Bad (loads into memory)
array = df.x.values

# Good (stays lazy)
mean = df.x.mean()
filtered = df[df.x > 10]
```

## Related Resources

- For data manipulation and filtering: See `data_processing.md`
- For performance optimization: See `performance.md`
- For file format details: See `io_operations.md`

### `references/data_processing.md`

# Data Processing and Manipulation

This reference covers filtering, selections, virtual columns, expressions, aggregations, groupby operations, and data transformations in Vaex.

## Filtering and Selections

Vaex uses boolean expressions to filter data efficiently without copying:

### Basic Filtering

```python
# Simple filter
df_filtered = df[df.age > 25]

# Multiple conditions
df_filtered = df[(df.age > 25) & (df.salary > 50000)]
df_filtered = df[(df.category == 'A') | (df.category == 'B')]

# Negation
df_filtered = df[~(df.age < 18)]
```

### Selection Objects

Vaex can maintain multiple named selections simultaneously:

```python
# Create named selection
df.select(df.age > 30, name='adults')
df.select(df.salary > 100000, name='high_earners')

# Use selection in operations
mean_age_adults = df.mean(df.age, selection='adults')
count_high_earners = df.count(selection='high_earners')

# Combine selections
df.select((df.age > 30) & (df.salary > 100000), name='adult_high_earners')

# List all selections
print(df.selection_names())

# Drop selection
df.select_drop('adults')
```

### Advanced Filtering

```python
# String matching
df_filtered = df[df.name.str.contains('John')]
df_filtered = df[df.name.str.startswith('A')]
df_filtered = df[df.email.str.endswith('@gmail.com')]

# Null/missing value filtering
df_filtered = df[df.age.isna()]      # Keep missing
df_filtered = df[df.age.notna()]     # Remove missing

# Value membership
df_filtered = df[df.category.isin(['A', 'B', 'C'])]

# Range filtering
df_filtered = df[df.age.between(25, 65)]
```

## Virtual Columns and Expressions

Virtual columns are computed on-the-fly with zero memory overhead:

### Creating Virtual Columns

```python
# Arithmetic operations
df['total'] = df.price * df.quantity
df['price_squared'] = df.price ** 2

# Mathematical functions
df['log_price'] = df.price.log()
df['sqrt_value'] = df.value.sqrt()
df['abs_diff'] = (df.x - df.y).abs()

# Conditional logic
df['is_adult'] = df.age >= 18
df['category'] = (df.score > 80).where('A', 'B')  # If-then-else
```

### Expression Methods

```python
# Mathematical
df.x.abs()          # Absolute value
df.x.sqrt()         # Square root
df.x.log()          # Natural log
df.x.log10()        # Base-10 log
df.x.exp()          # Exponential

# Trigonometric
df.angle.sin()
df.angle.cos()
df.angle.tan()
df.angle.arcsin()

# Rounding
df.x.round(2)       # Round to 2 decimals
df.x.floor()        # Round down
df.x.ceil()         # Round up

# Type conversion
df.x.astype('int64')
df.x.astype('float32')
df.x.astype('str')
```

### Conditional Expressions

```python
# where() method: condition.where(true_value, false_value)
df['status'] = (df.age >= 18).where('adult', 'minor')

# Multiple conditions with nested where
df['grade'] = (df.score >= 90).where('A',
              (df.score >= 80).where('B',
              (df.score >= 70).where('C', 'F')))

# Using searchsorted for binning
bins = [0, 18, 65, 100]
labels = ['minor', 'adult', 'senior']
df['age_group'] = df.age.searchsorted(bins).where(...)
```

## String Operations

Access string methods via the `.str` accessor:

### Basic String Methods

```python
# Case conversion
df['upper_name'] = df.name.str.upper()
df['lower_name'] = df.name.str.lower()
df['title_name'] = df.name.str.title()

# Trimming
df['trimmed'] = df.text.str.strip()
df['ltrimmed'] = df.text.str.lstrip()
df['rtrimmed'] = df.text.str.rstrip()

# Searching
df['has_john'] = df.name.str.contains('John')
df['starts_with_a'] = df.name.str.startswith('A')
df['ends_with_com'] = df.email.str.endswith('.com')

# Slicing
df['first_char'] = df.name.str.slice(0, 1)
df['last_three'] = df.name.str.slice(-3, None)

# Length
df['name_length'] = df.name.str.len()
```

### Advanced String Operations

```python
# Replacing
df['clean_text'] = df.text.str.replace('bad', 'good')

# Splitting (returns first part)
df['first_name'] = df.full_name.str.split(' ')[0]

# Concatenation
df['full_name'] = df.first_name + ' ' + df.last_name

# Padding
df['padded'] = df.code.str.pad(10, '0', 'left')  # Zero-padding
```

## DateTime Operations

Access datetime methods via the `.dt` accessor:

### DateTime Properties

```python
# Parsing strings to datetime
df['date_parsed'] = df.date_string.astype('datetime64')

# Extracting components
df['year'] = df.timestamp.dt.year
df['month'] = df.timestamp.dt.month
df['day'] = df.timestamp.dt.day
df['hour'] = df.timestamp.dt.hour
df['minute'] = df.timestamp.dt.minute
df['second'] = df.timestamp.dt.second

# Day of week
df['weekday'] = df.timestamp.dt.dayofweek  # 0=Monday
df['day_name'] = df.timestamp.dt.day_name  # 'Monday', 'Tuesday', ...

# Date arithmetic
df['tomorrow'] = df.date + pd.Timedelta(days=1)
df['next_week'] = df.date + pd.Timedelta(weeks=1)
```

## Aggregations

Vaex performs aggregations efficiently across billions of rows:

### Basic Aggregations

```python
# Single column
mean_age = df.age.mean()
std_age = df.age.std()
min_age = df.age.min()
max_age = df.age.max()
sum_sales = df.sales.sum()
count_rows = df.count()

# With selections
mean_adult_age = df.age.mean(selection='adults')

# Multiple at once with delay
mean = df.age.mean(delay=True)
std = df.age.std(delay=True)
results = vaex.execute([mean, std])
```

### Available Aggregation Functions

```python
# Central tendency
df.x.mean()
df.x.median_approx()  # Approximate median (fast)

# Dispersion
df.x.std()           # Standard deviation
df.x.var()           # Variance
df.x.min()
df.x.max()
df.x.minmax()        # Both min and max

# Count
df.count()           # Total rows
df.x.count()         # Non-missing values

# Sum and product
df.x.sum()
df.x.prod()

# Percentiles
df.x.quantile(0.5)           # Median
df.x.quantile([0.25, 0.75])  # Quartiles

# Correlation
df.correlation(df.x, df.y)
df.covar(df.x, df.y)

# Higher moments
df.x.kurtosis()
df.x.skew()

# Unique values
df.x.nunique()       # Count unique
df.x.unique()        # Get unique values (returns array)
```

## GroupBy Operations

Group data and compute aggregations per group:

### Basic GroupBy

```python
# Single column groupby
grouped = df.groupby('category')

# Aggregation
result = grouped.agg({'sales': 'sum'})
result = grouped.agg({'sales': 'sum', 'quantity': 'mean'})

# Multiple aggregations on same column
result = grouped.agg({
    'sales': ['sum', 'mean', 'std'],
    'quantity': 'sum'
})
```

### Advanced GroupBy

```python
# Multiple grouping columns
result = df.groupby(['category', 'region']).agg({
    'sales': 'sum',
    'quantity': 'mean'
})

# Custom aggregation functions
result = df.groupby('category').agg({
    'sales': lambda x: x.max() - x.min()
})

# Available aggregation functions
# 'sum', 'mean', 'std', 'min', 'max', 'count', 'first', 'last'
```

### GroupBy with Binning

```python
# Bin continuous variable and aggregate
result = df.groupby(vaex.vrange(0, 100, 10)).agg({
    'sales': 'sum'
})

# Datetime binning
result = df.groupby(df.timestamp.dt.year).agg({
    'sales': 'sum'
})
```

## Binning and Discretization

Create bins from continuous variables:

### Simple Binning

```python
# Create bins
df['age_bin'] = df.age.digitize([18, 30, 50, 65, 100])

# Labeled bins
bins = [0, 18, 30, 50, 65, 100]
labels = ['child', 'young_adult', 'adult', 'middle_age', 'senior']
df['age_group'] = df.age.digitize(bins)
# Note: Apply labels using where() or mapping
```

### Statistical Binning

```python
# Equal-width bins
df['value_bin'] = df.value.digitize(
    vaex.vrange(df.value.min(), df.value.max(), 10)
)

# Quantile-based bins
quantiles = df.value.quantile([0.25, 0.5, 0.75])
df['value_quartile'] = df.value.digitize(quantiles)
```

## Multi-dimensional Aggregations

Compute statistics on grids:

```python
# 2D histogram/heatmap data
counts = df.count(binby=[df.x, df.y], limits=[[0, 10], [0, 10]], shape=(100, 100))

# Mean on a grid
mean_z = df.mean(df.z, binby=[df.x, df.y], limits=[[0, 10], [0, 10]], shape=(50, 50))

# Multiple statistics on grid
stats = df.mean(df.z, binby=[df.x, df.y], shape=(50, 50), delay=True)
counts = df.count(binby=[df.x, df.y], shape=(50, 50), delay=True)
results = vaex.execute([stats, counts])
```

## Handling Missing Data

Work with missing, null, and NaN values:

### Detecting Missing Data

```python
# Check for missing
df['age_missing'] = df.age.isna()
df['age_present'] = df.age.notna()

# Count missing
missing_count = df.age.isna().sum()
missing_pct = df.age.isna().mean() * 100
```

### Handling Missing Data

```python
# Filter out missing
df_clean = df[df.age.notna()]

# Fill missing with value
df['age_filled'] = df.age.fillna(0)
df['age_filled'] = df.age.fillna(df.age.mean())

# Forward/backward fill (for time series)
df['age_ffill'] = df.age.fillna(method='ffill')
df['age_bfill'] = df.age.fillna(method='bfill')
```

### Missing Data Types in Vaex

Vaex distinguishes between:
- **NaN** - IEEE floating point Not-a-Number
- **NA** - Arrow null type
- **Missing** - General term for absent data

```python
# Check which missing type
df.is_masked('column_name')  # True if uses Arrow null (NA)

# Convert between types
df['col_masked'] = df.col.as_masked()  # Convert to NA representation
```

## Sorting

```python
# Sort by single column
df_sorted = df.sort('age')
df_sorted = df.sort('age', ascending=False)

# Sort by multiple columns
df_sorted = df.sort(['category', 'age'])

# Note: Sorting materializes a new column with indices
# For very large datasets, consider if sorting is necessary
```

## Joining DataFrames

Combine DataFrames based on keys:

```python
# Inner join
df_joined = df1.join(df2, on='key_column')

# Left join
df_joined = df1.join(df2, on='key_column', how='left')

# Join on different column names
df_joined = df1.join(
    df2,
    left_on='id',
    right_on='user_id',
    how='left'
)

# Multiple key columns
df_joined = df1.join(df2, on=['key1', 'key2'])
```

## Adding and Removing Columns

### Adding Columns

```python
# Virtual column (no memory)
df['new_col'] = df.x + df.y

# From external array (must match length)
import numpy as np
new_data = np.random.rand(len(df))
df['random'] = new_data

# Constant value
df['constant'] = 42
```

### Removing Columns

```python
# Drop single column
df = df.drop('column_name')

# Drop multiple columns
df = df.drop(['col1', 'col2', 'col3'])

# Select specific columns (drop others)
df = df[['col1', 'col2', 'col3']]
```

### Renaming Columns

```python
# Rename single column
df = df.rename('old_name', 'new_name')

# Rename multiple columns
df = df.rename({
    'old_name1': 'new_name1',
    'old_name2': 'new_name2'
})
```

## Common Patterns

### Pattern: Complex Feature Engineering

```python
# Multiple derived features
df['log_price'] = df.price.log()
df['price_per_unit'] = df.price / df.quantity
df['is_discount'] = df.discount > 0
df['price_category'] = (df.price > 100).where('expensive', 'affordable')
df['revenue'] = df.price * df.quantity * (1 - df.discount)
```

### Pattern: Text Cleaning

```python
# Clean and standardize text
df['email_clean'] = df.email.str.lower().str.strip()
df['has_valid_email'] = df.email_clean.str.contains('@')
df['domain'] = df.email_clean.str.split('@')[1]
```

### Pattern: Time-based Analysis

```python
# Extract temporal features
df['year'] = df.timestamp.dt.year
df['month'] = df.timestamp.dt.month
df['day_of_week'] = df.timestamp.dt.dayofweek
df['is_weekend'] = df.day_of_week >= 5
df['quarter'] = ((df.month - 1) // 3) + 1
```

### Pattern: Grouped Statistics

```python
# Compute statistics by group
monthly_sales = df.groupby(df.timestamp.dt.month).agg({
    'revenue': ['sum', 'mean', 'count'],
    'quantity': 'sum'
})

# Multiple grouping levels
category_region_sales = df.groupby(['category', 'region']).agg({
    'sales': 'sum',
    'profit': 'mean'
})
```

## Performance Tips

1. **Use virtual columns** - They're computed on-the-fly with no memory cost
2. **Batch operations with delay=True** - Compute multiple aggregations at once
3. **Avoid `.values` or `.to_pandas_df()`** - Keep operations lazy when possible
4. **Use selections** - Multiple named selections are more efficient than creating new DataFrames
5. **Leverage expressions** - They enable query optimization
6. **Minimize sorting** - Sorting is expensive on large datasets

## Related Resources

- For DataFrame creation: See `core_dataframes.md`
- For performance optimization: See `performance.md`
- For visualization: See `visualization.md`
- For ML pipelines: See `machine_learning.md`

### `references/io_operations.md`

# I/O Operations

This reference covers file input/output operations, format conversions, export strategies, and working with various data formats in Vaex.

## Overview

Vaex supports multiple file formats with varying performance characteristics. The choice of format significantly impacts loading speed, memory usage, and overall performance.

**Format recommendations:**
- **HDF5** - Best for most use cases (instant loading, memory-mapped)
- **Apache Arrow** - Best for interoperability (instant loading, columnar)
- **Parquet** - Good for distributed systems (compressed, columnar)
- **CSV** - Avoid for large datasets (slow loading, not memory-mapped)

## Reading Data

### HDF5 Files (Recommended)

```python
import vaex

# Open HDF5 file (instant, memory-mapped)
df = vaex.open('data.hdf5')

# Multiple files as one DataFrame
df = vaex.open('data_part*.hdf5')
df = vaex.open(['data_2020.hdf5', 'data_2021.hdf5', 'data_2022.hdf5'])
```

**Advantages:**
- Instant loading (memory-mapped, no data read into RAM)
- Optimal performance for Vaex operations
- Supports compression
- Random access patterns

### Apache Arrow Files

```python
# Open Arrow file (instant, memory-mapped)
df = vaex.open('data.arrow')
df = vaex.open('data.feather')  # Feather is Arrow format

# Multiple Arrow files
df = vaex.open('data_*.arrow')
```

**Advantages:**
- Instant loading (memory-mapped)
- Language-agnostic format
- Excellent for data sharing
- Zero-copy integration with Arrow ecosystem

### Parquet Files

```python
# Open Parquet file
df = vaex.open('data.parquet')

# Multiple Parquet files
df = vaex.open('data_*.parquet')

# From cloud storage
df = vaex.open('s3://bucket/data.parquet')
df = vaex.open('gs://bucket/data.parquet')
```

**Advantages:**
- Compressed by default
- Columnar format
- Wide ecosystem support
- Good for distributed systems

**Considerations:**
- Slower than HDF5/Arrow for local files
- May require full file read for some operations

### CSV Files

```python
# Lazy CSV (preferred for exploration, vaex 4.14+)
df = vaex.open('data.csv')

# Load entire CSV into memory
df = vaex.from_csv('data.csv')

# Large CSV with automatic chunking and HDF5 conversion
df = vaex.from_csv('large_data.csv', convert='large_data.hdf5', chunk_size=5_000_000)
# Creates HDF5 file for future fast loading

# CSV with options
df = vaex.from_csv(
    'data.csv',
    sep=',',
    header=0,
    names=['col1', 'col2', 'col3'],
    dtype={'col1': 'int64', 'col2': 'float64'},
    usecols=['col1', 'col2'],  # Only load specific columns
    nrows=100000  # Limit number of rows
)
```

**Recommendations:**
- **Always convert large CSVs to HDF5** for repeated use
- Use `convert` parameter to create HDF5 automatically
- CSV loading can take significant time for large files

### FITS Files (Astronomy)

```python
# Open FITS file
df = vaex.open('astronomical_data.fits')

# Multiple FITS files
df = vaex.open('survey_*.fits')
```

## Writing/Exporting Data

### Export to HDF5

```python
# Export to HDF5 (recommended for Vaex)
df.export_hdf5('output.hdf5')

# With progress bar
df.export_hdf5('output.hdf5', progress=True)

# Export subset of columns
df[['col1', 'col2', 'col3']].export_hdf5('subset.hdf5')

# Export with compression
df.export_hdf5('compressed.hdf5', compression='gzip')
```

### Export to Arrow

```python
# Export to Arrow format
df.export_arrow('output.arrow')

# Export to Feather (Arrow format)
df.export_feather('output.feather')
```

### Export to Parquet

```python
# Export to Parquet
df.export_parquet('output.parquet')

# With compression
df.export_parquet('output.parquet', compression='snappy')
df.export_parquet('output.parquet', compression='gzip')
```

### Export to CSV

```python
# Export to CSV (not recommended for large data)
df.export_csv('output.csv')

# With options
df.export_csv(
    'output.csv',
    sep=',',
    header=True,
    index=False,
    chunk_size=1_000_000
)

# Export subset
df[df.age > 25].export_csv('filtered_output.csv')
```

## Format Conversion

### CSV to HDF5 (Most Common)

```python
import vaex

# Method 1: Automatic conversion during read
df = vaex.from_csv('large.csv', convert='large.hdf5')
# Creates large.hdf5, returns DataFrame pointing to it

# Method 2: Explicit conversion
df = vaex.from_csv('large.csv')
df.export_hdf5('large.hdf5')

# Future loads (instant)
df = vaex.open('large.hdf5')
```

### HDF5 to Arrow

```python
# Load HDF5
df = vaex.open('data.hdf5')

# Export to Arrow
df.export_arrow('data.arrow')
```

### Parquet to HDF5

```python
# Load Parquet
df = vaex.open('data.parquet')

# Export to HDF5
df.export_hdf5('data.hdf5')
```

### Multiple CSV Files to Single HDF5

```python
import vaex
import glob

# Find all CSV files
csv_files = glob.glob('data_*.csv')

# Load and concatenate
dfs = [vaex.from_csv(f) for f in csv_files]
df_combined = vaex.concat(dfs)

# Export as single HDF5
df_combined.export_hdf5('combined_data.hdf5')
```

## Incremental/Chunked I/O

### Processing Large CSV in Chunks

```python
import vaex

# Process CSV in chunks
chunk_size = 1_000_000
output_file = 'processed.hdf5'

for i, df_chunk in enumerate(vaex.from_csv_chunked('huge.csv', chunk_size=chunk_size)):
    # Process chunk
    df_chunk['new_col'] = df_chunk.x + df_chunk.y

    # Append to HDF5
    if i == 0:
        df_chunk.export_hdf5(output_file)
    else:
        df_chunk.export_hdf5(output_file, mode='a')  # Append

# Load final result
df = vaex.open(output_file)
```

### Exporting in Chunks

```python
# Export large DataFrame in chunks (for CSV)
chunk_size = 1_000_000

for i in range(0, len(df), chunk_size):
    df_chunk = df[i:i+chunk_size]
    mode = 'w' if i == 0 else 'a'
    df_chunk.export_csv('large_output.csv', mode=mode, header=(i == 0))
```

## Pandas Integration

### From Pandas to Vaex

```python
import pandas as pd
import vaex

# Read with pandas
pdf = pd.read_csv('data.csv')

# Convert to Vaex
df = vaex.from_pandas(pdf, copy_index=False)

# For better performance: Use Vaex directly
df = vaex.from_csv('data.csv')  # Preferred
```

### From Vaex to Pandas

```python
# Full conversion (careful with large data!)
pdf = df.to_pandas_df()

# Convert subset
pdf = df[['col1', 'col2']].to_pandas_df()
pdf = df[:10000].to_pandas_df()  # First 10k rows
pdf = df[df.age > 25].to_pandas_df()  # Filtered

# Sample for exploration
pdf_sample = df.sample(n=10000).to_pandas_df()
```

## Arrow Integration

### From Arrow to Vaex

```python
import pyarrow as pa
import vaex

# From Arrow Table
arrow_table = pa.table({
    'a': [1, 2, 3],
    'b': [4, 5, 6]
})
df = vaex.from_arrow_table(arrow_table)

# From Arrow file
arrow_table = pa.ipc.open_file('data.arrow').read_all()
df = vaex.from_arrow_table(arrow_table)
```

### From Vaex to Arrow

```python
# Convert to Arrow Table
arrow_table = df.to_arrow_table()

# Write Arrow file
import pyarrow as pa
with pa.ipc.new_file('output.arrow', arrow_table.schema) as writer:
    writer.write_table(arrow_table)

# Or use Vaex export
df.export_arrow('output.arrow')
```

## Remote and Cloud Storage

Vaex supports streaming HDF5, Arrow, Parquet, and CSV from S3 and Google Cloud Storage. Install optional filesystem backends:

```bash
uv pip install s3fs gcsfs adlfs
```

### Reading from S3

```python
import vaex

# Read from S3 using default credentials (~/.aws/credentials or env vars)
df = vaex.open('s3://bucket-name/data.parquet')
df = vaex.open('s3://bucket-name/data.hdf5')

# With explicit fs_options (anon, profile, region, access_key, secret_key)
df = vaex.open(
    's3://bucket-name/data.parquet',
    fs_options={'profile': 'myprofile', 'region': 'us-east-1'},
)

# With explicit filesystem object
import s3fs
fs = s3fs.S3FileSystem(key='access_key', secret='secret_key')
df = vaex.open('s3://bucket-name/data.parquet', fs=fs)
```

### Reading from Google Cloud Storage

```python
# Read from GCS (requires gcsfs)
df = vaex.open('gs://bucket-name/data.parquet')

# With credentials
import gcsfs
fs = gcsfs.GCSFileSystem(token='path/to/credentials.json')
df = vaex.open('gs://bucket-name/data.parquet', fs=fs)
```

### Reading from Azure

```python
# Read from Azure Blob Storage (requires adlfs)
df = vaex.open('az://container-name/data.parquet')
```

### Writing to Cloud Storage

```python
# Export to S3
df.export_parquet('s3://bucket-name/output.parquet')
df.export_hdf5('s3://bucket-name/output.hdf5')

# Export to GCS
df.export_parquet('gs://bucket-name/output.parquet')
```

## Database Integration

### Reading from SQL Databases

```python
import vaex
import pandas as pd
from sqlalchemy import create_engine

# Read with pandas, convert to Vaex
engine = create_engine('postgresql://user:password@host:port/database')
pdf = pd.read_sql('SELECT * FROM table', engine)
df = vaex.from_pandas(pdf)

# For large tables: Read in chunks
chunks = []
for chunk in pd.read_sql('SELECT * FROM large_table', engine, chunksize=100000):
    chunks.append(vaex.from_pandas(chunk))
df = vaex.concat(chunks)

# Better: Export from database to CSV/Parquet, then load with Vaex
```

### Writing to SQL Databases

```python
# Convert to pandas, then write
pdf = df.to_pandas_df()
pdf.to_sql('table_name', engine, if_exists='replace', index=False)

# For large data: Write in chunks
chunk_size = 100000
for i in range(0, len(df), chunk_size):
    chunk = df[i:i+chunk_size].to_pandas_df()
    chunk.to_sql('table_name', engine,
                 if_exists='append' if i > 0 else 'replace',
                 index=False)
```

## Memory-Mapped Files

### Understanding Memory Mapping

```python
# HDF5 and Arrow files are memory-mapped by default
df = vaex.open('data.hdf5')  # No data loaded into RAM

# Data is read from disk on-demand
mean = df.x.mean()  # Streams through data, minimal memory

# Check if column is memory-mapped
print(df.is_local('column_name'))  # False = memory-mapped
```

### Forcing Data into Memory

```python
# If needed, load data into memory
df_in_memory = df.copy()
for col in df.get_column_names():
    df_in_memory[col] = df[col].values  # Materializes in memory
```

## File Compression

### HDF5 Compression

```python
# Export with compression
df.export_hdf5('compressed.hdf5', compression='gzip')
df.export_hdf5('compressed.hdf5', compression='lzf')
df.export_hdf5('compressed.hdf5', compression='blosc')

# Trade-off: Smaller file size, slightly slower I/O
```

### Parquet Compression

```python
# Parquet is compressed by default
df.export_parquet('data.parquet', compression='snappy')  # Fast
df.export_parquet('data.parquet', compression='gzip')    # Better compression
df.export_parquet('data.parquet', compression='brotli')  # Best compression
```

## Vaex Server (Remote Data)

### Starting Vaex Server

```bash
# Start server
vaex-server data.hdf5 --host 0.0.0.0 --port 9000
```

### Connecting to Remote Server

```python
import vaex

# Connect to remote Vaex server
df = vaex.open('ws://hostname:9000/data')

# Operations work transparently
mean = df.x.mean()  # Computed on server
```

## State Files

### Saving DataFrame State

```python
# Save state (includes virtual columns, selections, etc.)
df.state_write('state.json')

# Includes:
# - Virtual column definitions
# - Active selections
# - Variables
# - Transformations (scalers, encoders, models)
```

### Loading DataFrame State

```python
# Load data
df = vaex.open('data.hdf5')

# Apply saved state
df.state_load('state.json')

# All virtual columns, selections, and transformations restored
```

## Best Practices

### 1. Choose the Right Format

```python
# For local work: HDF5
df.export_hdf5('data.hdf5')

# For sharing/interoperability: Arrow
df.export_arrow('data.arrow')

# For distributed systems: Parquet
df.export_parquet('data.parquet')

# Avoid CSV for large data
```

### 2. Convert CSV Once

```python
# One-time conversion
df = vaex.from_csv('large.csv', convert='large.hdf5')

# All future loads
df = vaex.open('large.hdf5')  # Instant!
```

### 3. Materialize Before Export

```python
# If DataFrame has many virtual columns
df_materialized = df.materialize()
df_materialized.export_hdf5('output.hdf5')

# Faster exports and future loads
```

### 4. Use Compression Wisely

```python
# For archival or infrequently accessed data
df.export_hdf5('archived.hdf5', compression='gzip')

# For active work (faster I/O)
df.export_hdf5('working.hdf5')  # No compression
```

### 5. Checkpoint Long Pipelines

```python
# After expensive preprocessing
df_preprocessed = preprocess(df)
df_preprocessed.export_hdf5('checkpoint_preprocessed.hdf5')

# After feature engineering
df_features = engineer_features(df_preprocessed)
df_features.export_hdf5('checkpoint_features.hdf5')

# Enables resuming from checkpoints
```

## Performance Comparisons

### Format Loading Speed

```python
import time
import vaex

# CSV (slowest)
start = time.time()
df_csv = vaex.from_csv('data.csv')
csv_time = time.time() - start

# HDF5 (instant)
start = time.time()
df_hdf5 = vaex.open('data.hdf5')
hdf5_time = time.time() - start

# Arrow (instant)
start = time.time()
df_arrow = vaex.open('data.arrow')
arrow_time = time.time() - start

print(f"CSV: {csv_time:.2f}s")
print(f"HDF5: {hdf5_time:.4f}s")
print(f"Arrow: {arrow_time:.4f}s")
```

## Common Patterns

### Pattern: Production Data Pipeline

```python
import vaex

# Read from source (CSV, database export, etc.)
df = vaex.from_csv('raw_data.csv')

# Process
df['cleaned'] = clean(df.raw_column)
df['feature'] = engineer_feature(df)

# Export for production use
df.export_hdf5('production_data.hdf5')
df.state_write('production_state.json')

# In production: Fast loading
df_prod = vaex.open('production_data.hdf5')
df_prod.state_load('production_state.json')
```

### Pattern: Archiving with Compression

```python
# Archive old data with compression
df_2020 = vaex.open('data_2020.hdf5')
df_2020.export_hdf5('archive_2020.hdf5', compression='gzip')

# Remove uncompressed original
import os
os.remove('data_2020.hdf5')
```

### Pattern: Multi-Source Data Loading

```python
import vaex

# Load from multiple sources
df_csv = vaex.from_csv('data.csv')
df_hdf5 = vaex.open('data.hdf5')
df_parquet = vaex.open('data.parquet')

# Concatenate
df_all = vaex.concat([df_csv, df_hdf5, df_parquet])

# Export unified format
df_all.export_hdf5('unified.hdf5')
```

## Troubleshooting

### Issue: CSV Loading Too Slow

```python
# Solution 1: Lazy open for exploration (vaex 4.14+)
df = vaex.open('large.csv')

# Solution 2: Convert to HDF5 for repeated use
df = vaex.from_csv('large.csv', convert='large.hdf5')
# Future: df = vaex.open('large.hdf5')
```

### Issue: Out of Memory on Export

```python
# Solution: Export in chunks or materialize first
df_materialized = df.materialize()
df_materialized.export_hdf5('output.hdf5')
```

### Issue: Can't Read File from Cloud

```python
# Install required libraries
# uv pip install s3fs gcsfs adlfs

# Verify credentials
import s3fs
fs = s3fs.S3FileSystem()
fs.ls('s3://bucket-name/')
```

## Format Feature Matrix

| Feature | HDF5 | Arrow | Parquet | CSV |
|---------|------|-------|---------|-----|
| Load Speed | Instant | Instant | Fast | Slow |
| Memory-mapped | Yes | Yes | No | No |
| Compression | Optional | No | Yes | No |
| Columnar | Yes | Yes | Yes | No |
| Portability | Good | Excellent | Excellent | Excellent |
| File Size | Medium | Medium | Small | Large |
| Best For | Vaex workflows | Interop | Distributed | Exchange |

## Related Resources

- For DataFrame creation: See `core_dataframes.md`
- For performance optimization: See `performance.md`
- For data processing: See `data_processing.md`

### `references/machine_learning.md`

# Machine Learning Integration

This reference covers Vaex's machine learning capabilities including transformers, encoders, feature engineering, model integration, and building ML pipelines on large datasets.

## Overview

Vaex provides a comprehensive ML framework (`vaex.ml`) that works seamlessly with large datasets. The framework includes:
- Transformers for feature scaling and engineering
- Encoders for categorical variables
- Dimensionality reduction (PCA)
- Clustering algorithms
- Integration with scikit-learn, XGBoost, LightGBM, CatBoost, and Keras
- State management for production deployment

**Key advantage:** All transformations create virtual columns, so preprocessing doesn't increase memory usage.

## Feature Scaling

### Standard Scaler

```python
import vaex
import vaex.ml

df = vaex.open('data.hdf5')

# Fit standard scaler
scaler = vaex.ml.StandardScaler(features=['age', 'income', 'score'])
scaler.fit(df)

# Transform (creates virtual columns)
df = scaler.transform(df)

# Scaled columns created as: 'standard_scaled_age', 'standard_scaled_income', etc.
print(df.column_names)
```

### MinMax Scaler

```python
# Scale to [0, 1] range
minmax_scaler = vaex.ml.MinMaxScaler(features=['age', 'income'])
minmax_scaler.fit(df)
df = minmax_scaler.transform(df)

# Custom range
minmax_scaler = vaex.ml.MinMaxScaler(
    features=['age'],
    feature_range=(-1, 1)
)
```

### MaxAbs Scaler

```python
# Scale by maximum absolute value
maxabs_scaler = vaex.ml.MaxAbsScaler(features=['values'])
maxabs_scaler.fit(df)
df = maxabs_scaler.transform(df)
```

### Robust Scaler

```python
# Scale using median and IQR (robust to outliers)
robust_scaler = vaex.ml.RobustScaler(features=['income', 'age'])
robust_scaler.fit(df)
df = robust_scaler.transform(df)
```

## Categorical Encoding

### Label Encoder

```python
# Encode categorical to integers
label_encoder = vaex.ml.LabelEncoder(features=['category', 'region'])
label_encoder.fit(df)
df = label_encoder.transform(df)

# Creates: 'label_encoded_category', 'label_encoded_region'
```

### One-Hot Encoder

```python
# Create binary columns for each category
onehot = vaex.ml.OneHotEncoder(features=['category'])
onehot.fit(df)
df = onehot.transform(df)

# Creates columns like: 'category_A', 'category_B', 'category_C'

# Control prefix
onehot = vaex.ml.OneHotEncoder(
    features=['category'],
    prefix='cat_'
)
```

### Frequency Encoder

```python
# Encode by category frequency
freq_encoder = vaex.ml.FrequencyEncoder(features=['category'])
freq_encoder.fit(df)
df = freq_encoder.transform(df)

# Each category replaced by its frequency in the dataset
```

### Target Encoder (Mean Encoder)

```python
# Encode category by target mean (for supervised learning)
target_encoder = vaex.ml.TargetEncoder(
    features=['category'],
    target='target_variable'
)
target_encoder.fit(df)
df = target_encoder.transform(df)

# Handles unseen categories with global mean
```

### Weight of Evidence Encoder

```python
# Encode for binary classification
woe_encoder = vaex.ml.WeightOfEvidenceEncoder(
    features=['category'],
    target='binary_target'
)
woe_encoder.fit(df)
df = woe_encoder.transform(df)
```

## Feature Engineering

### Binning/Discretization

```python
# Bin continuous variable into discrete bins
binner = vaex.ml.Discretizer(
    features=['age'],
    n_bins=5,
    strategy='uniform'  # or 'quantile'
)
binner.fit(df)
df = binner.transform(df)
```

### Cyclic Transformations

```python
# Transform cyclic features (hour, day, month)
cyclic = vaex.ml.CycleTransformer(
    features=['hour', 'day_of_week'],
    n=[24, 7]  # Period for each feature
)
cyclic.fit(df)
df = cyclic.transform(df)

# Creates sin and cos components for each feature
```

### PCA (Principal Component Analysis)

```python
# Dimensionality reduction
pca = vaex.ml.PCA(
    features=['feature1', 'feature2', 'feature3', 'feature4'],
    n_components=2
)
pca.fit(df)
df = pca.transform(df)

# Creates: 'PCA_0', 'PCA_1'

# Access explained variance
print(pca.explained_variance_ratio_)
```

### Random Projection

```python
# Fast dimensionality reduction
projector = vaex.ml.RandomProjection(
    features=['x1', 'x2', 'x3', 'x4', 'x5'],
    n_components=3
)
projector.fit(df)
df = projector.transform(df)
```

## Clustering

### K-Means

```python
# Cluster data
kmeans = vaex.ml.KMeans(
    features=['feature1', 'feature2', 'feature3'],
    n_clusters=5,
    max_iter=100
)
kmeans.fit(df)
df = kmeans.transform(df)

# Creates 'prediction' column with cluster labels

# Access cluster centers
print(kmeans.cluster_centers_)
```

## Integration with External Libraries

### Scikit-Learn

```python
from sklearn.ensemble import RandomForestClassifier
import vaex.ml

# Prepare data
train_df = df[df.split == 'train']
test_df = df[df.split == 'test']

# Features and target
features = ['feature1', 'feature2', 'feature3']
target = 'target'

# Train scikit-learn model
model = RandomForestClassifier(n_estimators=100)

# Fit using Vaex data
sklearn_model = vaex.ml.sklearn.Predictor(
    features=features,
    target=target,
    model=model,
    prediction_name='rf_prediction'
)
sklearn_model.fit(train_df)

# Predict (creates virtual column)
test_df = sklearn_model.transform(test_df)

# Access predictions
predictions = test_df.rf_prediction.values
```

### XGBoost

```python
import xgboost as xgb
import vaex.ml

# Create XGBoost booster
booster = vaex.ml.xgboost.XGBoostModel(
    features=features,
    target=target,
    prediction_name='xgb_pred'
)

# Configure parameters
params = {
    'max_depth': 6,
    'eta': 0.1,
    'objective': 'reg:squarederror',
    'eval_metric': 'rmse'
}

# Train
booster.fit(
    df=train_df,
    params=params,
    num_boost_round=100
)

# Predict
test_df = booster.transform(test_df)
```

### LightGBM

```python
import lightgbm as lgb
import vaex.ml

# Create LightGBM model
lgb_model = vaex.ml.lightgbm.LightGBMModel(
    features=features,
    target=target,
    prediction_name='lgb_pred'
)

# Parameters
params = {
    'objective': 'binary',
    'metric': 'auc',
    'num_leaves': 31,
    'learning_rate': 0.05
}

# Train
lgb_model.fit(
    df=train_df,
    params=params,
    num_boost_round=100
)

# Predict
test_df = lgb_model.transform(test_df)
```

### CatBoost

```python
from catboost import CatBoostClassifier
import vaex.ml

# Create CatBoost model
catboost_model = vaex.ml.catboost.CatBoostModel(
    features=features,
    target=target,
    prediction_name='catboost_pred'
)

# Parameters
params = {
    'iterations': 100,
    'depth': 6,
    'learning_rate': 0.1,
    'loss_function': 'Logloss'
}

# Train
catboost_model.fit(train_df, **params)

# Predict
test_df = catboost_model.transform(test_df)
```

### Keras/TensorFlow

```python
from tensorflow import keras
import vaex.ml

# Define Keras model
def create_model(input_dim):
    model = keras.Sequential([
        keras.layers.Dense(64, activation='relu', input_shape=(input_dim,)),
        keras.layers.Dense(32, activation='relu'),
        keras.layers.Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

# Wrap in Vaex
keras_model = vaex.ml.keras.KerasModel(
    features=features,
    target=target,
    model=create_model(len(features)),
    prediction_name='keras_pred'
)

# Train
keras_model.fit(
    train_df,
    epochs=10,
    batch_size=10000
)

# Predict
test_df = keras_model.transform(test_df)
```

## Building ML Pipelines

### Sequential Pipeline

```python
import vaex.ml

# Create preprocessing pipeline
pipeline = []

# Step 1: Encode categorical
label_enc = vaex.ml.LabelEncoder(features=['category'])
pipeline.append(label_enc)

# Step 2: Scale features
scaler = vaex.ml.StandardScaler(features=['age', 'income'])
pipeline.append(scaler)

# Step 3: PCA
pca = vaex.ml.PCA(features=['age', 'income'], n_components=2)
pipeline.append(pca)

# Fit pipeline
for step in pipeline:
    step.fit(df)
    df = step.transform(df)

# Or use fit_transform
for step in pipeline:
    df = step.fit_transform(df)
```

### Complete ML Pipeline

```python
import vaex
import vaex.ml
from sklearn.ensemble import RandomForestClassifier

# Load data
df = vaex.open('data.hdf5')

# Split data
train_df = df[df.year < 2020]
test_df = df[df.year >= 2020]

# Define pipeline
# 1. Categorical encoding
cat_encoder = vaex.ml.LabelEncoder(features=['category', 'region'])

# 2. Feature scaling
scaler = vaex.ml.StandardScaler(features=['age', 'income', 'score'])

# 3. Model
features = ['label_encoded_category', 'label_encoded_region',
            'standard_scaled_age', 'standard_scaled_income', 'standard_scaled_score']
model = vaex.ml.sklearn.Predictor(
    features=features,
    target='target',
    model=RandomForestClassifier(n_estimators=100),
    prediction_name='prediction'
)

# Fit pipeline
train_df = cat_encoder.fit_transform(train_df)
train_df = scaler.fit_transform(train_df)
model.fit(train_df)

# Apply to test
test_df = cat_encoder.transform(test_df)
test_df = scaler.transform(test_df)
test_df = model.transform(test_df)

# Evaluate
accuracy = (test_df.prediction == test_df.target).mean()
print(f"Accuracy: {accuracy:.4f}")
```

## State Management and Deployment

### Saving Pipeline State

```python
# After fitting all transformers and model
# Save the entire pipeline state
train_df.state_write('pipeline_state.json')

# In production: Load fresh data and apply transformations
prod_df = vaex.open('new_data.hdf5')
prod_df.state_load('pipeline_state.json')

# All transformations and models are applied
predictions = prod_df.prediction.values
```

### Transferring State Between DataFrames

```python
# Fit on training data
train_df = cat_encoder.fit_transform(train_df)
train_df = scaler.fit_transform(train_df)
model.fit(train_df)

# Save state
train_df.state_write('model_state.json')

# Apply to test data
test_df.state_load('model_state.json')

# Apply to validation data
val_df.state_load('model_state.json')
```

### Exporting with Transformations

```python
# Export DataFrame with all virtual columns materialized
df_with_features = df.copy()
df_with_features = df_with_features.materialize()
df_with_features.export_hdf5('processed_data.hdf5')
```

## Model Evaluation

### Classification Metrics

```python
# Binary classification
from sklearn.metrics import accuracy_score, roc_auc_score, f1_score

y_true = test_df.target.values
y_pred = test_df.prediction.values
y_proba = test_df.prediction_proba.values if hasattr(test_df, 'prediction_proba') else None

accuracy = accuracy_score(y_true, y_pred)
f1 = f1_score(y_true, y_pred)
if y_proba is not None:
    auc = roc_auc_score(y_true, y_proba)

print(f"Accuracy: {accuracy:.4f}")
print(f"F1 Score: {f1:.4f}")
if y_proba is not None:
    print(f"AUC-ROC: {auc:.4f}")
```

### Regression Metrics

```python
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

y_true = test_df.target.values
y_pred = test_df.prediction.values

mse = mean_squared_error(y_true, y_pred)
rmse = np.sqrt(mse)
mae = mean_absolute_error(y_true, y_pred)
r2 = r2_score(y_true, y_pred)

print(f"RMSE: {rmse:.4f}")
print(f"MAE: {mae:.4f}")
print(f"R²: {r2:.4f}")
```

### Cross-Validation

```python
# Manual K-fold cross-validation
import numpy as np

# Create fold indices
df['fold'] = np.random.randint(0, 5, len(df))

results = []
for fold in range(5):
    train = df[df.fold != fold]
    val = df[df.fold == fold]

    # Fit pipeline
    train = encoder.fit_transform(train)
    train = scaler.fit_transform(train)
    model.fit(train)

    # Validate
    val = encoder.transform(val)
    val = scaler.transform(val)
    val = model.transform(val)

    accuracy = (val.prediction == val.target).mean()
    results.append(accuracy)

print(f"CV Accuracy: {np.mean(results):.4f} ± {np.std(results):.4f}")
```

## Feature Selection

### Correlation-Based

```python
# Compute correlations with target
correlations = {}
for feature in features:
    corr = df.correlation(df[feature], df.target)
    correlations[feature] = abs(corr)

# Sort by correlation
sorted_features = sorted(correlations.items(), key=lambda x: x[1], reverse=True)
top_features = [f[0] for f in sorted_features[:10]]

print("Top 10 features:", top_features)
```

### Variance-Based

```python
# Remove low-variance features
feature_variances = {}
for feature in features:
    var = df[feature].std() ** 2
    feature_variances[feature] = var

# Keep features with variance above threshold
threshold = 0.01
selected_features = [f for f, v in feature_variances.items() if v > threshold]
```

## Handling Imbalanced Data

### Class Weights

```python
# Compute class weights
class_counts = df.groupby('target', agg='count')
total = len(df)
weights = {
    0: total / (2 * class_counts[0]),
    1: total / (2 * class_counts[1])
}

# Use in model
model = RandomForestClassifier(class_weight=weights)
```

### Undersampling

```python
# Undersample majority class
minority_count = df[df.target == 1].count()

# Sample from majority class
majority_sampled = df[df.target == 0].sample(n=minority_count)
minority_all = df[df.target == 1]

# Combine
df_balanced = vaex.concat([majority_sampled, minority_all])
```

### Oversampling (SMOTE alternative)

```python
# Duplicate minority class samples
minority = df[df.target == 1]
majority = df[df.target == 0]

# Replicate minority
minority_oversampled = vaex.concat([minority] * 5)

# Combine
df_balanced = vaex.concat([majority, minority_oversampled])
```

## Common Patterns

### Pattern: End-to-End Classification Pipeline

```python
import vaex
import vaex.ml
from sklearn.ensemble import RandomForestClassifier

# Load and split
df = vaex.open('data.hdf5')
train = df[df.split == 'train']
test = df[df.split == 'test']

# Preprocessing
# Categorical encoding
cat_enc = vaex.ml.LabelEncoder(features=['cat1', 'cat2'])
train = cat_enc.fit_transform(train)

# Feature scaling
scaler = vaex.ml.StandardScaler(features=['num1', 'num2', 'num3'])
train = scaler.fit_transform(train)

# Model training
features = ['label_encoded_cat1', 'label_encoded_cat2',
            'standard_scaled_num1', 'standard_scaled_num2', 'standard_scaled_num3']
model = vaex.ml.sklearn.Predictor(
    features=features,
    target='target',
    model=RandomForestClassifier(n_estimators=100)
)
model.fit(train)

# Save state
train.state_write('production_pipeline.json')

# Apply to test
test.state_load('production_pipeline.json')

# Evaluate
accuracy = (test.prediction == test.target).mean()
print(f"Test Accuracy: {accuracy:.4f}")
```

### Pattern: Feature Engineering Pipeline

```python
# Create rich features
df['age_squared'] = df.age ** 2
df['income_log'] = df.income.log()
df['age_income_interaction'] = df.age * df.income

# Binning
df['age_bin'] = df.age.digitize([0, 18, 30, 50, 65, 100])

# Cyclic features
df['hour_sin'] = (2 * np.pi * df.hour / 24).sin()
df['hour_cos'] = (2 * np.pi * df.hour / 24).cos()

# Aggregate features
avg_by_category = df.groupby('category').agg({'income': 'mean'})
# Join back to create feature
df = df.join(avg_by_category, on='category', rsuffix='_category_mean')
```

## Best Practices

1. **Use virtual columns** - Transformers create virtual columns (no memory overhead)
2. **Save state files** - Enable easy deployment and reproduction
3. **Batch operations** - Use `delay=True` when computing multiple features
4. **Feature scaling** - Always scale features before PCA or distance-based algorithms
5. **Encode categories** - Use appropriate encoder (label, one-hot, target)
6. **Cross-validate** - Always validate on held-out data
7. **Monitor memory** - Check memory usage with `df.byte_size()`
8. **Export checkpoints** - Save intermediate results in long pipelines

## Related Resources

- For data preprocessing: See `data_processing.md`
- For performance optimization: See `performance.md`
- For DataFrame operations: See `core_dataframes.md`

### `references/performance.md`

# Performance and Optimization

This reference covers Vaex's performance features including lazy evaluation, caching, memory management, async operations, and optimization strategies for processing massive datasets.

## Understanding Lazy Evaluation

Lazy evaluation is the foundation of Vaex's performance:

### How Lazy Evaluation Works

```python
import vaex

df = vaex.open('large_file.hdf5')

# No computation happens here - just defines what to compute
df['total'] = df.price * df.quantity
df['log_price'] = df.price.log()
mean_expr = df.total.mean()

# Computation happens here (when result is needed)
result = mean_expr  # Now the mean is actually calculated
```

**Key concepts:**
- **Expressions** are lazy - they define computations without executing them
- **Materialization** happens when you access the result
- **Query optimization** happens automatically before execution

### When Does Evaluation Happen?

```python
# These trigger evaluation:
print(df.x.mean())                    # Accessing value
array = df.x.values                   # Getting NumPy array
pdf = df.to_pandas_df()              # Converting to pandas
df.export_hdf5('output.hdf5')       # Exporting

# These do NOT trigger evaluation:
df['new_col'] = df.x + df.y          # Creating virtual column
expr = df.x.mean()                    # Creating expression
df_filtered = df[df.x > 10]          # Creating filtered view
```

## Batching Operations with delay=True

Execute multiple operations together for better performance:

### Basic Delayed Execution

```python
# Without delay - each operation processes entire dataset
mean_x = df.x.mean()      # Pass 1 through data
std_x = df.x.std()        # Pass 2 through data
max_x = df.x.max()        # Pass 3 through data

# With delay - single pass through dataset
mean_x = df.x.mean(delay=True)
std_x = df.x.std(delay=True)
max_x = df.x.max(delay=True)
results = vaex.execute([mean_x, std_x, max_x])  # Single pass!

print(results[0])  # mean
print(results[1])  # std
print(results[2])  # max
```

### Delayed Execution with Multiple Columns

```python
# Compute statistics for many columns efficiently
stats = {}
delayed_results = []

for column in ['sales', 'quantity', 'profit', 'cost']:
    mean = df[column].mean(delay=True)
    std = df[column].std(delay=True)
    delayed_results.extend([mean, std])

# Execute all at once
results = vaex.execute(delayed_results)

# Process results
for i, column in enumerate(['sales', 'quantity', 'profit', 'cost']):
    stats[column] = {
        'mean': results[i*2],
        'std': results[i*2 + 1]
    }
```

### When to Use delay=True

Use `delay=True` when:
- Computing multiple aggregations
- Computing statistics on many columns
- Building dashboards or reports
- Any scenario requiring multiple passes through data

```python
# Bad: 4 passes through dataset
mean1 = df.col1.mean()
mean2 = df.col2.mean()
mean3 = df.col3.mean()
mean4 = df.col4.mean()

# Good: 1 pass through dataset
results = vaex.execute([
    df.col1.mean(delay=True),
    df.col2.mean(delay=True),
    df.col3.mean(delay=True),
    df.col4.mean(delay=True)
])
```

## Asynchronous Operations

Process data asynchronously using async/await:

### Async with async/await

```python
import vaex
import asyncio

async def compute_statistics(df):
    # Create async tasks
    mean_task = df.x.mean(delay=True)
    std_task = df.x.std(delay=True)

    # Execute asynchronously
    results = await vaex.async_execute([mean_task, std_task])

    return {'mean': results[0], 'std': results[1]}

# Run async function
async def main():
    df = vaex.open('large_file.hdf5')
    stats = await compute_statistics(df)
    print(stats)

asyncio.run(main())
```

### Using Promises/Futures

```python
# Get future object
future = df.x.mean(delay=True)

# Do other work...

# Get result when ready
result = future.get()  # Blocks until complete
```

## Virtual Columns vs Materialized Columns

Understanding the difference is crucial for performance:

### Virtual Columns (Preferred)

```python
# Virtual column - computed on-the-fly, zero memory
df['total'] = df.price * df.quantity
df['log_sales'] = df.sales.log()
df['full_name'] = df.first_name + ' ' + df.last_name

# Check if virtual
print(df.is_local('total'))  # False = virtual

# Benefits:
# - Zero memory overhead
# - Always up-to-date if source data changes
# - Fast to create
```

### Materialized Columns

```python
# Materialize a virtual column
df['total_materialized'] = df['total'].values

# Or use materialize method
df = df.materialize(df['total'], inplace=True)

# Check if materialized
print(df.is_local('total_materialized'))  # True = materialized

# When to materialize:
# - Column computed repeatedly (amortize cost)
# - Complex expression used in many operations
# - Need to export data
```

### Deciding: Virtual vs Materialized

```python
# Virtual is better when:
# - Column is simple (x + y, x * 2, etc.)
# - Column used infrequently
# - Memory is limited

# Materialize when:
# - Complex computation (multiple operations)
# - Used repeatedly in aggregations
# - Slows down other operations

# Example: Complex calculation used many times
df['complex'] = (df.x.log() * df.y.sqrt() + df.z ** 2).values  # Materialize
```

## Caching Strategies

Vaex automatically caches some operations, but you can optimize further:

### Automatic Caching

```python
# First call computes and caches
mean1 = df.x.mean()  # Computes

# Second call uses cache
mean2 = df.x.mean()  # From cache (instant)

# Cache invalidated if DataFrame changes
df['new_col'] = df.x + 1
mean3 = df.x.mean()  # Recomputes
```

### State Management

```python
# Save DataFrame state (includes virtual columns)
df.state_write('state.json')

# Load state later
df_new = vaex.open('data.hdf5')
df_new.state_load('state.json')  # Restores virtual columns, selections
```

### Checkpoint Pattern

```python
# Export intermediate results for complex pipelines
df['processed'] = complex_calculation(df)

# Save checkpoint
df.export_hdf5('checkpoint.hdf5')

# Resume from checkpoint
df = vaex.open('checkpoint.hdf5')
# Continue processing...
```

## Memory Management

Optimize memory usage for very large datasets:

### Memory-Mapped Files

```python
# HDF5 and Arrow are memory-mapped (optimal)
df = vaex.open('data.hdf5')  # No memory used until accessed

# File stays on disk, only accessed portions loaded to RAM
mean = df.x.mean()  # Streams through data, minimal memory
```

### Chunked Processing

```python
# Process large DataFrame in chunks
chunk_size = 1_000_000

for i1, i2, chunk in df.to_pandas_df(chunk_size=chunk_size):
    # Process chunk (careful: defeats Vaex's purpose)
    process_chunk(chunk)

# Better: Use Vaex operations directly (no chunking needed)
result = df.x.mean()  # Handles large data automatically
```

### Monitoring Memory Usage

```python
# Check DataFrame memory footprint
print(df.byte_size())  # Bytes used by materialized columns

# Check column memory
for col in df.get_column_names():
    if df.is_local(col):
        print(f"{col}: {df[col].nbytes / 1e9:.2f} GB")

# Profile operations
import vaex.profiler
with vaex.profiler():
    result = df.x.mean()
```

## Parallel Computation

Vaex automatically parallelizes operations:

### Multithreading

```python
# Vaex uses all CPU cores by default
import vaex

# Check/set thread count
print(vaex.multithreading.thread_count_default)
vaex.multithreading.thread_count_default = 8  # Use 8 threads

# Operations automatically parallelize
mean = df.x.mean()  # Uses all threads
```

### Distributed Computing with Dask

```python
# Convert to Dask for distributed processing
import vaex
import dask.dataframe as dd

# Create Vaex DataFrame
df_vaex = vaex.open('large_file.hdf5')

# Convert to Dask
df_dask = df_vaex.to_dask_dataframe()

# Process with Dask
result = df_dask.groupby('category')['value'].sum().compute()
```

## JIT Compilation

Vaex can use Just-In-Time compilation for custom operations:

### Using Numba

```python
import vaex
import numba

# Define JIT-compiled function
@numba.jit
def custom_calculation(x, y):
    return x ** 2 + y ** 2

# Apply to DataFrame
df['custom'] = df.apply(custom_calculation,
                        arguments=[df.x, df.y],
                        vectorize=True)
```

### Custom Aggregations

```python
@numba.jit
def custom_sum(a):
    total = 0
    for val in a:
        total += val * 2  # Custom logic
    return total

# Use in aggregation
result = df.x.custom_agg(custom_sum)
```

## Optimization Strategies

### Strategy 1: Minimize Materializations

```python
# Bad: Creates many materialized columns
df['a'] = (df.x + df.y).values
df['b'] = (df.a * 2).values
df['c'] = (df.b + df.z).values

# Good: Keep virtual until final export
df['a'] = df.x + df.y
df['b'] = df.a * 2
df['c'] = df.b + df.z
# Only materialize if exporting:
# df.export_hdf5('output.hdf5')
```

### Strategy 2: Use Selections Instead of Filtering

```python
# Less efficient: Creates new DataFrames
df_high = df[df.value > 100]
df_low = df[df.value <= 100]
mean_high = df_high.value.mean()
mean_low = df_low.value.mean()

# More efficient: Use selections
df.select(df.value > 100, name='high')
df.select(df.value <= 100, name='low')
mean_high = df.value.mean(selection='high')
mean_low = df.value.mean(selection='low')
```

### Strategy 3: Batch Aggregations

```python
# Less efficient: Multiple passes
stats = {
    'mean': df.x.mean(),
    'std': df.x.std(),
    'min': df.x.min(),
    'max': df.x.max()
}

# More efficient: Single pass
delayed = [
    df.x.mean(delay=True),
    df.x.std(delay=True),
    df.x.min(delay=True),
    df.x.max(delay=True)
]
results = vaex.execute(delayed)
stats = dict(zip(['mean', 'std', 'min', 'max'], results))
```

### Strategy 4: Choose Optimal File Formats

```python
# Slow: Large CSV
df = vaex.from_csv('huge.csv')  # Can take minutes

# Fast: HDF5 or Arrow
df = vaex.open('huge.hdf5')     # Instant
df = vaex.open('huge.arrow')    # Instant

# One-time conversion
df = vaex.from_csv('huge.csv', convert='huge.hdf5')
# Future loads: vaex.open('huge.hdf5')
```

### Strategy 5: Optimize Expressions

```python
# Less efficient: Repeated calculations
df['result'] = df.x.log() + df.x.log() * 2

# More efficient: Reuse calculations
df['log_x'] = df.x.log()
df['result'] = df.log_x + df.log_x * 2

# Even better: Combine operations
df['result'] = df.x.log() * 3  # Simplified math
```

## Performance Profiling

### Basic Profiling

```python
import time
import vaex

df = vaex.open('large_file.hdf5')

# Time operations
start = time.time()
result = df.x.mean()
elapsed = time.time() - start
print(f"Computed in {elapsed:.2f} seconds")
```

### Detailed Profiling

```python
# Profile with context manager
with vaex.profiler():
    result = df.groupby('category').agg({'value': 'sum'})
# Prints detailed timing information
```

### Benchmarking Patterns

```python
# Compare strategies
def benchmark_operation(operation, name):
    start = time.time()
    result = operation()
    elapsed = time.time() - start
    print(f"{name}: {elapsed:.3f}s")
    return result

# Test different approaches
benchmark_operation(lambda: df.x.mean(), "Direct mean")
benchmark_operation(lambda: df[df.x > 0].x.mean(), "Filtered mean")
benchmark_operation(lambda: df.x.mean(selection='positive'), "Selection mean")
```

## Common Performance Issues and Solutions

### Issue: Slow Aggregations

```python
# Problem: Multiple separate aggregations
for col in df.column_names:
    print(f"{col}: {df[col].mean()}")

# Solution: Batch with delay=True
delayed = [df[col].mean(delay=True) for col in df.column_names]
results = vaex.execute(delayed)
for col, result in zip(df.column_names, results):
    print(f"{col}: {result}")
```

### Issue: High Memory Usage

```python
# Problem: Materializing large virtual columns
df['large_col'] = (complex_expression).values

# Solution: Keep virtual, or materialize and export
df['large_col'] = complex_expression  # Virtual
# Or: df.export_hdf5('with_new_col.hdf5')
```

### Issue: Slow Exports

```python
# Problem: Exporting with many virtual columns
df.export_csv('output.csv')  # Slow if many virtual columns

# Solution: Export to HDF5 or Arrow (faster)
df.export_hdf5('output.hdf5')
df.export_arrow('output.arrow')

# Or materialize first for CSV
df_materialized = df.materialize()
df_materialized.export_csv('output.csv')
```

### Issue: Repeated Complex Calculations

```python
# Problem: Complex virtual column used repeatedly
df['complex'] = df.x.log() * df.y.sqrt() + df.z ** 3
result1 = df.groupby('cat1').agg({'complex': 'mean'})
result2 = df.groupby('cat2').agg({'complex': 'sum'})
result3 = df.complex.std()

# Solution: Materialize once
df['complex'] = (df.x.log() * df.y.sqrt() + df.z ** 3).values
# Or: df = df.materialize('complex')
```

## Performance Best Practices Summary

1. **Use HDF5 or Arrow formats** - Orders of magnitude faster than CSV
2. **Leverage lazy evaluation** - Don't force computation until necessary
3. **Batch operations with delay=True** - Minimize passes through data
4. **Keep columns virtual** - Materialize only when beneficial
5. **Use selections not filters** - More efficient for multiple segments
6. **Profile your code** - Identify bottlenecks before optimizing
7. **Avoid `.values` and `.to_pandas_df()`** - Keep operations in Vaex
8. **Parallelize naturally** - Vaex uses all cores automatically
9. **Export to efficient formats** - Checkpoint complex pipelines
10. **Optimize expressions** - Simplify math and reuse calculations

## Related Resources

- For DataFrame basics: See `core_dataframes.md`
- For data operations: See `data_processing.md`
- For file I/O optimization: See `io_operations.md`

### `references/visualization.md`

# Data Visualization

This reference covers Vaex's visualization capabilities for creating plots, heatmaps, and interactive visualizations of large datasets.

## Overview

Vaex excels at visualizing datasets with billions of rows through efficient binning and aggregation. The visualization system works directly with large data without sampling, providing accurate representations of the entire dataset.

**Key features:**
- Visualize billion-row datasets interactively
- No sampling required - uses all data
- Automatic binning and aggregation
- Integration with matplotlib
- Interactive widgets for Jupyter

## Recommended: `df.viz` Accessor

Since vaex 4.0, plotting methods live on the `df.viz` accessor. This is the preferred API in current docs.

```python
import vaex

df = vaex.open('data.hdf5')

# 2D heatmap (most common)
df.viz.heatmap(df.x, df.y, limits='99.7%', show=True)

# 1D histogram via heatmap on a single axis
df.viz.heatmap(df.age, what='count(*)', shape=64, show=True)

# Multiple panels and selections
import numpy as np
df.viz.heatmap(
    [['x', 'y'], ['x', 'z']],
    limits='99.7%',
    what=np.log(vaex.stat.count() + 1),
    selection=[None, df.x < df.y],
    figsize=(10, 4),
    show=True,
)
```

The `df.viz.heatmap()` method supports subplots, selections, layers, and custom statistics via the `what` argument. See the [vaex tutorial](https://vaex.io/docs/tutorial.html) for advanced `visual` layout options.

## Legacy DataFrame Methods

`df.plot1d()` and `df.plot()` still work on the DataFrame (they delegate to the viz accessor). Existing code using these methods does not need to change, but prefer `df.viz.heatmap()` for new code.

### 1D Histograms

```python
import vaex
import matplotlib.pyplot as plt

df = vaex.open('data.hdf5')

# Simple histogram
df.plot1d(df.age)

# With customization
df.plot1d(df.age,
          limits=[0, 100],
          shape=50,              # Number of bins
          figsize=(10, 6),
          xlabel='Age',
          ylabel='Count')

plt.show()
```

### 2D Density Plots (Heatmaps)

```python
# Basic 2D plot
df.plot(df.x, df.y)

# With limits
df.plot(df.x, df.y, limits=[[0, 10], [0, 10]])

# Auto limits using percentiles
df.plot(df.x, df.y, limits='99.7%')  # 3-sigma limits

# Customize shape (resolution)
df.plot(df.x, df.y, shape=(512, 512))

# Logarithmic color scale
df.plot(df.x, df.y, f='log')
```

### Scatter Plots (Small Data)

```python
# For smaller datasets or samples
df_sample = df.sample(n=1000)

df_sample.scatter(df_sample.x, df_sample.y,
                  alpha=0.5,
                  s=10)  # Point size

plt.show()
```

## Advanced Visualization Options

### Color Scales and Normalization

```python
# Linear scale (default)
df.plot(df.x, df.y, f='identity')

# Logarithmic scale
df.plot(df.x, df.y, f='log')
df.plot(df.x, df.y, f='log10')

# Square root scale
df.plot(df.x, df.y, f='sqrt')

# Custom colormap
df.plot(df.x, df.y, colormap='viridis')
df.plot(df.x, df.y, colormap='plasma')
df.plot(df.x, df.y, colormap='hot')
```

### Limits and Ranges

```python
# Manual limits
df.plot(df.x, df.y, limits=[[xmin, xmax], [ymin, ymax]])

# Percentile-based limits
df.plot(df.x, df.y, limits='99.7%')  # 3-sigma
df.plot(df.x, df.y, limits='95%')
df.plot(df.x, df.y, limits='minmax')  # Full range

# Mixed limits
df.plot(df.x, df.y, limits=[[0, 100], 'minmax'])
```

### Resolution Control

```python
# Higher resolution (more bins)
df.plot(df.x, df.y, shape=(1024, 1024))

# Lower resolution (faster)
df.plot(df.x, df.y, shape=(128, 128))

# Different resolutions per axis
df.plot(df.x, df.y, shape=(512, 256))
```

## Statistical Visualizations

### Visualizing Aggregations

```python
# Mean on a grid
df.plot(df.x, df.y, what=df.z.mean(),
        limits=[[0, 10], [0, 10]],
        shape=(100, 100),
        colormap='viridis')

# Standard deviation
df.plot(df.x, df.y, what=df.z.std())

# Sum
df.plot(df.x, df.y, what=df.z.sum())

# Count (default)
df.plot(df.x, df.y, what='count')
```

### Multiple Statistics

```python
# Create figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Count
df.plot(df.x, df.y, what='count',
        ax=axes[0, 0], show=False)
axes[0, 0].set_title('Count')

# Mean
df.plot(df.x, df.y, what=df.z.mean(),
        ax=axes[0, 1], show=False)
axes[0, 1].set_title('Mean of z')

# Std
df.plot(df.x, df.y, what=df.z.std(),
        ax=axes[1, 0], show=False)
axes[1, 0].set_title('Std of z')

# Min
df.plot(df.x, df.y, what=df.z.min(),
        ax=axes[1, 1], show=False)
axes[1, 1].set_title('Min of z')

plt.tight_layout()
plt.show()
```

## Working with Selections

Visualize different segments of data simultaneously:

```python
import vaex
import matplotlib.pyplot as plt

df = vaex.open('data.hdf5')

# Create selections
df.select(df.category == 'A', name='group_a')
df.select(df.category == 'B', name='group_b')

# Plot both selections
df.plot1d(df.value, selection='group_a', label='Group A')
df.plot1d(df.value, selection='group_b', label='Group B')
plt.legend()
plt.show()

# 2D plot with selection
df.plot(df.x, df.y, selection='group_a')
```

### Overlay Multiple Selections

```python
# Create base plot
fig, ax = plt.subplots(figsize=(10, 8))

# Plot each selection with different colors
df.plot(df.x, df.y, selection='group_a',
        ax=ax, show=False, colormap='Reds', alpha=0.5)
df.plot(df.x, df.y, selection='group_b',
        ax=ax, show=False, colormap='Blues', alpha=0.5)

ax.set_title('Overlaid Selections')
plt.show()
```

## Subplots and Layouts

### Creating Multiple Plots

```python
import matplotlib.pyplot as plt

# Create subplot grid
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# Plot different variables
variables = ['x', 'y', 'z', 'a', 'b', 'c']
for idx, var in enumerate(variables):
    row = idx // 3
    col = idx % 3
    df.plot1d(df[var], ax=axes[row, col], show=False)
    axes[row, col].set_title(f'Distribution of {var}')

plt.tight_layout()
plt.show()
```

### Faceted Plots

```python
# Plot by category
categories = df.category.unique()

fig, axes = plt.subplots(1, len(categories), figsize=(15, 5))

for idx, cat in enumerate(categories):
    df_cat = df[df.category == cat]
    df_cat.plot(df_cat.x, df_cat.y,
                ax=axes[idx], show=False)
    axes[idx].set_title(f'Category {cat}')

plt.tight_layout()
plt.show()
```

## Interactive Widgets (Jupyter)

Create interactive visualizations in Jupyter notebooks:

### Selection Widget

```python
# Interactive selection
df.widget.selection_expression()
```

### Histogram Widget

```python
# Interactive histogram with selection
df.plot_widget(df.x, df.y)
```

### Scatter Widget

```python
# Interactive scatter plot
df.scatter_widget(df.x, df.y)
```

## Customization

### Styling Plots

```python
import matplotlib.pyplot as plt

# Create plot with custom styling
fig, ax = plt.subplots(figsize=(12, 8))

df.plot(df.x, df.y,
        limits='99%',
        shape=(256, 256),
        colormap='plasma',
        ax=ax,
        show=False)

# Customize axes
ax.set_xlabel('X Variable', fontsize=14, fontweight='bold')
ax.set_ylabel('Y Variable', fontsize=14, fontweight='bold')
ax.set_title('Custom Density Plot', fontsize=16, fontweight='bold')
ax.grid(alpha=0.3)

# Add colorbar
plt.colorbar(ax.collections[0], ax=ax, label='Density')

plt.tight_layout()
plt.show()
```

### Figure Size and DPI

```python
# High-resolution plot
df.plot(df.x, df.y,
        figsize=(12, 10),
        dpi=300)
```

## Specialized Visualizations

### Hexbin Plots

```python
# Alternative to heatmap using hexagonal bins
plt.figure(figsize=(10, 8))
plt.hexbin(df.x.values[:100000], df.y.values[:100000],
           gridsize=50, cmap='viridis')
plt.colorbar(label='Count')
plt.xlabel('X')
plt.ylabel('Y')
plt.show()
```

### Contour Plots

```python
import numpy as np

# Get 2D histogram data
counts = df.count(binby=[df.x, df.y],
                  limits=[[0, 10], [0, 10]],
                  shape=(100, 100))

# Create contour plot
x = np.linspace(0, 10, 100)
y = np.linspace(0, 10, 100)
plt.contourf(x, y, counts.T, levels=20, cmap='viridis')
plt.colorbar(label='Count')
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Contour Plot')
plt.show()
```

### Vector Field Overlay

```python
# Compute mean vectors on grid
mean_vx = df.mean(df.vx, binby=[df.x, df.y],
                  limits=[[0, 10], [0, 10]],
                  shape=(20, 20))
mean_vy = df.mean(df.vy, binby=[df.x, df.y],
                  limits=[[0, 10], [0, 10]],
                  shape=(20, 20))

# Create grid
x = np.linspace(0, 10, 20)
y = np.linspace(0, 10, 20)
X, Y = np.meshgrid(x, y)

# Plot
fig, ax = plt.subplots(figsize=(10, 8))

# Base heatmap
df.plot(df.x, df.y, ax=ax, show=False)

# Vector overlay
ax.quiver(X, Y, mean_vx.T, mean_vy.T, alpha=0.7, color='white')

plt.show()
```

## Performance Considerations

### Optimizing Large Visualizations

```python
# For very large datasets, reduce shape
df.plot(df.x, df.y, shape=(256, 256))  # Fast

# For publication quality
df.plot(df.x, df.y, shape=(1024, 1024))  # Higher quality

# Balance quality and performance
df.plot(df.x, df.y, shape=(512, 512))  # Good balance
```

### Caching Visualization Data

```python
# Compute once, plot multiple times
counts = df.count(binby=[df.x, df.y],
                  limits=[[0, 10], [0, 10]],
                  shape=(512, 512))

# Use in different plots
plt.figure()
plt.imshow(counts.T, origin='lower', cmap='viridis')
plt.colorbar()
plt.show()

plt.figure()
plt.imshow(np.log10(counts.T + 1), origin='lower', cmap='plasma')
plt.colorbar()
plt.show()
```

## Export and Saving

### Saving Figures

```python
# Save as PNG
df.plot(df.x, df.y)
plt.savefig('plot.png', dpi=300, bbox_inches='tight')

# Save as PDF (vector)
plt.savefig('plot.pdf', bbox_inches='tight')

# Save as SVG
plt.savefig('plot.svg', bbox_inches='tight')
```

### Batch Plotting

```python
# Generate multiple plots
variables = ['x', 'y', 'z']

for var in variables:
    plt.figure(figsize=(10, 6))
    df.plot1d(df[var])
    plt.title(f'Distribution of {var}')
    plt.savefig(f'plot_{var}.png', dpi=300, bbox_inches='tight')
    plt.close()
```

## Common Patterns

### Pattern: Exploratory Data Analysis

```python
import matplotlib.pyplot as plt

# Create comprehensive visualization
fig = plt.figure(figsize=(16, 12))

# 1D histograms
ax1 = plt.subplot(3, 3, 1)
df.plot1d(df.x, ax=ax1, show=False)
ax1.set_title('X Distribution')

ax2 = plt.subplot(3, 3, 2)
df.plot1d(df.y, ax=ax2, show=False)
ax2.set_title('Y Distribution')

ax3 = plt.subplot(3, 3, 3)
df.plot1d(df.z, ax=ax3, show=False)
ax3.set_title('Z Distribution')

# 2D plots
ax4 = plt.subplot(3, 3, 4)
df.plot(df.x, df.y, ax=ax4, show=False)
ax4.set_title('X vs Y')

ax5 = plt.subplot(3, 3, 5)
df.plot(df.x, df.z, ax=ax5, show=False)
ax5.set_title('X vs Z')

ax6 = plt.subplot(3, 3, 6)
df.plot(df.y, df.z, ax=ax6, show=False)
ax6.set_title('Y vs Z')

# Statistics on grids
ax7 = plt.subplot(3, 3, 7)
df.plot(df.x, df.y, what=df.z.mean(), ax=ax7, show=False)
ax7.set_title('Mean Z on X-Y grid')

plt.tight_layout()
plt.savefig('eda_summary.png', dpi=300, bbox_inches='tight')
plt.show()
```

### Pattern: Comparison Across Groups

```python
# Compare distributions by category
categories = df.category.unique()

fig, axes = plt.subplots(len(categories), 2,
                         figsize=(12, 4 * len(categories)))

for idx, cat in enumerate(categories):
    df.select(df.category == cat, name=f'cat_{cat}')

    # 1D histogram
    df.plot1d(df.value, selection=f'cat_{cat}',
              ax=axes[idx, 0], show=False)
    axes[idx, 0].set_title(f'Category {cat} - Distribution')

    # 2D plot
    df.plot(df.x, df.y, selection=f'cat_{cat}',
            ax=axes[idx, 1], show=False)
    axes[idx, 1].set_title(f'Category {cat} - X vs Y')

plt.tight_layout()
plt.show()
```

### Pattern: Time Series Visualization

```python
# Aggregate by time bins
df['year'] = df.timestamp.dt.year
df['month'] = df.timestamp.dt.month

# Plot time series
monthly_sales = df.groupby(['year', 'month']).agg({'sales': 'sum'})

plt.figure(figsize=(14, 6))
plt.plot(range(len(monthly_sales)), monthly_sales['sales'])
plt.xlabel('Time Period')
plt.ylabel('Sales')
plt.title('Sales Over Time')
plt.grid(alpha=0.3)
plt.show()
```

## Integration with Other Libraries

### Plotly for Interactivity

```python
import plotly.graph_objects as go

# Get data from Vaex
counts = df.count(binby=[df.x, df.y], shape=(100, 100))

# Create plotly figure
fig = go.Figure(data=go.Heatmap(z=counts.T))
fig.update_layout(title='Interactive Heatmap')
fig.show()
```

### Seaborn Style

```python
import seaborn as sns
import matplotlib.pyplot as plt

# Use seaborn styling
sns.set_style('darkgrid')
sns.set_palette('husl')

df.plot1d(df.value)
plt.show()
```

## Best Practices

1. **Use appropriate shape** - Balance resolution and performance (256-512 for exploration, 1024+ for publication)
2. **Apply sensible limits** - Use percentile-based limits ('99%', '99.7%') to handle outliers
3. **Choose color scales wisely** - Log scale for wide-ranging counts, linear for uniform data
4. **Leverage selections** - Compare subsets without creating new DataFrames
5. **Cache aggregations** - Compute once if creating multiple similar plots
6. **Use vector formats for publication** - Save as PDF or SVG for scalable figures
7. **Avoid sampling** - Vaex visualizations use all data, no sampling needed

## Troubleshooting

### Issue: Empty or Sparse Plot

```python
# Problem: Limits don't match data range
df.plot(df.x, df.y, limits=[[0, 10], [0, 10]])

# Solution: Use automatic limits
df.plot(df.x, df.y, limits='minmax')
df.plot(df.x, df.y, limits='99%')
```

### Issue: Plot Too Slow

```python
# Problem: Too high resolution
df.plot(df.x, df.y, shape=(2048, 2048))

# Solution: Reduce shape
df.plot(df.x, df.y, shape=(512, 512))
```

### Issue: Can't See Low-Density Regions

```python
# Problem: Linear scale overwhelmed by high-density areas
df.plot(df.x, df.y, f='identity')

# Solution: Use logarithmic scale
df.plot(df.x, df.y, f='log')
```

## Related Resources

- For data aggregation: See `data_processing.md`
- For performance optimization: See `performance.md`
- For DataFrame basics: See `core_dataframes.md`
