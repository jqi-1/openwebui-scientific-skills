---
name: geopandas
description: Guidance and local audit tools for Python workflows that directly use GeoPandas GeoSeries, GeoDataFrame, spatial operations, or vector-data I/O.
---

# GeoPandas

Use GeoPandas for planar vector data represented as pandas-like `GeoSeries` and
`GeoDataFrame` objects. This skill targets stable **GeoPandas 1.1.4** (released
2026-06-26), not the unreleased 1.2 documentation.

## Reproducible environment

GeoPandas 1.1.4 requires Python 3.10+; its tagged source requires NumPy >=1.24,
pandas >=2.0, Shapely >=2.0, pyproj >=3.5, pyogrio >=0.7.2, and `packaging`.
This exact Python 3.12 snapshot was smoke-tested on 2026-07-23:

```bash
uv venv --python 3.12
uv pip install \
  "geopandas==1.1.4" \
  "numpy==2.5.1" \
  "pandas==3.0.5" \
  "shapely==2.1.2" \
  "pyproj==3.7.2" \
  "pyogrio==0.13.0" \
  "pyarrow==25.0.0" \
  "packaging==26.2"
```

Keep optional plotting and PostGIS packages pinned in the project lock as well.
Do not mix binary geospatial packages from incompatible package channels.

## Safety and privacy contract

- Treat exact coordinates, addresses, parcel boundaries, trajectories, and
  small-area joins as sensitive. Default reports to counts, categories, coarse
  extents, and redacted identifiers. Generalize before publication.
- Never automatically load a URL, cloud URI, GDAL `/vsi*` path, archive, or
  geocode an address. Obtain explicit approval, validate provenance and hashes,
  then stage an unpacked local file in an isolated workspace.
- GDAL/OGR drivers, GEOS, PROJ, pyogrio, Shapely, pyproj, and their wheels are a
  native-code trust boundary. Prefer official wheels/conda-forge, record native
  versions, restrict drivers, and process untrusted data in a sandbox.
- Do not open macro-enabled office files or nested archives through permissive
  GDAL drivers. The bundled CLIs use an extension allowlist and reject archives.
- Read only named database secrets such as `GEOPANDAS_POSTGIS_PASSWORD`; use a
  secret manager or scoped environment variable. Never embed a password in a
  URL or source, print an engine/URL, or dump the environment.
- Every derived artifact needs source hashes/versions, CRS, operation parameters,
  predicate, join cardinality, precision/repair choices, and row-count checks.

## Correctness gates

Apply these gates before trusting a result:

1. **Identity and provenance** — identify the source layer, stable feature key,
   duplicate IDs, row count, geometry column, parser/driver, and content hash.
2. **Geometry state** — count null, empty, invalid, mixed, Z/M, and collapsed
   geometries separately. `None` is missing; an empty Shapely geometry is real.
3. **CRS semantics** — require CRS metadata. `set_crs()` assigns metadata;
   `to_crs()` transforms coordinates. Never guess a CRS from coordinate ranges.
4. **Units and operation** — GeoPandas is planar. Geographic coordinates are
   angular; do not use them directly for buffer, distance, area, nearest joins,
   precision grids, or tolerances. Choose a fit-for-purpose local/equal-area CRS
   or a geodesic method.
5. **Transform quality** — inspect axis order, area of use, datum pipeline,
   expected accuracy, ballpark status, and missing grids. Keep PROJ network
   disabled unless the user explicitly approves grid retrieval.
6. **Topology and precision** — validate before and after repair/overlay. Pick a
   precision grid from source accuracy and CRS units; arbitrary snapping can
   collapse features or create bias.
7. **Cardinality** — state expected one-to-one, one-to-many, or many-to-many
   behavior before `merge`, `sjoin`, or `sjoin_nearest`; audit unmatched and
   multiplied rows afterward.
8. **Output contract** — use a new output path, preserve a stable feature ID,
   document schema/CRS/encoding, reopen the artifact, and compare counts/types.

## CRS and antimeridian rules

GeoPandas stores CRS as `pyproj.CRS`. Coordinate arrays use traditional GIS
`(x, y)` order, while authority definitions can advertise latitude-first axes.
Use `Transformer(..., always_xy=True)` for explicit coordinate-array pipelines,
and record that choice.

`to_crs()` transforms vertices and assumes each segment is straight in the
source CRS; it does not transform geodesic arcs. Geometries crossing ±180° or a
projection boundary can be badly wrapped. Detect crossings, split/unwrap and
densify in a documented geographic representation, transform parts, then
validate. Do not use Web Mercator as a general measurement CRS.

```python
crs = gdf.crs  # a pyproj.CRS when present
if crs is None or crs.is_geographic:
    raise ValueError("Choose a justified projected CRS before planar measurement")

unit_names = [axis.unit_name for axis in crs.axis_info]
areas = gdf.geometry.area  # square CRS units, not automatically square metres
```

See [CRS management](references/crs-management.md).

## Core API decisions

### Data structures

- A `GeoDataFrame` can hold multiple geometry columns, each with CRS metadata,
  but only `active_geometry_name` drives frame-level spatial operations.
- Binary `GeoSeries` methods are row-wise and align by index by default. Use
  `align=False` only when positional pairing is explicitly intended and lengths
  and order were verified.
- Duplicate column names and duplicate feature IDs are ambiguous; reject or
  resolve them before joins and exports.

See [data structures](references/data-structures.md).

### Geometry validity, precision, and union

Use `is_valid` and redacted `is_valid_reason()` categories before
`make_valid(method="linework"|"structure", keep_collapsed=...)`. Repair can
change geometry type or dimension; retain the original and compare counts,
area, types, empties, and collapsed parts.

`set_precision(grid_size, mode=...)` uses **CRS units** and may remove duplicate
vertices or collapse features. `union_all(method="unary", grid_size=...)` is the
robust default. Use `coverage` only after `is_valid_coverage()` proves
non-overlap and edge matching; use `disjoint_subset` with Shapely >=2.1 when its
partitioning assumption is useful.

See [geometric operations](references/geometric-operations.md).

### Joins, overlay, clip, and dissolve

- `sjoin` predicates are directional: `left.within(right)` is not
  `left.contains(right)`. `intersects` includes boundary contact; `contains`
  excludes boundary-only points, while `covers` includes boundary points.
- `predicate="dwithin"` requires `distance`; scalar or per-left-row distances
  are in CRS units. `sjoin_nearest` returns all equidistant nearest matches and
  does **not** implement a `k=` parameter.
- `overlay(..., make_valid=True)` repairs invalid input but can change types;
  `keep_geom_type=None` drops other types with a warning. Precision mismatch can
  create slivers; quantify them rather than silently deleting them.
- `clip` dissolves the mask. Rectangle clipping is fast but possibly dirty and
  may omit a line collapsed to a point; validate its output.
- `dissolve` combines `groupby.agg` with `union_all`; choose explicit attribute
  aggregations and audit null group keys.

See [spatial analysis](references/spatial-analysis.md).

### I/O, Arrow, and PostGIS

GeoPandas 1.x defaults to pyogrio. Driver availability and semantics come from
the installed GDAL, not GeoPandas alone. Prefer local GeoPackage for general
interchange and WKB GeoParquet for columnar interoperability.

GeoParquet defaults to stable schema 1.0.0. Native GeoArrow encodings and bbox
covering require schema 1.1.0 and remain less interoperable. A missing GeoParquet
`crs` key means `OGC:CRS84`; explicit `crs: null` means unknown—do not conflate
them. Reopen and validate every export.

Use parameterized SQL and a SQLAlchemy `Engine`/`Connection` for PostGIS.
`if_exists="replace"` is destructive; default to `"fail"` and use a transaction.

See [data I/O](references/data-io.md).

## Migration checklist

For code moving from GeoPandas 0.14 or earlier:

- GeoPandas 1.0 supports Shapely >=2 only; PyGEOS, Shapely <2, and the rtree
  spatial-index backend were removed.
- pyogrio replaced Fiona as the installed/default I/O engine. Set `engine=`
  explicitly and test schema, empty, datetime, encoding, and append behavior.
- Replace `sjoin(op=...)` with `predicate=`, `sindex.query_bulk()` with
  `sindex.query()`, `unary_union` with `union_all()`, and
  `GeometryArray.data` with `to_numpy()`/`np.asarray`.
- Replace `read_file(include_fields=...|ignore_fields=...)` with `columns=`.
  Use `schema_version=`, not the removed GeoParquet `version=` compatibility.
- Do not use removed `geopandas.datasets`, internal `geopandas.io.*` entry
  points, plot `axes`/`colormap`, or set-operation operators.
- `explode()` now defaults `index_parts=False`; a named Series passed to
  `set_geometry()` supplies the new active-column name; a named right index can
  replace `index_right` in `sjoin` output.
- Do not assign `.crs` to override metadata or rely on deprecated
  `set_geometry(drop=...)`; use explicit `set_crs()` and rename/drop steps.
- GeoPandas 1.1 requires Python >=3.10, pandas >=2.0, NumPy >=1.24, and pyproj
  >=3.5. Version 1.1.2 fixed SQL injection through a PostGIS geometry-column
  name; the pinned 1.1.4 includes that fix.

### Plotting and exploration

Maps are analytical outputs: label units, classification method, missing data,
normalization denominator, and date. `explore()` can expose every attribute in
tooltips/popups and contact tile/CDN servers; generalize first and use
`tiles=None`, `tooltip=False`, and `popup=False` for a local draft.

See [visualization](references/visualization.md).

## Bundled local CLIs

All helpers are deterministic, reject network/archive paths, bound input bytes
and feature counts, keep imports lazy so `--help` is dependency-free, and emit
JSON without coordinates or record identifiers.

| CLI | Purpose |
|---|---|
| `scripts/vector_inventory.py` | Redacted local vector/GeoParquet technical inventory |
| `scripts/crs_reprojection_plan.py` | CRS units, axes, candidate transform and antimeridian plan |
| `scripts/geometry_validity_report.py` | Dry-run validity audit; optional repair to a new GeoPackage |
| `scripts/spatial_join_audit.py` | Predicate semantics, duplicate IDs and join cardinality |
| `scripts/export_plan.py` | Non-executing vector/GeoParquet export contract |
| `scripts/sensitive_coordinates_checklist.py` | Privacy/generalization release gate |

```bash
python skills/geopandas/scripts/vector_inventory.py --help
python skills/geopandas/scripts/crs_reprojection_plan.py \
  --source-crs EPSG:4326 --target-crs EPSG:32631
python skills/geopandas/scripts/geometry_validity_report.py data.gpkg
python skills/geopandas/scripts/spatial_join_audit.py points.gpkg zones.gpkg \
  --predicate within --left-id point_id --right-id zone_id
python skills/geopandas/scripts/export_plan.py data.gpkg result.parquet \
  --format geoparquet --schema-version 1.0.0 \
  --stable-id-column feature_id --id-unique-verified
python skills/geopandas/scripts/sensitive_coordinates_checklist.py \
  --public-output --precise-points --contains-addresses
```

## Reference index

- [Data structures](references/data-structures.md)
- [CRS management](references/crs-management.md)
- [Geometric operations](references/geometric-operations.md)
- [Spatial analysis](references/spatial-analysis.md)
- [Data I/O](references/data-io.md)
- [Visualization](references/visualization.md)

## Sources (verified 2026-07-23)

- [GeoPandas 1.1.4 on PyPI](https://pypi.org/project/geopandas/1.1.4/) — released 2026-06-26.
- [GeoPandas 1.1.4 release](https://github.com/geopandas/geopandas/releases/tag/v1.1.4) — bug-fix release.
- [GeoPandas 1.1.4 tagged dependencies](https://github.com/geopandas/geopandas/blob/v1.1.4/pyproject.toml).
- [Stable GeoPandas documentation](https://geopandas.org/en/stable/).
- [GeoPandas 1.0 migration release](https://github.com/geopandas/geopandas/releases/tag/v1.0.0).

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/geopandas/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/crs-management.md`

# CRS, units, and reprojection

A CRS is part of the data model, not display metadata. An incorrect or missing
CRS can make numerically plausible results geographically wrong.

## Require authoritative CRS metadata

```python
from pyproj import CRS

if gdf.crs is None:
    raise ValueError("CRS is missing; recover it from authoritative source metadata")

crs = CRS.from_user_input(gdf.crs)
```

Do not infer EPSG:4326 because values resemble longitude/latitude. Coordinate
ranges are not evidence of datum, axis interpretation, units, or epoch.

### `set_crs` versus `to_crs`

```python
# Assign metadata only; coordinate numbers do not change.
gdf = gdf.set_crs("EPSG:4326")

# Transform coordinates; the source CRS must already be set.
projected = gdf.to_crs("EPSG:32631")
```

- Use `set_crs()` only when the coordinate values are already expressed in that
  CRS and metadata is absent or demonstrably wrong.
- Replacing existing metadata requires `allow_override=True`; record why.
- Use `to_crs()` to transform the active geometry column. Transform each
  additional geometry column explicitly.
- Do not assign `gdf.crs = ...`; manual override is deprecated.

## Axis order

EPSG definitions can be latitude/longitude while GIS coordinate arrays are
normally x/y (longitude/latitude). Inspect the authority axes:

```python
for axis in crs.axis_info:
    print(axis.name, axis.abbrev, axis.direction, axis.unit_name)
```

For explicit pyproj transformations, request traditional GIS x/y order:

```python
from pyproj import Transformer

transformer = Transformer.from_crs(
    source_crs,
    target_crs,
    always_xy=True,
    allow_ballpark=False,
    only_best=True,
)
x_out, y_out = transformer.transform(x_in, y_in, errcheck=True)
```

Record `always_xy=True`; it changes the API coordinate order, not the CRS
definition. GeoParquet 1.1 explicitly stores WKB/native coordinates as x/y even
when the CRS authority uses another axis order.

## Units and planar operations

GeoPandas and Shapely compute planar Cartesian geometry and ignore Z:

- geographic longitude/latitude axes are angular, usually degrees;
- projected axes may be metres, US survey feet, feet, or another linear unit;
- `.area` returns squared coordinate units;
- `.length`, `.distance`, `.buffer`, `sjoin_nearest(max_distance=...)`,
  `sjoin(predicate="dwithin", distance=...)`, precision grids, simplify
  tolerances, and gap widths use coordinate units.

```python
axis_units = [(axis.unit_name, axis.unit_conversion_factor) for axis in crs.axis_info]
if crs.is_geographic:
    raise ValueError("Planar measurement on angular coordinates is not accepted")
```

Do not label an output metres merely because a CRS is projected. Convert units
using the CRS axis metadata and document the conversion. Web Mercator
(`EPSG:3857`) is for web display, not general area/distance analysis.

### Choosing a measurement CRS

Choose based on the operation, study extent, datum, and required accuracy:

- local UTM or another local conformal CRS for local distances/angles;
- an equal-area CRS for area totals and areal normalization;
- an equidistant/azimuthal design for a specified distance origin;
- geodesic methods for large/global geographic extents.

`estimate_utm_crs()` is a convenience based on dataset bounds, not a proof of
suitability. It can be poor for multi-zone, polar, antimeridian-crossing, or
very large datasets.

## Geodesic measurements

When projection distortion is unacceptable, use the ellipsoid associated with
the CRS through `pyproj.Geod`, not Shapely's planar distance:

```python
geod = crs.get_geod()
azimuth_fwd, azimuth_back, metres = geod.inv(lon1, lat1, lon2, lat2)
area_m2, perimeter_m = geod.geometry_area_perimeter(polygon)
```

Ensure inputs are longitude/latitude on the intended geodetic datum. Geodesic
area is signed according to ring orientation and has documented limitations for
very large polygons; normalize orientation and test known controls.

## Datum transformations and operation selection

The same source/target CRS pair can have several operations. Selection depends
on area of interest, installed grids, authority, and accuracy:

```python
from pyproj.aoi import AreaOfInterest
from pyproj.transformer import TransformerGroup
from pyproj import network

network.set_network_enabled(False)
group = TransformerGroup(
    source_crs,
    target_crs,
    always_xy=True,
    area_of_interest=AreaOfInterest(west, south, east, north),
    allow_ballpark=False,
)

if not group.best_available:
    raise RuntimeError("Best transformation unavailable; inspect missing grids")

candidate = group.transformers[0]
print(candidate.description, candidate.accuracy, candidate.area_of_use)
```

Privacy note: an exact area of interest can reveal a sensitive study location.
Do not log it; retain only an approved coarse region or protected audit record.

Operational rules:

1. Set `allow_ballpark=False` for accuracy-sensitive work.
2. Use `only_best=True` with `Transformer.from_crs()` when failure is preferable
   to silently selecting a lower-quality operation.
3. Verify `accuracy` (`-1` means unknown) and `area_of_use`.
4. Inspect `TransformerGroup.unavailable_operations` for missing grids.
5. Keep PROJ network disabled by default. pyproj wheels do not include all
   transformation grids; downloading grids is a separate, explicit network and
   supply-chain action.
6. Record PROJ database/native versions and the selected operation description.
7. For dynamic CRS, record coordinate epoch. A CRS alone may be insufficient.

The bundled `scripts/crs_reprojection_plan.py` performs this inspection without
transforming coordinates or enabling network access.

## Geometry transformation caveat

`GeoDataFrame.to_crs()` transforms every existing vertex. It does not interpret
a segment as a geodesic arc:

```python
out = gdf.to_crs(target_crs)
```

If source linework is sparse, densify according to a documented geodesic or
source-space tolerance before projection when shape fidelity matters. Validate
the resulting topology and bounds.

## Antimeridian and projection boundaries

`to_crs()` warns that objects crossing the dateline or another projection
boundary have undesirable behavior. A naive line from 179°E to 179°W can be
treated as spanning almost the whole map.

Safe workflow:

1. Normalize and validate longitude convention (`[-180, 180]` or `[0, 360)`).
2. Detect segment jumps and bbox representations that cross the antimeridian.
3. Split/unwrap at ±180° in a documented geographic CRS.
4. Densify geodesic edges if required by the accuracy target.
5. Transform each part with an operation valid for its area.
6. Reassemble only when target topology permits it.
7. Compare source/target control points, feature counts, validity, and bounds.

For transformed bounds, use `Transformer.transform_bounds(..., densify_pts=...)`.
When geographic output returns `right < left`, pyproj documents that the bounds
cross the antimeridian and should be represented as two polygons. Do not sort
the numbers and erase that meaning.

## CRS equality and concatenation

Compare semantic CRS objects, not raw WKT strings:

```python
left_crs = CRS.from_user_input(left.crs)
right_crs = CRS.from_user_input(right.crs)
if not left_crs.equals(right_crs):
    right = right.to_crs(left_crs)
```

Equivalent does not mean equally appropriate for the analysis. Before concat,
join, overlay, or clip, require matching CRS and confirm both datasets use the
same coordinate epoch/realization where relevant.

## Reprojection provenance

Record:

- source and target CRS as WKT2/PROJJSON plus authority IDs when available;
- source of CRS assignment and any override;
- axis order exposed by the CRS and API order (`always_xy`);
- units and conversion factors;
- area of interest at an approved precision;
- chosen operation, expected accuracy, ballpark policy, and area of use;
- required/available grids, network policy, PROJ data/database versions;
- densification, antimeridian splitting, precision, and validation checks.

## Sources (verified 2026-07-23)

- [GeoPandas projections guide](https://geopandas.org/en/stable/docs/user_guide/projections.html).
- [GeoDataFrame.to_crs](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_crs.html).
- [GeoDataFrame.set_crs](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.set_crs.html).
- [pyproj Transformer API 3.7.2](https://pyproj4.github.io/pyproj/stable/api/transformer.html) — page updated 2025-07-02.
- [pyproj CRS API 3.7.2](https://pyproj4.github.io/pyproj/stable/api/crs/crs.html).
- [pyproj transformation grids](https://pyproj4.github.io/pyproj/stable/transformation_grids.html).
- [pyproj Geod API](https://pyproj4.github.io/pyproj/stable/api/geod.html).
- [GeoParquet 1.1.0 CRS and axis-order rules](https://geoparquet.org/releases/v1.1.0/).

### `references/data-io.md`

# Vector I/O, GeoParquet, Arrow, and PostGIS

GeoPandas 1.x defaults to pyogrio for vector-file I/O. pyogrio and Fiona are
bindings to GDAL/OGR; actual formats, options, and behavior depend on the
installed native GDAL and drivers.

## Local-only intake policy

Do not automatically pass any of these to GeoPandas/GDAL:

- `http://`, `https://`, `s3://`, `gs://`, Azure, or another remote URI;
- GDAL `/vsicurl/`, `/vsis3/`, `/vsizip/`, chained virtual filesystems, or
  pyogrio `zip+...` paths;
- ZIP/KMZ/TAR/GZ/7z/RAR or nested archives;
- macro-enabled office files or an untrusted permissive driver;
- a user-supplied PostGIS connection string.

GeoPandas officially supports URLs and GDAL supports network/archive virtual
filesystems, but that capability crosses network, decompression, parser, and
credential trust boundaries. Obtain explicit approval, verify source/hash and
size out of band, unpack in a sandbox with resource limits, then process an
allowlisted local regular file.

The bundled CLIs reject URL/VSI/archive syntax, symlinks, path traversal, and
non-allowlisted suffixes.

## Inspect before reading features

For GDAL-backed formats:

```python
from pathlib import Path
import pyogrio

path = Path("approved/input.gpkg")
if not path.is_file() or path.is_symlink():
    raise ValueError("Expected a vetted local regular file")

layers = pyogrio.list_layers(path)
info = pyogrio.read_info(path, layer="approved_layer", force_feature_count=False)
drivers = pyogrio.list_drivers()
```

Record:

- primary-file hash and byte size (a Shapefile hash does not cover sidecars);
- driver, layer, declared feature count, fields/dtypes, encoding, geometry type;
- CRS and whether bounds were present, but redact precise bounds by default;
- `pyogrio.__gdal_version__`, `pyogrio.__gdal_geos_version__`, Shapely GEOS,
  pyproj PROJ, package versions, and enabled driver capabilities.

`list_drivers()` returns capabilities containing `r`, `w`, and/or `a`, but a
listed driver is not proof every field/geometry is supported. Treat drivers as
an allowlist, not merely a discovered list.

## `read_file`

Stable signature:

```python
gdf = geopandas.read_file(
    filename,
    bbox=None,
    mask=None,
    columns=None,
    rows=None,
    engine="pyogrio",
    use_arrow=True,
)
```

Rules:

- `bbox` and `mask` are mutually exclusive.
- With pyogrio, a bbox tuple must already be in the dataset CRS. Fiona can
  reproject a GeoSeries/GeoDataFrame bbox; do not depend on engine-specific
  implicit behavior.
- A mask must have an explicit CRS compatible with the source.
- `columns=[]` reads geometry without attributes; `ignore_geometry=True`
  returns a pandas DataFrame.
- `rows=n` reads the first n rows; `rows=slice(a, b)` reads a slice.
- `where=` is evaluated by a driver SQL dialect. Do not concatenate untrusted
  expressions.
- Encoding auto-detection can fail; set a verified encoding explicitly.
- `use_arrow=True` requires PyArrow and speeds pyogrio bulk transfer, but does
  not change parser trust or correctness requirements.
- Bound both file bytes and features. Some drivers cannot cheaply report a
  count; read at most `limit + 1` and fail closed when the limit is exceeded.

GeoPandas may use HTTP range requests or download an entire URL in memory.
This skill therefore does not include remote-read examples.

## Filters are not always exact

pyogrio documents:

- `bbox`/`mask` coordinates must use the dataset CRS;
- when GDAL is built with GEOS, geometry intersection filtering is exact;
- without GEOS, filters can return features whose **bounding boxes** intersect,
  requiring a second exact predicate check;
- Arrow reads involving skip/max may read batches beyond the requested slice
  before slicing;
- feature IDs are driver-specific and may start at 0, 1, or another value.

Do not treat driver FID as a portable stable feature ID.

## Writing traditional vector formats

Write a new path and reopen it:

```python
output = Path("derived/result.gpkg")
if output.exists() or output.is_symlink():
    raise FileExistsError("Choose a new output path")

gdf.to_file(
    output,
    layer="result",
    driver="GPKG",
    engine="pyogrio",
    index=False,
    use_arrow=True,
)

roundtrip = geopandas.read_file(output, layer="result", engine="pyogrio")
```

Never use implicit overwrite/append. Driver behavior varies and multi-file
formats complicate atomic writes.

### Format tradeoffs

- **GeoPackage**: good general local interchange; multiple layers, one geometry
  column per layer, SQL-backed metadata.
- **GeoJSON**: broadly interoperable but normally WGS84 longitude/latitude,
  limited type fidelity, text-heavy, and easy to leak precise coordinates.
- **Shapefile**: legacy multi-file format with field-name, type, null, encoding,
  geometry, and size constraints. Avoid for new work.
- **FlatGeobuf**: efficient stream/spatial-index format, but interoperability
  still depends on driver versions.
- **GeoParquet**: efficient columnar storage with multiple geometry columns and
  explicit geospatial metadata.

Traditional formats often cannot store lists, structs, arbitrary objects, or
multiple geometry columns. Plan conversions and reject silent loss.

## GeoParquet and Feather

```python
gdf.to_parquet(
    "derived/result.parquet",
    index=False,
    compression="snappy",
    geometry_encoding="WKB",
    write_covering_bbox=False,
    schema_version="1.0.0",
)

roundtrip = geopandas.read_parquet(
    "derived/result.parquet",
    columns=["feature_id", "geometry"],
)
```

GeoPandas 1.1.4 write semantics:

- all geometry columns are preserved;
- default `geometry_encoding="WKB"` maximizes interoperability;
- default supported stable schema is **1.0.0**;
- `geometry_encoding="geoarrow"` requires GeoParquet 1.1.0, supports
  single-geometry native encodings, and is still described as experimental;
- `write_covering_bbox=True` adds a per-row `bbox` column and 1.1 covering
  metadata. It costs compute and may reveal precise extents;
- `schema_version` replaces the removed/deprecated old `version=` usage;
- `index=None` writes non-RangeIndex values as columns and stores RangeIndex as
  metadata. Use an explicit stable feature-ID column instead.

Read semantics:

- selecting no geometry columns raises; use `pandas.read_parquet` for a
  non-spatial result;
- if the stored primary geometry is omitted, the first selected geometry
  becomes active;
- bbox filtering works only when covering metadata/columns were written;
- if GeoParquet `crs` metadata is **missing**, the specification default is
  `OGC:CRS84`;
- an explicit `crs: null` means unknown/undefined, which is different;
- WKB/native coordinates are x/y regardless of authority axis order.

GeoParquet 1.1 metadata requires a `geo` JSON value, `primary_column`, and
metadata for every geometry column. Geometry columns must be root-level and may
be optional; native child coordinates cannot contain nulls. `edges` defaults to
`planar`. Feature identifiers are outside the core specification, so define and
document your own stable-ID metadata/column.

Do not use bbox covering for public sensitive-location data without
generalization and approval.

### Arrow in memory

GeoPandas 1.0 added `to_arrow()` and `from_arrow()` using GeoArrow extension
types. These improve interchange but do not make an array self-validating:
verify extension metadata, CRS, geometry encoding/type, nulls, and active
geometry after round-trip. GeoPandas 1.1 adds `to_pandas_kwargs` controls for
non-geometry Arrow conversion.

## PostGIS without credential leakage

Required writing dependencies are SQLAlchemy, GeoAlchemy2, and psycopg/psycopg2.
Create connections from named secrets without embedding or logging a connection
URL:

```python
import os
from sqlalchemy import URL, create_engine

db_url = URL.create(
    "postgresql+psycopg",
    username=os.environ["GEOPANDAS_POSTGIS_USER"],
    password=os.environ["GEOPANDAS_POSTGIS_PASSWORD"],
    host=os.environ["GEOPANDAS_POSTGIS_HOST"],
    port=int(os.environ["GEOPANDAS_POSTGIS_PORT"]),
    database=os.environ["GEOPANDAS_POSTGIS_DATABASE"],
)
engine = create_engine(db_url)
```

Read only those named variables (or secret-manager equivalents). Never print
`db_url`, `engine.url`, exception payloads containing it, or the broader
environment.

Use parameterized values and trusted SQL identifiers:

```python
from sqlalchemy import text

query = text(
    "SELECT feature_id, geom FROM approved_schema.features "
    "WHERE category = :category"
)
gdf = geopandas.read_postgis(
    query,
    con=engine,
    geom_col="geom",
    params={"category": approved_category},
    chunksize=10_000,
)
```

`read_postgis` infers one CRS from the SRID of the first geometry and assigns it
to all rows unless `crs=` is supplied. Verify all geometries share the expected
SRID. With `chunksize`, it returns an iterator; validate every chunk and enforce
a total-row limit.

For writes:

```python
with engine.begin() as connection:
    gdf.to_postgis(
        "derived_features",
        con=connection,
        schema="approved_schema",
        if_exists="fail",
        index=False,
        chunksize=10_000,
    )
```

- Default to `if_exists="fail"`.
- `replace` drops an existing table and is destructive.
- Validate schema/table/geometry column names against an allowlist; do not
  interpolate user input.
- GeoPandas 1.1.2 fixed SQL injection through a geometry-column name; remain on
  a patched version and still validate identifiers.
- Use least-privilege database roles and a transaction.

## Fiona-to-pyogrio migration

GeoPandas 1.0 changed the default engine from Fiona to pyogrio. Differences
include:

- schema/metadata keywords and driver options;
- writing attribute-only tables;
- handling empty geometries and unsupported field types;
- datetime resolution/timezone behavior;
- append and encoding behavior;
- error/warning text and filter behavior.

Set `engine=` explicitly for reproducibility and test round-trips before
migration. Do not assume identical outputs merely because both engines use GDAL.

## Export verification and provenance

For every output:

1. choose a new local path and explicit format/driver/layer;
2. record source hashes, source layer, stack/native versions, CRS, precision,
   repair, and transformation choices;
3. record field names/types/nullability, geometry columns/types, stable ID,
   index policy, encoding, dimensions, and expected losses;
4. write, then reopen with an independent code path when feasible;
5. compare row count, stable-ID set, null/empty/invalid/type counts, CRS, bounds
   at protected precision, and representative attribute values;
6. hash the completed artifact and store the audit separately.

Use `scripts/vector_inventory.py` for redacted intake and
`scripts/export_plan.py` for a non-executing output contract.

## Sources (verified 2026-07-23)

- [GeoPandas reading and writing files](https://geopandas.org/en/stable/docs/user_guide/io.html).
- [geopandas.read_file](https://geopandas.org/en/stable/docs/reference/api/geopandas.read_file.html).
- [GeoDataFrame.to_file](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_file.html).
- [GeoDataFrame.to_parquet](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_parquet.html).
- [geopandas.read_parquet](https://geopandas.org/en/stable/docs/reference/api/geopandas.read_parquet.html).
- [geopandas.read_postgis](https://geopandas.org/en/stable/docs/reference/api/geopandas.read_postgis.html).
- [GeoDataFrame.to_postgis](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_postgis.html).
- [Fiona-to-pyogrio migration](https://geopandas.org/en/stable/docs/user_guide/fiona_to_pyogrio.html).
- [pyogrio introduction](https://pyogrio.readthedocs.io/en/stable/introduction.html).
- [pyogrio API](https://pyogrio.readthedocs.io/en/stable/api.html).
- [GeoParquet 1.1.0 specification](https://geoparquet.org/releases/v1.1.0/).
- [GeoArrow 0.2 specification](https://github.com/geoarrow/geoarrow).
- [GeoPandas 1.1.2 security/bug-fix release](https://github.com/geopandas/geopandas/releases/tag/v1.1.2) — released 2025-12-22.

### `references/data-structures.md`

# GeoPandas data structures

GeoPandas 1.1.4 extends pandas with a `geometry` extension dtype backed by
Shapely 2. A `GeoSeries` is one geometry-valued pandas Series; a `GeoDataFrame`
is a DataFrame with one active geometry column and may contain additional
geometry columns.

## Construction

Always assign CRS at construction when it is known from authoritative metadata.
Do not infer it from coordinate ranges.

```python
import geopandas as gpd
import pandas as pd
from shapely import Point, box

points = gpd.GeoSeries(
    [Point(0, 0), Point(1, 1), None],
    index=["feature-a", "feature-b", "feature-c"],
    crs="EPSG:3857",
    name="location",
)

gdf = gpd.GeoDataFrame(
    {
        "feature_id": ["feature-a", "feature-b"],
        "value": [10, 20],
        "geometry": [Point(0, 0), Point(1, 1)],
    },
    geometry="geometry",
    crs="EPSG:3857",
)

table = pd.DataFrame({"x": [0.0, 1.0], "y": [0.0, 1.0]})
from_xy = gpd.GeoDataFrame(
    table,
    geometry=gpd.points_from_xy(table["x"], table["y"]),
    crs="EPSG:3857",
)
```

`points_from_xy` interprets arguments as x then y. For geographic data, that is
normally longitude then latitude in the coordinate array, even though the
authority definition of EPSG:4326 advertises latitude-first axes.

## Active and additional geometry columns

Frame-level spatial methods act on one active geometry column:

```python
gdf["buffered"] = gdf.geometry.buffer(10)
gdf = gdf.set_geometry("buffered")

assert gdf.active_geometry_name == "buffered"
assert gdf.geometry.name == "buffered"

gdf = gdf.rename_geometry("analysis_geometry")
```

Important distinctions:

- `gdf.geometry` always returns the active geometry, not necessarily a column
  literally named `"geometry"`.
- `rename_geometry()` updates the active-column bookkeeping. A plain pandas
  `rename(columns=...)` must be followed by `set_geometry()`.
- A `GeoDataFrame` can hold multiple geometry columns with different CRS
  metadata. Switching the active column switches the CRS exposed as `gdf.crs`.
- Ordinary vector formats generally support only one geometry per layer.
  GeoParquet and Feather can preserve multiple geometry columns.
- GeoPandas 1.0 changed `set_geometry(named_series)`: the Series name becomes
  the active column name and the old geometry column is preserved. Avoid the
  deprecated `drop=` parameter; rename/drop explicitly.

Check every geometry column independently:

```python
geometry_columns = [
    name for name, dtype in gdf.dtypes.items() if str(dtype) == "geometry"
]
column_crs = {name: gdf[name].crs for name in geometry_columns}
```

## Missing, empty, and invalid are different

Treat these states separately:

| State | Test | Meaning |
|---|---|---|
| Missing | `series.isna()` | Unknown geometry, represented by `None` |
| Empty | `series.is_empty` | A geometry object with no coordinates |
| Invalid | `~series.is_valid` after excluding missing | Coordinates violate topology rules |

```python
missing = gdf.geometry.isna()
empty = gdf.geometry.is_empty
invalid = (~missing) & (~empty) & (~gdf.geometry.is_valid)
usable = ~(missing | empty | invalid)
```

Missing values generally propagate through element-wise operations and are
ignored by reductions such as `union_all()`. Empty geometries participate as
geometries: they may have area `0.0` and remain empty after intersection.
Never use only `dropna()` to remove unusable geometries.

## Index alignment

Binary geometry methods are **row-wise**, not all-pairs operations. With a
GeoSeries argument, `align=None` defaults to label alignment:

```python
left = gpd.GeoSeries([Point(0, 0), Point(1, 1)], index=["a", "b"])
right = gpd.GeoSeries([Point(1, 1), Point(0, 0)], index=["b", "a"])

by_label = left.intersects(right, align=True)
by_position = left.intersects(right, align=False)
```

Use `align=False` only after proving equal lengths and intended row order.
GeoPandas 1.0 raises on some unaligned pandas Series method arguments to avoid
ambiguous automatic alignment. For all-pairs matching use a spatial join or
spatial-index query.

Assignment also aligns by index:

```python
result = gdf.copy()
derived = result.geometry.buffer(10)
result.loc[:, "buffered"] = derived  # label-aligned
```

Reset or preserve indices deliberately before positional work. Never assume the
pandas index is a stable feature identifier.

## Feature identity and duplicate controls

Keep a non-null, stable feature-ID column across reads, joins, explode,
overlay, dissolve, and exports:

```python
ids = gdf["feature_id"]
if ids.isna().any() or ids.duplicated(keep=False).any():
    raise ValueError("feature_id must be non-null and unique for this workflow")
```

Cardinality-changing operations need explicit provenance:

- `explode(ignore_index=False, index_parts=False)` defaults to no part-level
  MultiIndex in GeoPandas 1.0+. Create a part number if parts need identity.
- Spatial joins can repeat either side; retain both source IDs.
- Overlay can split one feature into many. Add source IDs before overlay and
  generate a derived ID afterward.
- Dissolve intentionally combines IDs; record group keys and aggregation rules.
- `pd.concat` requires compatible geometry-column CRS and can preserve duplicate
  indices unless `ignore_index=True`.

## Geometry type and dimensionality

`geom_type`, `has_z`, and (with Shapely 2.1) `has_m` describe different
properties. Mixed geometry types are valid in memory but can break overlay or
export contracts. Z and M ordinates are not used by GeoPandas' planar topology:

```python
summary = {
    "types": gdf.geometry.geom_type.value_counts(dropna=False).to_dict(),
    "has_z": int(gdf.geometry.has_z.sum()),
    "has_m": int(gdf.geometry.has_m.sum()),
}
```

Do not silently drop Z/M. If a target format or operation is 2D-only, record the
loss and create a new derived artifact.

## Copying and conversion

- Use `gdf.copy()` before replacing an active geometry.
- Call `merge()` from the GeoDataFrame side; `plain_df.merge(gdf, ...)` can
  return a non-spatial DataFrame.
- Reading a non-spatial layer with `read_file()` returns a pandas DataFrame in
  GeoPandas 1.0+.
- `np.asarray(gdf.geometry)` or `gdf.geometry.to_numpy()` replaces removed
  access to `GeometryArray.data`.
- Do not serialize geometries with pickle for exchange. Use GeoPackage,
  GeoParquet, WKB, or WKT with an explicit CRS contract.

## Minimum structure audit

Record, without emitting coordinates or identifiers:

1. row and column counts;
2. active and additional geometry-column names;
3. CRS per geometry column;
4. counts of missing, empty, invalid, Z/M, and each geometry type;
5. index uniqueness and stable-ID null/duplicate counts;
6. source hash, parser/driver, package/native versions, and operation timestamp.

The bundled `scripts/vector_inventory.py` emits a redacted metadata inventory;
`scripts/geometry_validity_report.py` adds bounded geometry-state counts.

## Sources (verified 2026-07-23)

- [GeoPandas data structures](https://geopandas.org/en/stable/docs/user_guide/data_structures.html).
- [GeoSeries API](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoSeries.html).
- [GeoDataFrame API](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.html).
- [Missing and empty geometries](https://geopandas.org/en/stable/docs/user_guide/missing_empty.html).
- [GeoSeries.intersects alignment](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoSeries.intersects.html).
- [GeoPandas 1.0.0 release and migrations](https://github.com/geopandas/geopandas/releases/tag/v1.0.0) — released 2024-06-24.

### `references/geometric-operations.md`

# Geometric operations, validity, and precision

GeoPandas delegates geometry work to Shapely/GEOS. Operations are planar,
two-dimensional, and expressed in CRS coordinate units. Z/M ordinates may be
carried but are not part of topology.

## Preflight state

Count missing, empty, invalid, and mixed geometries separately before any
constructive or set operation:

```python
geometry = gdf.geometry
missing = geometry.isna()
empty = geometry.is_empty
invalid = (~missing) & (~empty) & (~geometry.is_valid)

state = {
    "rows": len(gdf),
    "missing": int(missing.sum()),
    "empty": int(empty.sum()),
    "invalid": int(invalid.sum()),
    "types": geometry.geom_type.value_counts(dropna=False).to_dict(),
}
```

`is_valid` concerns polygon/ring topology; points and lines are generally valid
unless malformed. `is_simple`, `is_ring`, and `minimum_clearance` answer
different questions.

### Redacted validity diagnostics

`is_valid_reason()` can include the coordinate of a defect, for example a
self-intersection. Precise coordinates can be sensitive. Aggregate only the
reason category before `[` and retain detailed diagnostics in a protected local
artifact:

```python
reason_category = (
    geometry[invalid]
    .is_valid_reason()
    .str.split("[", n=1)
    .str[0]
    .value_counts()
)
```

## Repair is a model change

GeoPandas 1.1 exposes Shapely 2.1 repair controls:

```python
repaired = geometry.make_valid(
    method="structure",
    keep_collapsed=True,
)
```

Methods:

- `linework` preserves every edge/vertex, nodes all rings, and reconstructs
  areas with even/odd parity. It can produce complex `GeometryCollection`
  output and requires `keep_collapsed=True`.
- `structure` repairs rings, merges shells, and subtracts holes. It assumes
  shell/hole categorization is meaningful, requires GEOS >=3.10, and can drop
  collapsed parts when `keep_collapsed=False`.

Repair can turn a polygon into a multipolygon, line, point, collection, or empty
geometry. Never replace source data in place. Create a new artifact and compare:

1. valid/invalid/null/empty counts;
2. geometry-type and dimensionality transitions;
3. component counts and collapsed outputs;
4. area/length changes in appropriate units;
5. stable feature IDs and row count;
6. downstream predicate/coverage behavior.

`overlay(make_valid=True)` also repairs invalid inputs, but that convenience can
hide type changes. Audit and repair explicitly for traceable work.

## Precision models

`set_precision(grid_size, mode=...)` rounds x/y to a grid in **CRS units**:

```python
snapped = geometry.set_precision(
    grid_size=0.01,
    mode="valid_output",
)
```

Shapely 2.1 modes:

- `valid_output` removes collapsed polygonal/linear elements and duplicate
  vertices while producing valid output;
- `pointwise` rounds independently, retains duplicate vertices, and may produce
  invalid output;
- `keep_collapsed` preserves collapsed linear elements but removes collapsed
  polygonal elements.

Consequences:

- features narrower/shorter than the grid may become empty;
- spikes and narrow sections can disappear or split polygons;
- duplicate vertices are normally removed;
- Z is not rounded;
- vertex/ring/order is canonicalized and must not be used as identity;
- inputs should be valid first;
- later operations use the higher precision (smaller grid size) of inputs.

Choose the grid from documented source resolution and error—not decimal
aesthetics. `0.001` degrees is not a universal metric tolerance.

For one union/dissolve, `grid_size=` can apply fixed precision without first
attaching a precision model:

```python
merged = geometry.union_all(method="unary", grid_size=0.01)
```

Record whether precision was attached to inputs or applied only to an operation.

## `union_all` algorithms

GeoPandas 1.1.4 signature:

```python
geometry.union_all(method="unary", grid_size=None)
```

- `unary`: robust general-purpose algorithm; the only method supporting
  `grid_size`.
- `coverage`: optimized for non-overlapping edge-matched polygon coverages; it
  can return invalid geometry if polygons overlap.
- `disjoint_subset`: optimized when input can be divided into non-intersecting
  subsets; requires Shapely >=2.1 and may be slower when there is one subset.

Do not use `coverage` based on visual inspection:

```python
if not geometry.is_valid_coverage(gap_width=0.0):
    edges = geometry.invalid_coverage_edges(gap_width=0.0)
    raise ValueError("Not an edge-matched non-overlapping coverage")

merged = geometry.union_all(method="coverage")
```

`is_valid_coverage()` ignores non-polygon geometry and requires Shapely >=2.1.
If narrow gaps matter, select `gap_width` in justified projected units.
`simplify_coverage()` preserves shared boundaries for a valid coverage; ordinary
element-wise `simplify()` does not.

The old `unary_union` attribute is deprecated. Use `union_all()`.

## Constructive operations

All distance/tolerance arguments are CRS units:

```python
buffered = geometry.buffer(50)
simplified = geometry.simplify(5, preserve_topology=True)
densified = geometry.segmentize(max_segment_length=10)
centroids = geometry.centroid
inside_points = geometry.representative_point()
```

Correctness notes:

- Buffering geographic degrees does not create a fixed-metre buffer.
- Negative polygon buffers can collapse to empty.
- `centroid` may fall outside a concave polygon; `representative_point()` is
  guaranteed within the geometry but is not a centroid.
- `preserve_topology=True` protects each geometry's validity, not shared
  boundaries between adjacent features.
- `segmentize()` inserts vertices along planar segments; it does not create
  geodesic densification.
- Affine rotate/scale/translate/skew operations are coordinate-space transforms,
  not CRS transformations.

## Binary predicates

Predicates implement DE-9IM relationships and are directional:

| Predicate | Practical meaning |
|---|---|
| `intersects` | Boundaries or interiors share any point |
| `disjoint` | Share no point |
| `within` | Left geometry lies in right interior/boundary under DE-9IM |
| `contains` | Inverse direction of `within`; boundary-only point is not contained |
| `covers` | No point of right lies outside left; includes boundary cases |
| `covered_by` | Inverse of `covers` |
| `contains_properly` | Contains with no common boundary points |
| `touches` | Interiors do not meet, boundaries do |
| `crosses` | Interiors meet with lower-dimensional result |
| `overlaps` | Same-dimensional partial overlap, neither contains the other |
| `dwithin` | Planar distance is within the supplied CRS-unit threshold |

Do not describe `contains`, `covers`, and `intersects` as interchangeable.
Boundary-point tests are an important synthetic fixture.

Binary GeoSeries calls are one-to-one and index-aligned by default:

```python
matched = left.intersects(right, align=True)
```

They do not answer whether each left geometry intersects *any* right geometry.
Use `sjoin` or the spatial index for all-pairs matching.

## Overlay robustness and slivers

Overlay and intersection can create tiny slivers from precision mismatch,
near-coincident edges, or distinct source accuracy:

1. validate inputs and CRS;
2. quantify source precision/accuracy;
3. select a justified grid if snapping is appropriate;
4. run overlay with explicit `keep_geom_type`;
5. validate output and count type changes;
6. summarize area distribution and very small parts in projected units;
7. compare area conservation appropriate to the selected overlay mode.

Do not delete polygons below an arbitrary area threshold. A small polygon can be
legitimate, and thresholding can bias boundaries. Record any sliver rule and
retain pre-cleaning output.

## Equality and identity

- `geom_equals` is topological equality; coordinate order may differ.
- `geom_equals_exact(tolerance=...)` checks structural coordinate equality
  within tolerance.
- `geom_equals_identical` exposes Shapely's identical comparison in GeoPandas
  1.1 and includes coordinate/order details.
- `normalize()` can canonicalize ordering for reproducible comparisons, but a
  normalized WKB hash is still geometry identity, not stable feature identity.

## Post-operation validation

For every geometry-changing operation, record:

- operation and all parameters;
- source/target CRS and units;
- package and GEOS versions;
- null/empty/invalid/type/component counts before and after;
- row expansion/contraction and stable-ID mapping;
- precision model, repair method, collapsed-part policy;
- area/length conservation checks where meaningful;
- a new output path and source/output hashes.

The bundled `scripts/geometry_validity_report.py` provides bounded dry-run
counts and optional new-file repair without emitting geometries or coordinates.

## Sources (verified 2026-07-23)

- [GeoPandas geometric manipulations](https://geopandas.org/en/stable/docs/user_guide/geometric_manipulations.html).
- [GeoSeries.make_valid](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoSeries.make_valid.html).
- [GeoSeries.union_all](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoSeries.union_all.html).
- [GeoSeries.is_valid_coverage](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoSeries.is_valid_coverage.html).
- [Shapely 2.1.2 make_valid](https://shapely.readthedocs.io/en/2.1.2/reference/shapely.make_valid.html).
- [Shapely 2.1.2 set_precision](https://shapely.readthedocs.io/en/2.1.2/reference/shapely.set_precision.html).
- [Shapely 2.1.2 union_all](https://shapely.readthedocs.io/en/2.1.2/reference/shapely.union_all.html).
- [GeoPandas 1.1.0 release](https://github.com/geopandas/geopandas/releases/tag/v1.1.0) — released 2025-06-01.

### `references/spatial-analysis.md`

# Spatial joins, overlay, clip, and dissolve

Spatial operations can multiply, split, or merge records. Define geometry
semantics and expected cardinality before running them, then audit both.

## Shared preflight

For each input:

1. preserve a non-null stable feature-ID column;
2. count duplicate IDs and duplicate pandas indices;
3. require CRS and reproject to a common, justified CRS;
4. count null, empty, invalid, mixed, and Z/M geometries;
5. validate precision/accuracy compatibility;
6. state whether boundary contact should count;
7. state the expected one-to-one, one-to-many, many-to-one, or many-to-many
   relationship.

GeoPandas operations are planar and ignore Z. Geographic longitude/latitude is
not suitable for distance/nearest work.

## Attribute joins

Call `merge` from the spatial object so geometry dtype and CRS are retained:

```python
result = zones.merge(
    attributes,
    on="zone_id",
    how="left",
    validate="one_to_one",
    indicator=True,
)
```

Use pandas `validate=` whenever the key contract is known. Before merging, audit
null/duplicate keys on both sides. Afterward, count `_merge` categories and
verify row count. A pandas index is not a feature key.

## Binary-predicate spatial joins

Stable GeoPandas 1.1.4 signature:

```python
joined = left.sjoin(
    right,
    how="inner",
    predicate="intersects",
    distance=None,
    on_attribute=None,
)
```

`predicate` is evaluated directionally from each left geometry against right
geometries. Query available values from
`left.sindex.valid_query_predicates`.

Common choices:

- point-in-polygon strict interior: points on polygon boundaries do not satisfy
  `within`;
- point in polygon including boundary: reverse the relation and use `covers`,
  or explicitly test the intended boundary behavior;
- any shared boundary/interior: `intersects`;
- boundary-only relationships: `touches`;
- distance threshold: `dwithin`.

`dwithin` requires `distance`. It may be a scalar or a one-dimensional array
with one value per **left row**; values are CRS units:

```python
joined = left.sjoin(
    right,
    predicate="dwithin",
    distance=500,
)
```

`on_attribute="category"` (or a list/tuple) adds equality on columns present in
both frames after the spatial predicate. It is a restriction, not a substitute
for checking nulls, normalization, and duplicates in the attribute.

### Geometry and index retention

- `how="left"` keeps left keys and only left geometry.
- `how="right"` keeps right keys and only right geometry.
- `how="inner"` keeps matching pairs and only left geometry.
- GeoPandas 1.0 preserves a named right index as that output column name;
  otherwise output often uses `index_right`. Do not hard-code that name as a
  permanent ID.

Every qualifying pair produces a row. One left feature intersecting three right
features yields three rows. Empty/null geometries do not produce predicate
matches.

### Cardinality audit

Add internal unique row numbers before joining; never expose user IDs in a
public report:

```python
left_work = left.reset_index(drop=True).assign(_left_row=lambda x: range(len(x)))
right_work = right.reset_index(drop=True).assign(_right_row=lambda x: range(len(x)))

pairs = left_work[["_left_row", left_work.geometry.name]].sjoin(
    right_work[["_right_row", right_work.geometry.name]],
    predicate="intersects",
    how="inner",
)

left_multiplicity = pairs.groupby("_left_row").size()
right_multiplicity = pairs.groupby("_right_row").size()
```

Report pair count, matched/unmatched counts on both sides, and counts with
multiple matches. Compare these to the declared contract. The bundled
`scripts/spatial_join_audit.py` implements this with redacted aggregate output.

## Nearest spatial joins

```python
nearest = left.sjoin_nearest(
    right,
    how="left",
    max_distance=1_000,
    distance_col="distance_crs_units",
    exclusive=False,
)
```

Key semantics:

- distance and `max_distance` use CRS units;
- geographic CRS results are inaccurate;
- `max_distance > 0` can substantially reduce work and limits accepted matches;
- all equidistant nearest or intersecting neighbors are returned, so one input
  can produce multiple rows;
- `exclusive=True` excludes geometrically equal nearest candidates;
- GeoPandas `sjoin_nearest` has no `k=` argument. For k-nearest behavior use a
  separately designed spatial-index/neighbor workflow and define tie handling.

Never silently keep the first tie. Report tie counts and specify a deterministic
domain rule if one result must be selected.

## Overlay

```python
result = left.overlay(
    right,
    how="intersection",
    keep_geom_type=False,
    make_valid=False,
)
```

Modes:

| `how` | Result |
|---|---|
| `intersection` | Areas/parts shared by both |
| `union` | All partitioned parts with attributes from either/both |
| `identity` | All left parts split by right |
| `difference` | Left minus right |
| `symmetric_difference` | Parts in exactly one input |

Constraints and choices:

- Each input must have a uniform supported family: (Multi)Polygon,
  (Multi)Point, or line/LinearRing family.
- Inputs need the same CRS.
- `make_valid=True` repairs invalid inputs and may change types; pre-audit repair
  is more traceable. With `False`, invalid inputs raise.
- `keep_geom_type=None` behaves as `True` and warns when dropping other result
  types. Set it explicitly and count dropped/type-changed results.
- Union-like modes place `NaN` in attributes absent from one side.
- Near-coincident boundaries and precision mismatch produce slivers. Use a
  justified precision model, quantify small parts, and validate area balance.

Always keep source IDs from both inputs. Overlay can split one source feature
into many derived records.

## Clip

```python
clipped = gpd.clip(
    features,
    mask,
    keep_geom_type=False,
    sort=False,
)
```

- Both layers must share CRS.
- Multiple mask geometries are dissolved before intersection, so mask
  attributes are not transferred.
- A four-number `(minx, miny, maxx, maxy)` mask activates a fast rectangle
  path. It is possibly dirty, does not guarantee valid output, and can omit a
  line that collapses to a point.
- `keep_geom_type=False` retains mixed-dimensional outputs; set deliberately.
- `sort=False` does not promise source order. Preserve IDs and sort explicitly
  if order is part of the contract.

Validate clip output. Use overlay intersection when mask attributes or more
auditable topology are required.

## Dissolve

`dissolve` performs `groupby.agg` on attributes and `union_all` on geometry:

```python
dissolved = parcels.dissolve(
    by="region_id",
    aggfunc={
        "population": "sum",
        "source_date": "max",
    },
    as_index=False,
    dropna=False,
    method="unary",
    grid_size=0.01,
)
```

Avoid the default `aggfunc="first"` for meaningful attributes. Specify every
aggregation and its units. Decide whether null group keys should be dropped
(`dropna=True`) or retained as a group (`False`).

Union methods:

- `unary`: robust general default; supports `grid_size`;
- `coverage`: fast only for proven non-overlapping, edge-matched polygons and
  may produce invalid output otherwise;
- `disjoint_subset`: Shapely >=2.1, useful for disjoint partitions.

For coverage mode, run `is_valid_coverage()` first. After dissolve, compare
group counts, summed attributes, validity, empty output, and area in a suitable
projected CRS.

## Spatial index

GeoPandas uses Shapely's spatial index automatically for joins, clip, and
overlay. Direct queries are candidate/predicate operations:

```python
predicate_names = gdf.sindex.valid_query_predicates
indices = gdf.sindex.query(query_geometry, predicate="intersects")
```

GeoPandas 1.0 removed `sindex.query_bulk`; use `query`. GeoPandas 1.1 supports
indices, dense boolean, and optional SciPy sparse boolean output formats. Do not
assume the shape/orientation of an undocumented output; set `output_format`
explicitly and test.

Spatial indexing does not fix CRS, invalid geometry, distance units, predicate
direction, or cardinality.

## Area and distance checks

For planar metrics:

```python
if gdf.crs is None or gdf.crs.is_geographic:
    raise ValueError("Use a justified projected CRS")

area = gdf.geometry.area
length = gdf.geometry.length
distance = gdf.geometry.distance(reference_geometry)
```

Confirm axis unit and conversion factor before labeling values. For
large/global or cross-zone work, use a geodesic design instead.

## Provenance checklist

Record:

- source hashes, layer names, stable IDs, input row/state counts;
- source and operation CRS, units, and transform pipeline;
- predicate direction, boundary semantics, distance/max-distance;
- join type, attribute restrictions, expected and observed cardinality;
- validity repair, precision grid, overlay/union method;
- mask dissolve/rectangle choice, dissolve aggregations;
- output row/type/state counts and new artifact hash.

## Sources (verified 2026-07-23)

- [GeoPandas merging data guide](https://geopandas.org/en/stable/docs/user_guide/mergingdata.html).
- [geopandas.sjoin](https://geopandas.org/en/stable/docs/reference/api/geopandas.sjoin.html).
- [geopandas.sjoin_nearest](https://geopandas.org/en/stable/docs/reference/api/geopandas.sjoin_nearest.html).
- [geopandas.overlay](https://geopandas.org/en/stable/docs/reference/api/geopandas.overlay.html).
- [geopandas.clip](https://geopandas.org/en/stable/docs/reference/api/geopandas.clip.html).
- [GeoDataFrame.dissolve](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.dissolve.html).
- [GeoPandas set operations guide](https://geopandas.org/en/stable/docs/user_guide/set_operations.html).
- [GeoPandas aggregation with dissolve](https://geopandas.org/en/stable/docs/user_guide/aggregation_with_dissolve.html).

### `references/visualization.md`

# Static and interactive visualization

A map is a derived analytical artifact. It can misstate units, hide missing
data, expose exact locations, or contact third-party services even when the
underlying geometry operations are correct.

## Privacy gate

Before plotting:

1. classify coordinates, addresses, trajectories, parcels, facilities, and
   small-area attributes for sensitivity;
2. decide whether the audience needs exact geometry;
3. aggregate, suppress small groups, jitter only with a defensible privacy
   model, or generalize at an appropriate scale;
4. remove direct identifiers and sensitive tooltip/popup fields;
5. inspect the output itself—HTML, SVG, PDF, and GeoJSON can preserve exact
   coordinates or attributes even when the image looks coarse.

The bundled `scripts/sensitive_coordinates_checklist.py` provides a conservative
release gate. It does not claim legal or privacy compliance.

## Static plotting

GeoPandas `.plot()` uses Matplotlib:

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(8, 6))
gdf.plot(
    ax=ax,
    column="rate",
    cmap="viridis",
    legend=True,
    missing_kwds={
        "color": "lightgrey",
        "edgecolor": "black",
        "hatch": "///",
        "label": "Missing",
    },
)
ax.set_title("Synthetic rate by region")
ax.set_axis_off()
fig.savefig("derived/map.png", dpi=300, bbox_inches="tight")
```

Pin Matplotlib and optional mapping dependencies in the project lock. The
GeoPandas 1.1 tagged source tests Matplotlib >=3.7 and mapclassify >=2.5.

### Choropleth correctness

State in the title/caption or metadata:

- variable definition, units, date, and source;
- whether values are counts, rates, densities, or percentages;
- normalization denominator and treatment of zero/missing denominators;
- classification method, number of bins, and explicit boundaries;
- color-map direction and meaning;
- missing/suppressed/out-of-scope styling;
- CRS/projection and any geographic generalization.

Raw counts over unequal polygon areas often communicate population size rather
than rate. Compute an appropriate rate/density first and retain numerator and
denominator.

`scheme=` delegates classification to mapclassify:

```python
ax = gdf.plot(
    column="rate",
    scheme="quantiles",
    k=5,
    cmap="viridis",
    legend=True,
)
```

Quantiles balance feature counts but can place almost equal values in different
bins. Equal intervals can leave sparse bins; natural breaks are data-dependent
and make cross-map comparisons difficult. For comparisons, reuse explicit
boundaries and a common normalization.

### Missing data

GeoPandas ignores missing values by default. That can make missing areas look
like background or water. Always count missing values and use `missing_kwds`
when they are meaningful. Distinguish:

- missing attribute;
- missing geometry;
- empty geometry;
- suppressed value;
- zero;
- outside the study area.

Do not coerce missing values to zero for visual convenience.

### Categorical maps

Use `categorical=True` for categories and a qualitative palette. Verify category
order and legend labels; do not imply magnitude with a sequential palette.
GeoPandas 1.1.4 fixed custom categorical/boolean `legend_kwds={"labels": ...}`
being ignored by `explore()`.

### Layering

```python
fig, ax = plt.subplots(figsize=(8, 6))
areas.plot(ax=ax, facecolor="none", edgecolor="0.4", zorder=1)
generalized_points.plot(ax=ax, color="black", markersize=8, zorder=2)
```

- Reproject every layer to a common CRS.
- Use `facecolor="none"` for transparent polygon faces; Python `None` means
  something different.
- Choose `zorder`, alpha, and line width deliberately.
- Confirm no layer is hidden by a filled polygon.
- Keep a stable visual scale when comparing panels.

## Projection and extent

Choose a map projection for the communication goal:

- equal-area for area comparisons;
- local conformal for local shape/angles;
- Web Mercator only when required by a web tile system;
- a suitable global projection for world views.

GeoPandas may set a latitude-dependent aspect for geographic plots, but that is
not a replacement for a chosen projection. Exact metric scale bars require a
projected CRS with known linear units and limited distortion.

Antimeridian-crossing geometries must be split/wrapped before plotting; changing
axis limits does not repair a line drawn across the map.

## Basemaps are network and licensing dependencies

Tile helpers such as contextily and `explore(tiles=...)` can send viewport,
zoom, IP, and timing information to a provider and can disclose the study area.
They also introduce attribution, terms-of-use, caching, availability, and
reproducibility requirements.

Do not fetch tiles automatically. If a user explicitly approves a provider:

- verify its official URL, license, attribution, and usage limits;
- generalize sensitive overlays before the request;
- record provider, style, retrieval date, zoom, and tile hashes/cache;
- do not put credentials in source or generated HTML;
- use a vetted cache for reproducible/offline output where permitted.

## Interactive `explore`

`GeoDataFrame.explore()` returns a `folium.Map`. Background tiles require CRS
metadata and normally cause network requests. Start with a no-tile,
no-attribute local draft:

```python
interactive = generalized_gdf.explore(
    tiles=None,
    tooltip=False,
    popup=False,
    style_kwds={"fillOpacity": 0.5, "weight": 1},
)
interactive.save("derived/local-draft.html")
```

Even `tiles=None` HTML can reference CDN-hosted JavaScript/CSS depending on the
Folium configuration. Inspect the generated HTML and use an approved offline
asset strategy before sensitive or air-gapped use.

Privacy hazards:

- `popup=True` can expose all columns;
- tooltip lists can expose addresses or unique IDs;
- coordinates are embedded in the HTML/GeoJSON;
- layer names and filenames can disclose project context;
- user-added tile URLs can leak tokens and viewport;
- sharing the HTML shares data, not just a screenshot.

For multiple layers, add only generalized/allowlisted columns and explicit
names. Do not use the interactive map as a data-access control boundary.

## Geometry and plotting edge cases

- Empty/missing geometries are not visible; report their counts.
- Invalid polygons can render inconsistently; validate first.
- Mixed geometry types need explicit styles per type.
- Polygon holes and ring orientation should be checked after repair/export.
- Z/M are ignored by 2D plotting.
- Marker size is in display units, not map units, unless explicitly transformed.
- Alpha blending can create misleading dark areas from duplicated/overlapping
  features; audit duplicate geometry and join multiplication.
- Tiny overlay slivers can dominate outlines; fix/audit topology rather than
  merely hiding them.

## Accessibility and honest design

- Prefer perceptually uniform, color-vision-aware palettes.
- Include text labels/patterns when color alone is insufficient.
- Keep legend order, labels, precision, and units consistent with the data.
- Avoid rainbow palettes and excessive classes.
- Use adequate contrast and minimum line/marker sizes.
- Include alt text/caption summarizing the main pattern and missing/suppressed
  data.
- Do not imply uncertainty-free precision; display uncertainty or caveats.

## Reproducible output

Record:

- source/output hashes and privacy/generalization decision;
- package versions, CRS, projection, extent, and antimeridian handling;
- plotted column, normalization, classification/bins, palette, missing style;
- layer order and styling;
- figure size, DPI, and format;
- tile provider/license/retrieval metadata or explicit `tiles=None`;
- tooltip/popup allowlist and HTML external-resource audit.

Raster PNG reduces direct coordinate extraction compared with SVG/HTML but is
not anonymization. Check metadata and visual landmarks before release.

## Sources (verified 2026-07-23)

- [GeoPandas mapping and plotting guide](https://geopandas.org/en/stable/docs/user_guide/mapping.html).
- [GeoPandas interactive mapping guide](https://geopandas.org/en/stable/docs/user_guide/interactive_mapping.html).
- [GeoDataFrame.plot API](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.plot.html).
- [GeoDataFrame.explore API](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.explore.html).
- [GeoPandas 1.1.4 release notes](https://github.com/geopandas/geopandas/releases/tag/v1.1.4) — released 2026-06-26.
- [GeoPandas 1.1.0 release notes](https://github.com/geopandas/geopandas/releases/tag/v1.1.0) — plotting and dependency changes.

### `scripts/_common.py`

```python
"""Shared local-only safety and reporting helpers for GeoPandas CLIs."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import tempfile
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

PINNED_STACK = {
    "geopandas": "1.1.4",
    "numpy": "2.5.1",
    "packaging": "26.2",
    "pandas": "3.0.5",
    "pyarrow": "25.0.0",
    "pyogrio": "0.13.0",
    "pyproj": "3.7.2",
    "shapely": "2.1.2",
}
DEFAULT_MAX_INPUT_BYTES = 64 * 1024 * 1024
DEFAULT_MAX_OUTPUT_BYTES = 256 * 1024 * 1024
DEFAULT_MAX_FEATURES = 100_000
ABSOLUTE_MAX_INPUT_BYTES = 512 * 1024 * 1024
ABSOLUTE_MAX_OUTPUT_BYTES = 1024 * 1024 * 1024
ABSOLUTE_MAX_FEATURES = 1_000_000
GDAL_SUFFIXES = {".fgb", ".geojson", ".gpkg", ".json", ".shp"}
PARQUET_SUFFIXES = {".geoparquet", ".parquet"}
FEATHER_SUFFIXES = {".arrow", ".feather"}
ALLOWED_INPUT_SUFFIXES = GDAL_SUFFIXES | PARQUET_SUFFIXES | FEATHER_SUFFIXES
ARCHIVE_SUFFIXES = {
    ".7z",
    ".bz2",
    ".gz",
    ".kmz",
    ".rar",
    ".tar",
    ".tgz",
    ".xz",
    ".zip",
}
SENSITIVE_FIELD_TOKENS = {
    "address",
    "coordinate",
    "email",
    "latitude",
    "location",
    "longitude",
    "parcel",
    "phone",
    "postcode",
    "trajectory",
    "zipcode",
}


class CliError(ValueError):
    """A bounded, user-facing CLI error."""


def positive_int(value: str) -> int:
    """Argparse converter for positive integers."""
    try:
        number = int(value)
    except ValueError as exc:
        raise ValueError("must be an integer") from exc
    if number < 1:
        raise ValueError("must be at least 1")
    return number


def bounded_limit(value: int, *, name: str, maximum: int) -> int:
    """Validate a positive resource limit against a hard ceiling."""
    if value < 1:
        raise CliError(f"{name} must be at least 1")
    if value > maximum:
        raise CliError(f"{name} may not exceed {maximum}")
    return value


def finite_number(value: Any, *, name: str) -> float:
    """Return one finite floating-point value."""
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise CliError(f"{name} must be a finite number") from exc
    if not math.isfinite(number):
        raise CliError(f"{name} must be finite")
    return number


def reject_nonlocal(value: str, *, label: str) -> None:
    """Reject URLs, GDAL virtual filesystems, archives, and path tricks."""
    lowered = value.casefold().strip()
    if not lowered or "\x00" in value:
        raise CliError(f"{label} is empty or invalid")
    if "://" in lowered or lowered.startswith(("/vsi", "vsi")):
        raise CliError(f"{label} must be a local path, not a URL or GDAL VSI path")
    if "!" in value or lowered.startswith(("zip+", "tar+")):
        raise CliError(f"{label} may not address an archive member")
    suffixes = {suffix.casefold() for suffix in Path(lowered).suffixes}
    if suffixes & ARCHIVE_SUFFIXES:
        raise CliError(f"{label} may not be an archive or compressed file")


def _root_path(value: str | Path) -> Path:
    raw = str(value)
    reject_nonlocal(raw, label="root")
    candidate = Path(raw).expanduser()
    if candidate.is_symlink():
        raise CliError("root may not be a symbolic link")
    try:
        root = candidate.resolve(strict=True)
    except OSError as exc:
        raise CliError("root does not exist or cannot be resolved") from exc
    if not root.is_dir():
        raise CliError("root must be a directory")
    return root


def _reject_symlink_components(candidate: Path, root: Path) -> None:
    current = candidate
    while True:
        if current.is_symlink():
            raise CliError("symbolic-link paths are not accepted")
        if current == root:
            return
        parent = current.parent
        if parent == current:
            raise CliError("path escapes the configured root")
        current = parent


def _candidate_path(value: str | Path, root: Path, *, label: str) -> Path:
    raw = str(value)
    reject_nonlocal(raw, label=label)
    supplied = Path(raw).expanduser()
    if ".." in supplied.parts:
        raise CliError(f"{label} may not contain '..'")
    candidate = supplied if supplied.is_absolute() else root / supplied
    resolved = candidate.resolve(strict=False)
    if not resolved.is_relative_to(root):
        raise CliError(f"{label} must remain inside the configured root")
    _reject_symlink_components(candidate, root)
    return candidate


def checked_input_file(
    value: str | Path,
    *,
    root: str | Path = ".",
    max_bytes: int = DEFAULT_MAX_INPUT_BYTES,
    allowed_suffixes: set[str] | None = None,
) -> Path:
    """Resolve one bounded, allowlisted local regular input file."""
    max_bytes = bounded_limit(
        max_bytes,
        name="max_input_bytes",
        maximum=ABSOLUTE_MAX_INPUT_BYTES,
    )
    resolved_root = _root_path(root)
    candidate = _candidate_path(value, resolved_root, label="input")
    try:
        path = candidate.resolve(strict=True)
    except OSError as exc:
        raise CliError("input does not exist or cannot be resolved") from exc
    if not path.is_file():
        raise CliError("input must be a regular file")
    suffixes = allowed_suffixes or ALLOWED_INPUT_SUFFIXES
    if path.suffix.casefold() not in suffixes:
        raise CliError("input suffix is not on the vector-data allowlist")
    size = path.stat().st_size
    if size > max_bytes:
        raise CliError(f"input exceeds the {max_bytes}-byte limit")
    return path


def checked_output_file(
    value: str | Path,
    *,
    root: str | Path = ".",
    allowed_suffixes: set[str],
) -> Path:
    """Resolve a new local output path without creating or overwriting it."""
    resolved_root = _root_path(root)
    candidate = _candidate_path(value, resolved_root, label="output")
    if candidate.suffix.casefold() not in allowed_suffixes:
        raise CliError("output suffix is not allowed for this operation")
    if candidate.exists() or candidate.is_symlink():
        raise CliError("output already exists; choose a new path")
    parent = candidate.parent
    if parent.is_symlink() or not parent.exists() or not parent.is_dir():
        raise CliError("output parent must be an existing non-symlink directory")
    return candidate.resolve(strict=False)


def sha256_file(path: Path) -> str:
    """Hash a bounded local file without loading it into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def package_versions() -> dict[str, str | None]:
    """Return distribution versions without importing optional packages."""
    found: dict[str, str | None] = {}
    for name in PINNED_STACK:
        try:
            found[name] = version(name)
        except PackageNotFoundError:
            found[name] = None
    return found


def native_versions() -> dict[str, str | None]:
    """Return native-library versions after callers have accepted the boundary."""
    try:
        import pyogrio
        import pyproj
        import shapely
    except ImportError as exc:
        raise CliError(
            "runtime analysis requires the pinned GeoPandas stack from SKILL.md"
        ) from exc
    gdal_geos = getattr(pyogrio, "__gdal_geos_version__", None)
    return {
        "gdal": ".".join(str(part) for part in pyogrio.__gdal_version__),
        "gdal_geos": (
            ".".join(str(part) for part in gdal_geos) if gdal_geos else None
        ),
        "geos": str(shapely.geos_version_string),
        "proj": str(pyproj.proj_version_str),
    }


def disable_proj_network() -> None:
    """Disable PROJ network access for this process."""
    try:
        from pyproj import network
    except ImportError as exc:
        raise CliError("pyproj is required for CRS analysis") from exc
    network.set_network_enabled(False)


def crs_summary(value: Any) -> dict[str, Any]:
    """Summarize CRS semantics without serializing sensitive data extents."""
    try:
        from pyproj import CRS
    except ImportError as exc:
        raise CliError("pyproj is required for CRS analysis") from exc
    if value is None:
        return {
            "present": False,
            "authority": None,
            "geographic": None,
            "projected": None,
            "axes": [],
        }
    try:
        crs = CRS.from_user_input(value)
    except (TypeError, ValueError) as exc:
        raise CliError("CRS metadata cannot be parsed") from exc
    authority = crs.to_authority()
    axes = []
    for axis in crs.axis_info:
        factor = axis.unit_conversion_factor
        axes.append(
            {
                "abbreviation": axis.abbrev,
                "direction": axis.direction,
                "unit": axis.unit_name,
                "unit_to_si": float(factor) if factor is not None else None,
            }
        )
    return {
        "present": True,
        "authority": f"{authority[0]}:{authority[1]}" if authority else None,
        "geographic": bool(crs.is_geographic),
        "projected": bool(crs.is_projected),
        "axes": axes,
    }


def _json_scalar(value: Any) -> Any:
    """Convert common array scalars to strict JSON values."""
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if hasattr(value, "item"):
        return _json_scalar(value.item())
    return str(value)


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CliError(f"duplicate JSON metadata key: {key!r}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise CliError(f"non-finite JSON metadata value is not allowed: {value}")


def inspect_geoparquet(path: Path) -> dict[str, Any]:
    """Inspect Parquet metadata without reading feature coordinates."""
    try:
        from pyarrow import parquet
    except ImportError as exc:
        raise CliError("PyArrow is required to inventory GeoParquet") from exc
    try:
        parquet_file = parquet.ParquetFile(path)
    except (OSError, ValueError) as exc:
        raise CliError("PyArrow could not read Parquet metadata") from exc
    file_metadata = parquet_file.metadata
    key_values = file_metadata.metadata or {}
    raw_geo = key_values.get(b"geo")
    geo: dict[str, Any] | None = None
    if raw_geo is not None:
        try:
            decoded = raw_geo.decode("utf-8")
            parsed = json.loads(
                decoded,
                object_pairs_hook=_strict_object,
                parse_constant=_reject_constant,
            )
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CliError("GeoParquet geo metadata is invalid JSON") from exc
        if not isinstance(parsed, dict):
            raise CliError("GeoParquet geo metadata must be an object")
        geo = parsed
    columns = geo.get("columns", {}) if geo else {}
    if columns is not None and not isinstance(columns, dict):
        raise CliError("GeoParquet columns metadata must be an object")
    crs_states = {"missing": 0, "null": 0, "present": 0}
    covering_columns = 0
    geometry_types: dict[str, int] = {}
    for metadata in (columns or {}).values():
        if not isinstance(metadata, dict):
            raise CliError("GeoParquet geometry column metadata must be an object")
        if "crs" not in metadata:
            crs_states["missing"] += 1
        elif metadata["crs"] is None:
            crs_states["null"] += 1
        else:
            crs_states["present"] += 1
        if metadata.get("covering") is not None:
            covering_columns += 1
        for geometry_type in metadata.get("geometry_types", []):
            key = str(geometry_type)
            geometry_types[key] = geometry_types.get(key, 0) + 1
    arrow_types: dict[str, int] = {}
    for field in parquet_file.schema_arrow:
        key = str(field.type)
        arrow_types[key] = arrow_types.get(key, 0) + 1
    return {
        "kind": "geoparquet" if geo else "parquet_without_geo_metadata",
        "declared_features": int(file_metadata.num_rows),
        "row_groups": int(file_metadata.num_row_groups),
        "field_count": len(parquet_file.schema_arrow),
        "field_type_counts": dict(sorted(arrow_types.items())),
        "geometry_column_count": len(columns or {}),
        "primary_geometry_declared": bool(geo and geo.get("primary_column")),
        "schema_version": _json_scalar(geo.get("version")) if geo else None,
        "crs_metadata_states": crs_states,
        "geometry_type_metadata_counts": dict(sorted(geometry_types.items())),
        "covering_geometry_columns": covering_columns,
        "bounds_redacted": True,
        "feature_data_loaded": False,
    }


def inspect_gdal_vector(path: Path, *, layer: str | None = None) -> dict[str, Any]:
    """Inspect one GDAL vector layer without reading feature coordinates."""
    try:
        import pyogrio
    except ImportError as exc:
        raise CliError("pyogrio is required to inventory this vector format") from exc
    try:
        layers = pyogrio.list_layers(path)
    except (OSError, RuntimeError, ValueError) as exc:
        raise CliError("GDAL could not enumerate local vector layers") from exc
    layer_count = len(layers)
    if layer_count > 1 and layer is None:
        raise CliError("multi-layer input requires an explicit --layer")
    try:
        info = pyogrio.read_info(
            path,
            layer=layer,
            force_feature_count=False,
            force_total_bounds=False,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        raise CliError("GDAL could not inspect the selected local layer") from exc
    fields = [str(item) for item in info.get("fields", [])]
    dtypes: dict[str, int] = {}
    for dtype in info.get("dtypes", []):
        key = str(dtype)
        dtypes[key] = dtypes.get(key, 0) + 1
    sensitive_names = 0
    for field in fields:
        normalized = re.sub(r"[^a-z0-9]+", "_", field.casefold())
        if any(token in normalized for token in SENSITIVE_FIELD_TOKENS):
            sensitive_names += 1
    declared = info.get("features", -1)
    try:
        declared_features = int(declared)
    except (TypeError, ValueError):
        declared_features = -1
    return {
        "kind": "gdal_vector",
        "driver": _json_scalar(info.get("driver")),
        "layer_count": layer_count,
        "layer_explicitly_selected": layer is not None,
        "declared_features": declared_features if declared_features >= 0 else None,
        "field_count": len(fields),
        "field_type_counts": dict(sorted(dtypes.items())),
        "sensitive_field_name_count": sensitive_names,
        "geometry_type": _json_scalar(info.get("geometry_type")),
        "encoding": _json_scalar(info.get("encoding")),
        "crs": crs_summary(info.get("crs")),
        "bounds_available": info.get("total_bounds") is not None,
        "bounds_redacted": True,
        "feature_data_loaded": False,
    }


def inspect_local_vector(path: Path, *, layer: str | None = None) -> dict[str, Any]:
    """Dispatch to a metadata-only local vector inventory."""
    suffix = path.suffix.casefold()
    if suffix in PARQUET_SUFFIXES:
        if layer is not None:
            raise CliError("--layer is not valid for GeoParquet")
        return inspect_geoparquet(path)
    if suffix in FEATHER_SUFFIXES:
        raise CliError("Feather/Arrow inventory is not implemented; convert a vetted copy")
    return inspect_gdal_vector(path, layer=layer)


def load_geodataframe(
    path: Path,
    *,
    layer: str | None,
    max_features: int,
) -> Any:
    """Load at most max_features local geometries from an allowlisted format."""
    max_features = bounded_limit(
        max_features,
        name="max_features",
        maximum=ABSOLUTE_MAX_FEATURES,
    )
    if path.suffix.casefold() not in GDAL_SUFFIXES:
        raise CliError("this analysis accepts only allowlisted GDAL vector files")
    try:
        import geopandas as gpd
    except ImportError as exc:
        raise CliError("GeoPandas is required for geometry analysis") from exc
    info = inspect_gdal_vector(path, layer=layer)
    declared = info["declared_features"]
    if declared is not None and declared > max_features:
        raise CliError(f"input declares more than {max_features} features")
    try:
        frame = gpd.read_file(
            path,
            layer=layer,
            engine="pyogrio",
            rows=slice(0, max_features + 1),
            use_arrow=True,
        )
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        raise CliError("GeoPandas could not read the bounded local layer") from exc
    if not isinstance(frame, gpd.GeoDataFrame):
        raise CliError("selected layer has no geometry column")
    if len(frame) > max_features:
        raise CliError(f"input exceeds the {max_features}-feature limit")
    return frame


def geometry_state(frame: Any) -> dict[str, Any]:
    """Return aggregate geometry state without values, IDs, or coordinates."""
    geometry = frame.geometry
    missing = geometry.isna()
    empty = geometry.is_empty
    invalid = (~missing) & (~empty) & (~geometry.is_valid)
    type_counts: dict[str, int] = {}
    for value in geometry.geom_type:
        key = "missing" if value is None else str(value)
        type_counts[key] = type_counts.get(key, 0) + 1
    reason_counts: dict[str, int] = {}
    if bool(invalid.any()):
        for reason in geometry[invalid].is_valid_reason():
            category = str(reason).split("[", 1)[0].strip()[:120]
            reason_counts[category] = reason_counts.get(category, 0) + 1
    has_m = getattr(geometry, "has_m", None)
    return {
        "features": len(frame),
        "missing": int(missing.sum()),
        "empty": int(empty.sum()),
        "invalid": int(invalid.sum()),
        "valid_nonempty": int((~missing & ~empty & ~invalid).sum()),
        "geometry_type_counts": dict(sorted(type_counts.items())),
        "validity_reason_categories": dict(sorted(reason_counts.items())),
        "has_z": int(geometry.has_z.fillna(False).sum()),
        "has_m": int(has_m.fillna(False).sum()) if has_m is not None else None,
        "duplicate_index_rows": int(frame.index.duplicated(keep=False).sum()),
        "coordinates_emitted": False,
        "identifiers_emitted": False,
    }


def duplicate_column_state(frame: Any, name: str | None) -> dict[str, Any]:
    """Report null/duplicate counts for an optional ID without emitting values."""
    if name is None:
        return {"provided": False, "null_rows": None, "duplicate_rows": None}
    if name not in frame.columns:
        raise CliError("requested ID column is not present")
    values = frame[name]
    return {
        "provided": True,
        "null_rows": int(values.isna().sum()),
        "duplicate_rows": int(values.duplicated(keep=False).sum()),
    }


def write_new_geopackage(
    frame: Any,
    destination: Path,
    *,
    max_output_bytes: int = DEFAULT_MAX_OUTPUT_BYTES,
) -> None:
    """Write a single-layer GeoPackage and link it atomically to a new path."""
    max_output_bytes = bounded_limit(
        max_output_bytes,
        name="max_output_bytes",
        maximum=ABSOLUTE_MAX_OUTPUT_BYTES,
    )
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=".geopandas-repair-",
        suffix=".gpkg",
        dir=destination.parent,
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        temporary.unlink()
        frame.to_file(
            temporary,
            layer="repaired",
            driver="GPKG",
            engine="pyogrio",
            index=False,
            use_arrow=True,
        )
        if temporary.stat().st_size > max_output_bytes:
            raise CliError(f"derived output exceeds the {max_output_bytes}-byte limit")
        try:
            os.link(temporary, destination)
        except FileExistsError as exc:
            raise CliError("output appeared concurrently; nothing was overwritten") from exc
    finally:
        temporary.unlink(missing_ok=True)


def json_text(payload: Any) -> str:
    """Serialize strict, deterministic JSON."""
    return json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )


def emit_json(payload: Any) -> None:
    """Print a strict JSON report."""
    print(json_text(payload))


def fail_json(tool: str, exc: BaseException) -> int:
    """Emit a redacted error and return the CLI usage/data error status."""
    if isinstance(exc, CliError):
        message = str(exc)
    else:
        message = f"{type(exc).__name__}: operation failed; details redacted"
    emit_json(
        {
            "ok": False,
            "tool": tool,
            "error": message[:500],
            "network_accessed": False,
            "coordinates_emitted": False,
            "identifiers_emitted": False,
        }
    )
    return 2
```

### `scripts/crs_reprojection_plan.py`

```python
#!/usr/bin/env python3
"""Plan CRS and datum transformation semantics without transforming coordinates."""

from __future__ import annotations

import argparse
import sys
from typing import Any

from _common import (
    CliError,
    crs_summary,
    disable_proj_network,
    emit_json,
    fail_json,
    finite_number,
    native_versions,
    package_versions,
)

TOOL = "crs_reprojection_plan"
METRIC_OPERATIONS = {"area", "buffer", "distance", "nearest", "precision"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect CRS axes, units, datum-operation candidates, grid availability, "
            "and antimeridian risk without reading data or transforming coordinates."
        ),
        epilog=(
            "PROJ network access is forcibly disabled. Optional bbox values are used "
            "only as a protected area-of-interest hint and are never emitted."
        ),
    )
    parser.add_argument("--source-crs", required=True, help="Authoritative source CRS")
    parser.add_argument("--target-crs", required=True, help="Proposed target CRS")
    parser.add_argument(
        "--operation",
        choices=(
            "reproject",
            "area",
            "buffer",
            "distance",
            "nearest",
            "precision",
            "display",
        ),
        default="reproject",
        help="Purpose used for unit-readiness checks (default: reproject)",
    )
    parser.add_argument(
        "--bbox",
        nargs=4,
        metavar=("WEST_X", "SOUTH_Y", "EAST_X", "NORTH_Y"),
        help=(
            "Optional source-CRS bbox/area-of-interest. For geographic x/y input, "
            "east < west marks an antimeridian crossing. Values are not emitted."
        ),
    )
    parser.add_argument(
        "--allow-ballpark",
        action="store_true",
        help="Include ballpark candidates in this plan (not recommended for accuracy work)",
    )
    return parser


def _dynamic(crs: Any) -> bool:
    datum = getattr(crs, "datum", None)
    type_name = str(getattr(datum, "type_name", "")).casefold()
    return "dynamic" in type_name


def _candidate_summary(transformer: Any) -> dict[str, Any]:
    accuracy = float(transformer.accuracy)
    area = transformer.area_of_use
    return {
        "description": str(transformer.description)[:300],
        "accuracy_metres": accuracy if accuracy >= 0 else None,
        "accuracy_known": accuracy >= 0,
        "area_of_use_name": str(area.name)[:200] if area else None,
    }


def plan(args: argparse.Namespace) -> dict[str, Any]:
    try:
        from pyproj import CRS
        from pyproj.aoi import AreaOfInterest
        from pyproj.transformer import TransformerGroup
    except ImportError as exc:
        raise CliError("pyproj is required for CRS planning") from exc

    disable_proj_network()
    try:
        source = CRS.from_user_input(args.source_crs)
        target = CRS.from_user_input(args.target_crs)
    except (TypeError, ValueError) as exc:
        raise CliError("source or target CRS cannot be parsed") from exc

    bbox_values: list[float] | None = None
    crosses_antimeridian = False
    area_of_interest = None
    if args.bbox is not None:
        bbox_values = [
            finite_number(item, name=f"bbox[{index}]")
            for index, item in enumerate(args.bbox)
        ]
        west, south, east, north = bbox_values
        if south > north:
            raise CliError("bbox south must not exceed north")
        crosses_antimeridian = bool(source.is_geographic and east < west)
        if not crosses_antimeridian:
            try:
                area_of_interest = AreaOfInterest(west, south, east, north)
            except (TypeError, ValueError) as exc:
                raise CliError("bbox is not a valid area of interest") from exc

    try:
        group = TransformerGroup(
            source,
            target,
            always_xy=True,
            area_of_interest=area_of_interest,
            allow_ballpark=args.allow_ballpark,
        )
    except (TypeError, ValueError) as exc:
        raise CliError("PROJ could not construct transformation candidates") from exc

    candidates = [_candidate_summary(item) for item in group.transformers[:5]]
    source_info = crs_summary(source)
    target_info = crs_summary(target)
    linear_target = bool(
        target.is_projected
        and target.axis_info
        and all(
            "degree" not in str(axis.unit_name).casefold() for axis in target.axis_info[:2]
        )
    )
    metric_ready = args.operation not in METRIC_OPERATIONS or linear_target
    warnings: list[str] = []
    if source.is_geographic:
        warnings.append(
            "Source coordinates are angular; GeoPandas segment transforms are vertex-wise, not geodesic."
        )
    if args.operation in METRIC_OPERATIONS and not linear_target:
        warnings.append(
            "Target CRS does not provide projected linear axes for the requested planar operation."
        )
    if crosses_antimeridian:
        warnings.append(
            "The bbox crosses the antimeridian; split/unwrap and densify as justified before to_crs."
        )
    if not group.best_available:
        warnings.append(
            "The best known operation is unavailable, commonly because a transformation grid is absent."
        )
    if not candidates:
        warnings.append("No available transformation candidate satisfies this policy.")
    if _dynamic(source) or _dynamic(target):
        warnings.append(
            "A dynamic CRS is involved; record and validate the coordinate epoch separately."
        )

    return {
        "ok": bool(candidates) and metric_ready and bool(group.best_available),
        "tool": TOOL,
        "source_crs": source_info,
        "target_crs": target_info,
        "purpose": args.operation,
        "coordinate_array_order": "x_y_via_always_xy",
        "source_dynamic_crs": _dynamic(source),
        "target_dynamic_crs": _dynamic(target),
        "bbox": {
            "provided": bbox_values is not None,
            "values_emitted": False,
            "used_as_area_of_interest": area_of_interest is not None,
            "crosses_antimeridian": crosses_antimeridian,
        },
        "operation_policy": {
            "allow_ballpark": bool(args.allow_ballpark),
            "only_best_recommended_for_execution": True,
            "proj_network_enabled": False,
            "metric_operation_ready": metric_ready,
        },
        "candidate_count": len(group.transformers),
        "candidate_summaries_first_five": candidates,
        "best_available": bool(group.best_available),
        "unavailable_operation_count": len(group.unavailable_operations),
        "coordinates_transformed": False,
        "network_accessed": False,
        "coordinates_emitted": False,
        "identifiers_emitted": False,
        "stack": {"packages": package_versions(), "native": native_versions()},
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = plan(args)
        emit_json(report)
        return 0 if report["ok"] else 2
    except Exception as exc:  # noqa: BLE001 - errors are redacted at CLI boundary
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/export_plan.py`

```python
#!/usr/bin/env python3
"""Create a non-executing, redacted vector export and GeoParquet plan."""

from __future__ import annotations

import argparse
import sys
from typing import Any

from _common import (
    ABSOLUTE_MAX_FEATURES,
    DEFAULT_MAX_FEATURES,
    DEFAULT_MAX_INPUT_BYTES,
    CliError,
    bounded_limit,
    checked_input_file,
    checked_output_file,
    emit_json,
    fail_json,
    inspect_local_vector,
    native_versions,
    package_versions,
    positive_int,
    sha256_file,
)

TOOL = "export_plan"
FORMAT_SUFFIXES = {
    "flatgeobuf": {".fgb"},
    "geopackage": {".gpkg"},
    "geojson": {".geojson", ".json"},
    "geoparquet": {".geoparquet", ".parquet"},
    "shapefile": {".shp"},
}
SUFFIX_FORMAT = {
    suffix: format_name
    for format_name, suffixes in FORMAT_SUFFIXES.items()
    for suffix in suffixes
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Plan—but do not execute—a local vector export. Inspect only metadata, "
            "validate a new output path, and emit format/privacy/provenance gates."
        ),
        epilog=(
            "No feature data or coordinates are loaded. URLs, archives, symlinks, "
            "path traversal, and existing output paths are rejected."
        ),
    )
    parser.add_argument("input", help="Allowlisted local vector/GeoParquet input")
    parser.add_argument("output", help="Proposed new local output path")
    parser.add_argument("--root", default=".", help="Existing local I/O root")
    parser.add_argument("--layer", help="Exact input layer name")
    parser.add_argument(
        "--format",
        choices=tuple(sorted(FORMAT_SUFFIXES)),
        help="Target format; default infers from output suffix",
    )
    parser.add_argument(
        "--stable-id-column",
        help="Declared stable feature-ID column (name is not emitted)",
    )
    parser.add_argument(
        "--id-unique-verified",
        action="store_true",
        help="Attest that stable ID is non-null and unique in the planned export",
    )
    parser.add_argument(
        "--index-policy",
        choices=("omit", "include"),
        default="omit",
        help="Whether to serialize the pandas index (default: omit)",
    )
    parser.add_argument(
        "--geometry-encoding",
        choices=("WKB", "geoarrow"),
        default="WKB",
        help="GeoParquet geometry encoding (default: WKB)",
    )
    parser.add_argument(
        "--schema-version",
        choices=("1.0.0", "1.1.0"),
        default="1.0.0",
        help="GeoParquet schema version (default: stable 1.0.0)",
    )
    parser.add_argument(
        "--write-covering-bbox",
        action="store_true",
        help="Plan a GeoParquet 1.1 per-row bbox covering column",
    )
    parser.add_argument(
        "--public-output",
        action="store_true",
        help="Mark the proposed output as intended for public release",
    )
    parser.add_argument(
        "--sensitive-coordinates",
        action="store_true",
        help="Mark input as containing sensitive exact locations",
    )
    parser.add_argument(
        "--generalized-and-reviewed",
        action="store_true",
        help="Attest that coordinates/attributes were generalized and reviewed",
    )
    parser.add_argument(
        "--max-input-bytes",
        type=positive_int,
        default=DEFAULT_MAX_INPUT_BYTES,
    )
    parser.add_argument(
        "--max-features",
        type=positive_int,
        default=DEFAULT_MAX_FEATURES,
        help="Declared-feature threshold for the downstream export",
    )
    return parser


def _format_risks(format_name: str) -> list[str]:
    risks = {
        "geopackage": [
            "One geometry column per layer; additional geometry columns need separate layers or explicit encoding.",
            "Append/overwrite behavior is driver-specific; this plan requires a new file.",
        ],
        "geojson": [
            "Text output exposes exact coordinates and attributes directly.",
            "CRS/type/datetime/large-integer fidelity is limited; RFC 7946 interoperability normally expects WGS84 longitude/latitude.",
        ],
        "shapefile": [
            "Legacy multi-file output has field-name, null, type, encoding, geometry, and size limitations.",
            "A single hash does not cover the complete sidecar set.",
        ],
        "flatgeobuf": [
            "Driver/version interoperability and field-type support must be roundtrip-tested.",
        ],
        "geoparquet": [
            "GeoParquet readers vary in support for schema 1.1 native encodings and bbox covering.",
            "Stable feature IDs require an explicit project column/metadata contract.",
        ],
    }
    return risks[format_name]


def plan(args: argparse.Namespace) -> dict[str, Any]:
    max_features = bounded_limit(
        args.max_features,
        name="max_features",
        maximum=ABSOLUTE_MAX_FEATURES,
    )
    source = checked_input_file(
        args.input,
        root=args.root,
        max_bytes=args.max_input_bytes,
    )
    suffix = str(args.output).casefold().strip()
    suffix = "." + suffix.rsplit(".", 1)[-1] if "." in suffix else ""
    inferred = SUFFIX_FORMAT.get(suffix)
    format_name = args.format or inferred
    if format_name is None:
        raise CliError("target format cannot be inferred from output suffix")
    destination = checked_output_file(
        args.output,
        root=args.root,
        allowed_suffixes=FORMAT_SUFFIXES[format_name],
    )
    if inferred is not None and inferred != format_name:
        raise CliError("target format conflicts with output suffix")

    technical = inspect_local_vector(source, layer=args.layer)
    declared = technical.get("declared_features")
    blockers: list[str] = []
    warnings = _format_risks(format_name)

    if args.stable_id_column is None:
        blockers.append("declare a stable feature-ID column")
    elif not args.id_unique_verified:
        blockers.append("verify the stable ID is non-null and unique")
    if declared is not None and declared > max_features:
        blockers.append("declared feature count exceeds the downstream limit")
    if (
        args.public_output
        and args.sensitive_coordinates
        and not args.generalized_and_reviewed
    ):
        blockers.append(
            "public sensitive-coordinate output requires generalization and review"
        )
    if args.generalized_and_reviewed and not args.sensitive_coordinates:
        warnings.append(
            "Generalization attestation was supplied without marking coordinates sensitive."
        )

    geoparquet_options_used = (
        args.geometry_encoding != "WKB"
        or args.schema_version != "1.0.0"
        or args.write_covering_bbox
    )
    if format_name != "geoparquet" and geoparquet_options_used:
        blockers.append("GeoParquet options are valid only for geoparquet output")
    if format_name == "geoparquet":
        if args.geometry_encoding == "geoarrow" and args.schema_version != "1.1.0":
            blockers.append("native geoarrow encoding requires schema 1.1.0")
        if args.write_covering_bbox and args.schema_version != "1.1.0":
            blockers.append("bbox covering requires schema 1.1.0")
        if args.write_covering_bbox and args.sensitive_coordinates:
            blockers.append(
                "per-row bbox covering is not approved for sensitive coordinates"
            )
        if args.schema_version == "1.1.0":
            warnings.append(
                "GeoPandas describes native encoding and bbox covering as experimental/interoperability-limited."
            )

    if technical["kind"] == "gdal_vector":
        if not technical["crs"]["present"]:
            blockers.append("source CRS metadata is missing")
    elif technical["kind"] == "geoparquet":
        states = technical["crs_metadata_states"]
        if states["null"]:
            blockers.append("one or more GeoParquet geometry columns have unknown CRS")
        if states["missing"]:
            warnings.append(
                "A missing GeoParquet CRS key means OGC:CRS84, not unknown CRS."
            )
    else:
        blockers.append("input Parquet lacks required GeoParquet metadata")

    return {
        "ok": not blockers,
        "tool": TOOL,
        "executed": False,
        "feature_data_loaded": False,
        "source": {
            "sha256": sha256_file(source),
            "bytes": source.stat().st_size,
            "path_emitted": False,
            "technical_inventory": technical,
        },
        "target": {
            "format": format_name,
            "suffix": destination.suffix.casefold(),
            "path_emitted": False,
            "exists": False,
            "index_policy": args.index_policy,
            "stable_id_declared": args.stable_id_column is not None,
            "stable_id_name_emitted": False,
            "stable_id_unique_verified": bool(args.id_unique_verified),
        },
        "geoparquet": (
            {
                "schema_version": args.schema_version,
                "geometry_encoding": args.geometry_encoding,
                "write_covering_bbox": bool(args.write_covering_bbox),
                "default_stable_contract": bool(
                    args.schema_version == "1.0.0"
                    and args.geometry_encoding == "WKB"
                    and not args.write_covering_bbox
                ),
            }
            if format_name == "geoparquet"
            else None
        ),
        "privacy": {
            "public_output": bool(args.public_output),
            "sensitive_coordinates": bool(args.sensitive_coordinates),
            "generalized_and_reviewed": bool(args.generalized_and_reviewed),
            "coordinates_emitted": False,
        },
        "roundtrip_checks_required": [
            "row count and stable-ID set",
            "CRS and active/additional geometry columns",
            "null, empty, invalid, geometry type, and dimensionality counts",
            "field types, nullability, encoding, and expected format losses",
            "protected coarse bounds and representative attributes",
            "new artifact hash and package/native versions",
        ],
        "format_risks": warnings,
        "blockers": blockers,
        "resource_limits": {
            "max_input_bytes": args.max_input_bytes,
            "max_features_for_execution": max_features,
        },
        "network_accessed": False,
        "coordinates_emitted": False,
        "identifiers_emitted": False,
        "stack": {"packages": package_versions(), "native": native_versions()},
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = plan(args)
        emit_json(report)
        return 0 if report["ok"] else 2
    except Exception as exc:  # noqa: BLE001 - errors are redacted at CLI boundary
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/geometry_validity_report.py`

```python
#!/usr/bin/env python3
"""Audit and simulate repair of bounded local geometries with optional new output."""

from __future__ import annotations

import argparse
import hashlib
import sys
from typing import Any

from _common import (
    DEFAULT_MAX_FEATURES,
    DEFAULT_MAX_INPUT_BYTES,
    DEFAULT_MAX_OUTPUT_BYTES,
    CliError,
    checked_input_file,
    checked_output_file,
    crs_summary,
    duplicate_column_state,
    emit_json,
    fail_json,
    finite_number,
    geometry_state,
    load_geodataframe,
    native_versions,
    package_versions,
    positive_int,
    sha256_file,
    write_new_geopackage,
)

TOOL = "geometry_validity_report"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Audit null/empty/invalid geometry and simulate make_valid locally. "
            "Default is dry-run; --repair-output writes only a new GeoPackage."
        ),
        epilog=(
            "No coordinates, paths, IDs, or validity-reason coordinates are emitted. "
            "URLs, archives, symlinks, traversal, and overwrite are rejected."
        ),
    )
    parser.add_argument("input", help="Allowlisted local GDAL vector file")
    parser.add_argument("--root", default=".", help="Existing local I/O root")
    parser.add_argument("--layer", help="Exact input layer name")
    parser.add_argument("--id-column", help="Optional stable ID column to audit")
    parser.add_argument(
        "--method",
        choices=("linework", "structure"),
        default="linework",
        help="Shapely make_valid algorithm (default: linework)",
    )
    parser.add_argument(
        "--drop-collapsed",
        action="store_true",
        help="For structure repair only, drop lower-dimensional collapsed parts",
    )
    parser.add_argument(
        "--precision-grid",
        help=(
            "Optional positive post-repair precision grid in projected CRS units; "
            "geographic or missing CRS is rejected"
        ),
    )
    parser.add_argument(
        "--repair-output",
        help="Optional new .gpkg path; existing paths are never overwritten",
    )
    parser.add_argument(
        "--max-input-bytes",
        type=positive_int,
        default=DEFAULT_MAX_INPUT_BYTES,
    )
    parser.add_argument(
        "--max-output-bytes",
        type=positive_int,
        default=DEFAULT_MAX_OUTPUT_BYTES,
    )
    parser.add_argument(
        "--max-features",
        type=positive_int,
        default=DEFAULT_MAX_FEATURES,
    )
    return parser


def _type_transition_count(before: Any, after: Any) -> int:
    before_types = [
        "missing" if value is None else str(value) for value in before.geom_type
    ]
    after_types = [
        "missing" if value is None else str(value) for value in after.geom_type
    ]
    return sum(left != right for left, right in zip(before_types, after_types))


def report(args: argparse.Namespace) -> dict[str, Any]:
    if args.drop_collapsed and args.method != "structure":
        raise CliError("--drop-collapsed is valid only with --method structure")
    path = checked_input_file(
        args.input,
        root=args.root,
        max_bytes=args.max_input_bytes,
    )
    frame = load_geodataframe(
        path,
        layer=args.layer,
        max_features=args.max_features,
    )
    before_geometry = frame.geometry.copy()
    before = geometry_state(frame)
    id_state = duplicate_column_state(frame, args.id_column)
    crs = crs_summary(frame.crs)

    grid_size: float | None = None
    if args.precision_grid is not None:
        grid_size = finite_number(args.precision_grid, name="precision_grid")
        if grid_size <= 0:
            raise CliError("precision_grid must be greater than zero")
        if not crs["present"] or crs["geographic"] or not crs["projected"]:
            raise CliError("precision_grid requires a known projected CRS")

    repaired_frame = frame.copy()
    repaired_geometry = repaired_frame.geometry.make_valid(
        method=args.method,
        keep_collapsed=not args.drop_collapsed,
    )
    if grid_size is not None:
        repaired_geometry = repaired_geometry.set_precision(
            grid_size,
            mode="valid_output",
        )
    repaired_frame = repaired_frame.set_geometry(repaired_geometry)
    simulated = geometry_state(repaired_frame)

    output_report: dict[str, Any] = {
        "requested": args.repair_output is not None,
        "written": False,
        "path_emitted": False,
        "basename_sha256": None,
        "sha256": None,
        "roundtrip_verified": False,
    }
    if args.repair_output is not None:
        destination = checked_output_file(
            args.repair_output,
            root=args.root,
            allowed_suffixes={".gpkg"},
        )
        write_new_geopackage(
            repaired_frame,
            destination,
            max_output_bytes=args.max_output_bytes,
        )
        roundtrip = load_geodataframe(
            destination,
            layer="repaired",
            max_features=args.max_features,
        )
        roundtrip_state = geometry_state(roundtrip)
        if roundtrip_state != simulated:
            destination.unlink(missing_ok=True)
            raise CliError("roundtrip geometry-state verification failed; output removed")
        output_report = {
            "requested": True,
            "written": True,
            "path_emitted": False,
            "basename_sha256": hashlib.sha256(
                destination.name.encode("utf-8")
            ).hexdigest(),
            "sha256": sha256_file(destination),
            "roundtrip_verified": True,
        }

    return {
        "ok": True,
        "tool": TOOL,
        "dry_run": args.repair_output is None,
        "source": {
            "primary_file_sha256": sha256_file(path),
            "primary_file_bytes": path.stat().st_size,
            "path_emitted": False,
        },
        "crs": crs,
        "stable_id_audit": id_state,
        "before": before,
        "simulated_after": simulated,
        "repair_contract": {
            "method": args.method,
            "keep_collapsed": not args.drop_collapsed,
            "precision_grid": grid_size,
            "precision_grid_units": (
                "source_projected_crs_units" if grid_size is not None else None
            ),
            "type_transition_rows": _type_transition_count(
                before_geometry,
                repaired_geometry,
            ),
            "source_modified": False,
        },
        "output": output_report,
        "network_accessed": False,
        "coordinates_emitted": False,
        "identifiers_emitted": False,
        "stack": {"packages": package_versions(), "native": native_versions()},
        "warnings": [
            "Repair can change type, dimension, component count, area, and emptiness.",
            "Validity reasons were reduced to categories; defect coordinates were not emitted.",
            "A written GeoPackage retains source attributes and coordinates and remains sensitive.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        emit_json(report(args))
        return 0
    except Exception as exc:  # noqa: BLE001 - errors are redacted at CLI boundary
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/sensitive_coordinates_checklist.py`

```python
#!/usr/bin/env python3
"""Produce a deterministic privacy/generalization checklist without reading data."""

from __future__ import annotations

import argparse
import sys

from _common import CliError, emit_json, fail_json, finite_number, positive_int

TOOL = "sensitive_coordinates_checklist"
SENSITIVE_FLAGS = (
    "precise_points",
    "contains_addresses",
    "trajectories",
    "parcel_boundaries",
    "rare_categories",
    "linked_identifiers",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a conservative coordinate/privacy/generalization release "
            "checklist. No file, environment variable, coordinate, or network is read."
        ),
        epilog=(
            "This is a technical review aid, not a legal, ethical, or regulatory "
            "compliance determination. Exact coordinates and addresses can reidentify."
        ),
    )
    parser.add_argument(
        "--audience",
        choices=("private-analysis", "restricted-team", "public"),
        default="private-analysis",
    )
    parser.add_argument("--public-output", action="store_true")
    parser.add_argument("--precise-points", action="store_true")
    parser.add_argument("--contains-addresses", action="store_true")
    parser.add_argument("--trajectories", action="store_true")
    parser.add_argument("--parcel-boundaries", action="store_true")
    parser.add_argument("--rare-categories", action="store_true")
    parser.add_argument("--linked-identifiers", action="store_true")
    parser.add_argument(
        "--generalization",
        action="append",
        choices=(
            "aggregate",
            "coarsen-coordinates",
            "simplify",
            "suppress-small-groups",
            "remove-sensitive-fields",
            "mask-extent",
        ),
        default=[],
        help="Applied/proposed control; repeat for multiple controls",
    )
    parser.add_argument(
        "--minimum-group-size",
        type=positive_int,
        help="Smallest released aggregate group; not a compliance threshold",
    )
    parser.add_argument(
        "--tolerance",
        help="Optional positive generalization tolerance; value is not echoed",
    )
    crs = parser.add_mutually_exclusive_group()
    crs.add_argument(
        "--projected-linear-crs",
        action="store_true",
        help="Attest tolerance uses a reviewed projected linear CRS",
    )
    crs.add_argument(
        "--geographic-crs",
        action="store_true",
        help="Mark coordinates/tolerance as angular longitude-latitude",
    )
    parser.add_argument("--direct-identifiers-removed", action="store_true")
    parser.add_argument("--attribute-review-complete", action="store_true")
    parser.add_argument("--reidentification-review-complete", action="store_true")
    parser.add_argument("--visual-review-complete", action="store_true")
    parser.add_argument("--provenance-recorded", action="store_true")
    parser.add_argument("--tile-and-cdn-access-disabled", action="store_true")
    return parser


def checklist(args: argparse.Namespace) -> dict:
    public = bool(args.public_output or args.audience == "public")
    flags = {name: bool(getattr(args, name)) for name in SENSITIVE_FLAGS}
    sensitive = any(flags.values())
    controls = sorted(set(args.generalization))
    blockers: list[str] = []
    warnings: list[str] = []

    tolerance_provided = args.tolerance is not None
    if tolerance_provided:
        tolerance = finite_number(args.tolerance, name="tolerance")
        if tolerance <= 0:
            raise CliError("tolerance must be greater than zero")
        if not args.projected_linear_crs:
            blockers.append(
                "a numeric generalization tolerance requires a reviewed projected linear CRS"
            )
    if args.geographic_crs and any(
        item in controls for item in ("coarsen-coordinates", "simplify")
    ):
        blockers.append(
            "angular-coordinate generalization needs an explicit distortion-aware design"
        )

    if public and sensitive:
        if not controls:
            blockers.append("public sensitive geodata requires documented generalization")
        if not args.direct_identifiers_removed:
            blockers.append("remove direct identifiers before public release")
        if not args.attribute_review_complete:
            blockers.append("complete an attribute disclosure review")
        if not args.reidentification_review_complete:
            blockers.append("complete a linkage/reidentification review")
        if not args.visual_review_complete:
            blockers.append("inspect the rendered and serialized outputs")
        if not args.provenance_recorded:
            blockers.append("record source and generalization provenance")
    if public and not args.tile_and_cdn_access_disabled:
        blockers.append(
            "disable or explicitly approve tile/CDN access for the public artifact"
        )
    if args.contains_addresses and "remove-sensitive-fields" not in controls:
        blockers.append("exact addresses require removal from released attributes")
    if args.trajectories and "aggregate" not in controls:
        blockers.append("trajectories require aggregation or a separately reviewed model")
    spatial_controls = {
        "aggregate",
        "coarsen-coordinates",
        "mask-extent",
        "simplify",
    }
    if (
        (args.precise_points or args.parcel_boundaries)
        and public
        and not set(controls) & spatial_controls
    ):
        blockers.append("exact geometry needs spatial generalization before release")
    if (
        (args.rare_categories or args.linked_identifiers)
        and public
        and "suppress-small-groups" not in controls
    ):
        blockers.append("small/rare linked groups require suppression review")

    if args.minimum_group_size is None and public and sensitive:
        blockers.append("define and review a minimum released aggregate group size")
    elif args.minimum_group_size is not None:
        if args.minimum_group_size < 5:
            warnings.append(
                "The declared group size is very small; no universal threshold guarantees privacy."
            )
        if "suppress-small-groups" not in controls:
            warnings.append(
                "A group-size value was supplied without the suppress-small-groups control."
            )

    if not sensitive:
        warnings.append(
            "No sensitivity flags were selected; verify that classification is complete."
        )
    if not public:
        warnings.append(
            "Restricted handling still needs access control, retention, and audit policy."
        )
    warnings.extend(
        [
            "Jittering alone is not anonymization and can preserve reidentifiable patterns.",
            "Rasterization, simplification, or coordinate rounding alone does not remove sensitive attributes.",
            "HTML/SVG/GeoJSON can embed exact coordinates and properties beyond what is visibly rendered.",
        ]
    )

    return {
        "ok": not blockers,
        "tool": TOOL,
        "not_a_compliance_determination": True,
        "audience": "public" if public else args.audience,
        "sensitivity": {
            "any_flagged": sensitive,
            "categories": flags,
        },
        "controls": controls,
        "minimum_group_size_declared": args.minimum_group_size is not None,
        "tolerance": {
            "provided": tolerance_provided,
            "value_emitted": False,
            "projected_linear_crs_attested": bool(args.projected_linear_crs),
            "geographic_crs_flagged": bool(args.geographic_crs),
        },
        "review_attestations": {
            "direct_identifiers_removed": bool(args.direct_identifiers_removed),
            "attribute_review_complete": bool(args.attribute_review_complete),
            "reidentification_review_complete": bool(
                args.reidentification_review_complete
            ),
            "visual_review_complete": bool(args.visual_review_complete),
            "provenance_recorded": bool(args.provenance_recorded),
            "tile_and_cdn_access_disabled": bool(
                args.tile_and_cdn_access_disabled
            ),
        },
        "blockers": blockers,
        "warnings": warnings,
        "files_opened": False,
        "environment_read": False,
        "network_accessed": False,
        "coordinates_emitted": False,
        "identifiers_emitted": False,
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = checklist(args)
        emit_json(report)
        return 0 if report["ok"] else 2
    except Exception as exc:  # noqa: BLE001 - errors are redacted at CLI boundary
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/spatial_join_audit.py`

```python
#!/usr/bin/env python3
"""Run a bounded local spatial join and emit only aggregate cardinality."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from typing import Any

from _common import (
    ABSOLUTE_MAX_FEATURES,
    DEFAULT_MAX_FEATURES,
    DEFAULT_MAX_INPUT_BYTES,
    CliError,
    bounded_limit,
    checked_input_file,
    crs_summary,
    duplicate_column_state,
    emit_json,
    fail_json,
    finite_number,
    geometry_state,
    load_geodataframe,
    native_versions,
    package_versions,
    positive_int,
    sha256_file,
)

TOOL = "spatial_join_audit"
DEFAULT_MAX_PAIRS = 1_000_000
ABSOLUTE_MAX_PAIRS = 10_000_000


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Audit a bounded local binary-predicate or nearest spatial join. "
            "Only aggregate multiplicity is emitted; no pairs, IDs, or coordinates."
        ),
        epilog=(
            "Both inputs must be local allowlisted files under --root. Invalid or "
            "CRS-incompatible inputs block execution. All operations are planar."
        ),
    )
    parser.add_argument("left", help="Local left vector file")
    parser.add_argument("right", help="Local right vector file")
    parser.add_argument("--root", default=".", help="Existing local I/O root")
    parser.add_argument("--left-layer", help="Exact left layer name")
    parser.add_argument("--right-layer", help="Exact right layer name")
    parser.add_argument("--left-id", help="Optional left stable ID column to audit")
    parser.add_argument("--right-id", help="Optional right stable ID column to audit")
    parser.add_argument(
        "--mode",
        choices=("predicate", "nearest"),
        default="predicate",
        help="Join mode (default: predicate)",
    )
    parser.add_argument(
        "--predicate",
        default="intersects",
        help="Spatial-index predicate for predicate mode (default: intersects)",
    )
    parser.add_argument(
        "--distance",
        help="Positive CRS-unit scalar required for predicate=dwithin",
    )
    parser.add_argument(
        "--max-distance",
        help="Optional positive CRS-unit search limit for nearest mode",
    )
    parser.add_argument(
        "--exclusive",
        action="store_true",
        help="Nearest mode: exclude geometrically equal candidates",
    )
    parser.add_argument(
        "--on-attribute",
        action="append",
        default=[],
        help="Additional equality column present on both sides; repeat as needed",
    )
    parser.add_argument(
        "--max-input-bytes",
        type=positive_int,
        default=DEFAULT_MAX_INPUT_BYTES,
        help="Maximum bytes for each primary input file",
    )
    parser.add_argument(
        "--max-features",
        type=positive_int,
        default=DEFAULT_MAX_FEATURES,
        help=f"Maximum features per input (default: {DEFAULT_MAX_FEATURES})",
    )
    parser.add_argument(
        "--max-pairs",
        type=positive_int,
        default=DEFAULT_MAX_PAIRS,
        help=f"Maximum joined pairs before failing closed (default: {DEFAULT_MAX_PAIRS})",
    )
    return parser


def _work_frame(frame: Any, row_column: str, attributes: list[str]) -> Any:
    active = frame.geometry.name
    columns = [active, *attributes]
    work = frame.loc[:, columns].copy()
    if active != "_audit_geometry":
        work = work.rename_geometry("_audit_geometry")
    work[row_column] = range(len(work))
    return work


def _counter_summary(counter: Counter[int], total_features: int) -> dict[str, int]:
    matched = len(counter)
    return {
        "matched_features": matched,
        "unmatched_features": total_features - matched,
        "features_with_one_match": sum(count == 1 for count in counter.values()),
        "features_with_multiple_matches": sum(
            count > 1 for count in counter.values()
        ),
        "maximum_matches_for_one_feature": max(counter.values(), default=0),
    }


def _run_chunked_join(
    left: Any,
    right: Any,
    *,
    mode: str,
    predicate: str,
    distance: float | None,
    max_distance: float | None,
    exclusive: bool,
    attributes: list[str],
    max_pairs: int,
) -> dict[str, Any]:
    try:
        import geopandas as gpd
    except ImportError as exc:
        raise CliError("GeoPandas is required for join analysis") from exc

    left_work = _work_frame(left, "_audit_left_row", attributes)
    right_work = _work_frame(right, "_audit_right_row", attributes)
    if len(right_work) > max_pairs:
        raise CliError(
            "right feature count exceeds max_pairs; one left feature could match all"
        )
    left_counts: Counter[int] = Counter()
    right_counts: Counter[int] = Counter()
    pair_count = 0
    right_size = max(len(right_work), 1)
    chunk_size = max(1, min(512, max_pairs // right_size or 1))

    for start in range(0, len(left_work), chunk_size):
        chunk = left_work.iloc[start : start + chunk_size]
        if mode == "nearest":
            joined = gpd.sjoin_nearest(
                chunk,
                right_work,
                how="inner",
                max_distance=max_distance,
                exclusive=exclusive,
            )
        else:
            joined = gpd.sjoin(
                chunk,
                right_work,
                how="inner",
                predicate=predicate,
                distance=distance,
                on_attribute=attributes or None,
            )
        pair_count += len(joined)
        if pair_count > max_pairs:
            raise CliError(
                f"joined pair count exceeds the configured {max_pairs}-pair limit"
            )
        left_counts.update(int(value) for value in joined["_audit_left_row"])
        right_counts.update(int(value) for value in joined["_audit_right_row"])

    return {
        "pair_count": pair_count,
        "left": _counter_summary(left_counts, len(left)),
        "right": _counter_summary(right_counts, len(right)),
        "many_to_many_observed": bool(
            any(count > 1 for count in left_counts.values())
            and any(count > 1 for count in right_counts.values())
        ),
        "pairs_emitted": False,
        "chunked": True,
        "chunk_size": chunk_size,
    }


def audit(args: argparse.Namespace) -> dict[str, Any]:
    max_features = bounded_limit(
        args.max_features,
        name="max_features",
        maximum=ABSOLUTE_MAX_FEATURES,
    )
    max_pairs = bounded_limit(
        args.max_pairs,
        name="max_pairs",
        maximum=ABSOLUTE_MAX_PAIRS,
    )
    left_path = checked_input_file(
        args.left,
        root=args.root,
        max_bytes=args.max_input_bytes,
    )
    right_path = checked_input_file(
        args.right,
        root=args.root,
        max_bytes=args.max_input_bytes,
    )
    if left_path == right_path and args.left_layer == args.right_layer:
        raise CliError("left and right inputs resolve to the same layer")

    left = load_geodataframe(
        left_path,
        layer=args.left_layer,
        max_features=max_features,
    )
    right = load_geodataframe(
        right_path,
        layer=args.right_layer,
        max_features=max_features,
    )
    left_state = geometry_state(left)
    right_state = geometry_state(right)
    left_id = duplicate_column_state(left, args.left_id)
    right_id = duplicate_column_state(right, args.right_id)

    try:
        from pyproj import CRS
    except ImportError as exc:
        raise CliError("pyproj is required for CRS comparison") from exc
    blockers: list[str] = []
    same_crs = False
    if left.crs is None or right.crs is None:
        blockers.append("both inputs require explicit CRS metadata")
    else:
        same_crs = CRS.from_user_input(left.crs).equals(CRS.from_user_input(right.crs))
        if not same_crs:
            blockers.append("input CRS values are not equivalent")
    if left_state["invalid"] or right_state["invalid"]:
        blockers.append("invalid input geometries require separate repair review")
    for attribute in args.on_attribute:
        if attribute not in left.columns or attribute not in right.columns:
            blockers.append("an on_attribute column is absent from one input")
            break

    distance: float | None = None
    max_distance: float | None = None
    if args.mode == "predicate":
        if args.exclusive or args.max_distance is not None:
            blockers.append("--exclusive/--max-distance apply only to nearest mode")
        if args.predicate == "dwithin":
            if args.distance is None:
                blockers.append("predicate dwithin requires --distance")
            else:
                distance = finite_number(args.distance, name="distance")
                if distance <= 0:
                    blockers.append("distance must be greater than zero")
        elif args.distance is not None:
            blockers.append("--distance is valid only for predicate dwithin")
        if not blockers:
            valid = set(left.sindex.valid_query_predicates) & set(
                right.sindex.valid_query_predicates
            )
            if args.predicate not in valid:
                blockers.append("predicate is not supported by both spatial indexes")
    else:
        if args.distance is not None or args.on_attribute:
            blockers.append("--distance/--on-attribute apply only to predicate mode")
        if args.max_distance is not None:
            max_distance = finite_number(args.max_distance, name="max_distance")
            if max_distance <= 0:
                blockers.append("max_distance must be greater than zero")

    geographic = bool(left.crs is not None and left.crs.is_geographic)
    if args.mode == "nearest" and geographic:
        blockers.append("nearest joins are inaccurate in a geographic CRS")
    if args.predicate == "dwithin" and geographic:
        blockers.append("dwithin distance is angular in a geographic CRS")

    pair_audit = None
    if not blockers:
        pair_audit = _run_chunked_join(
            left,
            right,
            mode=args.mode,
            predicate=args.predicate,
            distance=distance,
            max_distance=max_distance,
            exclusive=args.exclusive,
            attributes=args.on_attribute,
            max_pairs=max_pairs,
        )

    warnings = [
        "intersects includes boundary contact; contains/within and covers/covered_by differ at boundaries.",
        "All GeoPandas joins are planar and ignore Z.",
        "Declare expected cardinality separately and compare it with this aggregate audit.",
    ]
    if args.mode == "nearest":
        warnings.append(
            "Nearest returns every equidistant match and has no k parameter."
        )
    if left_state["missing"] or left_state["empty"]:
        warnings.append("Missing/empty left geometries remain unmatched.")
    if right_state["missing"] or right_state["empty"]:
        warnings.append("Missing/empty right geometries remain unmatched.")

    return {
        "ok": not blockers,
        "tool": TOOL,
        "mode": args.mode,
        "predicate": args.predicate if args.mode == "predicate" else None,
        "distance_provided": distance is not None,
        "max_distance_provided": max_distance is not None,
        "exclusive": bool(args.exclusive),
        "on_attribute_column_count": len(args.on_attribute),
        "crs": {
            "left": crs_summary(left.crs),
            "right": crs_summary(right.crs),
            "equivalent": same_crs,
        },
        "left": {
            "source_sha256": sha256_file(left_path),
            "geometry_state": left_state,
            "stable_id_audit": left_id,
        },
        "right": {
            "source_sha256": sha256_file(right_path),
            "geometry_state": right_state,
            "stable_id_audit": right_id,
        },
        "pair_audit": pair_audit,
        "blockers": blockers,
        "resource_limits": {
            "max_input_bytes_each": args.max_input_bytes,
            "max_features_each": max_features,
            "max_pairs": max_pairs,
        },
        "network_accessed": False,
        "coordinates_emitted": False,
        "identifiers_emitted": False,
        "stack": {"packages": package_versions(), "native": native_versions()},
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = audit(args)
        emit_json(report)
        return 0 if report["ok"] else 2
    except Exception as exc:  # noqa: BLE001 - errors are redacted at CLI boundary
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/vector_inventory.py`

```python
#!/usr/bin/env python3
"""Create a redacted, metadata-only inventory of one local vector dataset."""

from __future__ import annotations

import argparse
import hashlib
import sys

from _common import (
    ABSOLUTE_MAX_FEATURES,
    DEFAULT_MAX_FEATURES,
    DEFAULT_MAX_INPUT_BYTES,
    PINNED_STACK,
    bounded_limit,
    checked_input_file,
    emit_json,
    fail_json,
    inspect_local_vector,
    native_versions,
    package_versions,
    positive_int,
    sha256_file,
)

TOOL = "vector_inventory"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Inventory one allowlisted local vector file without loading feature "
            "coordinates or emitting paths, layer names, fields, IDs, or bounds."
        ),
        epilog=(
            "URLs, GDAL VSI paths, archives, compression, symlinks, traversal, "
            "and non-allowlisted extensions are rejected. Native GDAL/GEOS/PROJ "
            "parsers remain a trust boundary; inspect only vetted local files."
        ),
    )
    parser.add_argument("input", help="Local vector or GeoParquet file")
    parser.add_argument(
        "--root",
        default=".",
        help="Existing local root that must contain the input (default: .)",
    )
    parser.add_argument(
        "--layer",
        help="Exact local layer name; required for multi-layer GDAL datasets",
    )
    parser.add_argument(
        "--max-input-bytes",
        type=positive_int,
        default=DEFAULT_MAX_INPUT_BYTES,
        help=f"Maximum primary-file bytes (default: {DEFAULT_MAX_INPUT_BYTES})",
    )
    parser.add_argument(
        "--max-features",
        type=positive_int,
        default=DEFAULT_MAX_FEATURES,
        help=(
            "Downstream feature-load threshold to compare with declared count "
            f"(default: {DEFAULT_MAX_FEATURES}; no features are loaded)"
        ),
    )
    return parser


def inventory(args: argparse.Namespace) -> dict:
    max_features = bounded_limit(
        args.max_features,
        name="max_features",
        maximum=ABSOLUTE_MAX_FEATURES,
    )
    path = checked_input_file(
        args.input,
        root=args.root,
        max_bytes=args.max_input_bytes,
    )
    technical = inspect_local_vector(path, layer=args.layer)
    installed = package_versions()
    declared = technical.get("declared_features")
    warnings = [
        "No feature values, coordinates, bounds, paths, layer names, or field names were emitted.",
        "GDAL/GEOS/PROJ and binary wheels are native-code trust boundaries.",
        "Driver metadata is not proof that every feature or field will parse safely.",
    ]
    if path.suffix.casefold() == ".shp":
        warnings.append(
            "The hash covers only the .shp primary file, not required sidecars."
        )
    if declared is None:
        warnings.append(
            "The driver did not provide a cheap feature count; downstream reads must enforce limit+1."
        )
    return {
        "ok": True,
        "tool": TOOL,
        "source": {
            "basename_sha256": hashlib.sha256(path.name.encode("utf-8")).hexdigest(),
            "suffix": path.suffix.casefold(),
            "primary_file_bytes": path.stat().st_size,
            "primary_file_sha256": sha256_file(path),
            "path_emitted": False,
        },
        "technical_inventory": technical,
        "resource_limits": {
            "max_input_bytes": args.max_input_bytes,
            "max_features_for_downstream_load": max_features,
            "declared_within_feature_limit": (
                None if declared is None else declared <= max_features
            ),
            "feature_data_loaded": False,
        },
        "stack": {
            "packages": installed,
            "native": native_versions(),
            "matches_pinned_snapshot": {
                name: installed.get(name) == expected
                for name, expected in PINNED_STACK.items()
            },
        },
        "network_accessed": False,
        "coordinates_emitted": False,
        "identifiers_emitted": False,
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        emit_json(inventory(args))
        return 0
    except Exception as exc:  # noqa: BLE001 - errors are redacted at CLI boundary
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
```
