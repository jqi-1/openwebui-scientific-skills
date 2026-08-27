---
name: geomaster
description: Comprehensive geospatial science skill covering remote sensing, GIS, spatial analysis, machine learning for earth observation, and 30+ scientific domains. Supports satellite imagery processing (Sentinel, Landsat, MODIS, SAR, hyperspectral), vector and raster data operations, spatial statistics, point cloud processing, network analysis, cloud-native workflows (STAC, COG, Planetary Computer), and 8 programming languages (Python, R, Julia, JavaScript, C++, Java, Go, Rust) with 500+ code examples. Use for remote sensing workflows, GIS analysis, spatial ML, Earth observation data processing, terrain analysis, hydrological modeling, marine spatial analysis, atmospheric science, and any geospatial computation task.
---

# GeoMaster

Comprehensive geospatial science skill covering GIS, remote sensing, spatial analysis, and ML for Earth observation across 70+ topics with 500+ code examples in 8 programming languages.

## Installation

```bash
# Core Python stack (conda recommended)
conda install -c conda-forge gdal rasterio fiona shapely pyproj geopandas

# Remote sensing & ML
uv pip install rsgislib torchgeo earthengine-api
uv pip install scikit-learn xgboost torch-geometric

# Network & visualization
uv pip install osmnx networkx folium keplergl
uv pip install cartopy contextily mapclassify

# Big data & cloud
uv pip install xarray rioxarray dask-geopandas
uv pip install pystac-client planetary-computer

# Point clouds
uv pip install laspy pylas open3d pdal

# Databases
conda install -c conda-forge postgis spatialite
```

## Quick Start

### NDVI from Sentinel-2

```python
import rasterio
import numpy as np

with rasterio.open('sentinel2.tif') as src:
    red = src.read(4).astype(float)   # B04
    nir = src.read(8).astype(float)   # B08
    ndvi = (nir - red) / (nir + red + 1e-8)
    ndvi = np.nan_to_num(ndvi, nan=0)

    profile = src.profile
    profile.update(count=1, dtype=rasterio.float32)

    with rasterio.open('ndvi.tif', 'w', **profile) as dst:
        dst.write(ndvi.astype(rasterio.float32), 1)
```

### Spatial Analysis with GeoPandas

```python
import geopandas as gpd

# Load and ensure same CRS
zones = gpd.read_file('zones.geojson')
points = gpd.read_file('points.geojson')

if zones.crs != points.crs:
    points = points.to_crs(zones.crs)

# Spatial join and statistics
joined = gpd.sjoin(points, zones, how='inner', predicate='within')
stats = joined.groupby('zone_id').agg({
    'value': ['count', 'mean', 'std', 'min', 'max']
}).round(2)
```

### Google Earth Engine Time Series

```python
import ee
import pandas as pd

ee.Initialize(project='your-project')
roi = ee.Geometry.Point([-122.4, 37.7]).buffer(10000)

s2 = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
      .filterBounds(roi)
      .filterDate('2020-01-01', '2023-12-31')
      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)))

def add_ndvi(img):
    return img.addBands(img.normalizedDifference(['B8', 'B4']).rename('NDVI'))

s2_ndvi = s2.map(add_ndvi)

def extract_series(image):
    stats = image.reduceRegion(ee.Reducer.mean(), roi.centroid(), scale=10, maxPixels=1e9)
    return ee.Feature(None, {'date': image.date().format('YYYY-MM-dd'), 'ndvi': stats.get('NDVI')})

series = s2_ndvi.map(extract_series).getInfo()
df = pd.DataFrame([f['properties'] for f in series['features']])
df['date'] = pd.to_datetime(df['date'])
```

## Core Concepts

### Data Types

| Type | Examples | Libraries |
|------|----------|-----------|
| Vector | Shapefile, GeoJSON, GeoPackage | GeoPandas, Fiona, GDAL |
| Raster | GeoTIFF, NetCDF, COG | Rasterio, Xarray, GDAL |
| Point Cloud | LAS, LAZ | Laspy, PDAL, Open3D |

### Coordinate Systems

- **EPSG:4326** (WGS 84) - Geographic, lat/lon, use for storage
- **EPSG:3857** (Web Mercator) - Web maps only (don't use for area/distance!)
- **EPSG:326xx/327xx** (UTM) - Metric calculations, <1% distortion per zone
- Use `gdf.estimate_utm_crs()` for automatic UTM detection

```python
# Always check CRS before operations
assert gdf1.crs == gdf2.crs, "CRS mismatch!"

# For area/distance calculations, use projected CRS
gdf_metric = gdf.to_crs(gdf.estimate_utm_crs())
area_sqm = gdf_metric.geometry.area
```

### OGC Standards

- **WMS**: Web Map Service - raster maps
- **WFS**: Web Feature Service - vector data
- **WCS**: Web Coverage Service - raster coverage
- **STAC**: Spatiotemporal Asset Catalog - modern metadata

## Common Operations

### Spectral Indices

```python
def calculate_indices(image_path):
    """NDVI, EVI, SAVI, NDWI from Sentinel-2."""
    with rasterio.open(image_path) as src:
        B02, B03, B04, B08, B11 = [src.read(i).astype(float) for i in [1,2,3,4,5]]

    ndvi = (B08 - B04) / (B08 + B04 + 1e-8)
    evi = 2.5 * (B08 - B04) / (B08 + 6*B04 - 7.5*B02 + 1)
    savi = ((B08 - B04) / (B08 + B04 + 0.5)) * 1.5
    ndwi = (B03 - B08) / (B03 + B08 + 1e-8)

    return {'NDVI': ndvi, 'EVI': evi, 'SAVI': savi, 'NDWI': ndwi}
```

### Vector Operations

```python
# Buffer (use projected CRS!)
gdf_proj = gdf.to_crs(gdf.estimate_utm_crs())
gdf['buffer_1km'] = gdf_proj.geometry.buffer(1000)

# Spatial relationships
intersects = gdf[gdf.geometry.intersects(other_geometry)]
contains = gdf[gdf.geometry.contains(point_geometry)]

# Geometric operations
gdf['centroid'] = gdf.geometry.centroid
gdf['simplified'] = gdf.geometry.simplify(tolerance=0.001)

# Overlay operations
intersection = gpd.overlay(gdf1, gdf2, how='intersection')
union = gpd.overlay(gdf1, gdf2, how='union')
```

### Terrain Analysis

```python
def terrain_metrics(dem_path):
    """Calculate slope, aspect, hillshade from DEM."""
    with rasterio.open(dem_path) as src:
        dem = src.read(1)

    dy, dx = np.gradient(dem)
    slope = np.arctan(np.sqrt(dx**2 + dy**2)) * 180 / np.pi
    aspect = (90 - np.arctan2(-dy, dx) * 180 / np.pi) % 360

    # Hillshade
    az_rad, alt_rad = np.radians(315), np.radians(45)
    hillshade = (np.sin(alt_rad) * np.sin(np.radians(slope)) +
                 np.cos(alt_rad) * np.cos(np.radians(slope)) *
                 np.cos(np.radians(aspect) - az_rad))

    return slope, aspect, hillshade
```

### Network Analysis

```python
import osmnx as ox
import networkx as nx

# Download and analyze street network
G = ox.graph_from_place('San Francisco, CA', network_type='drive')
G = ox.add_edge_speeds(G).add_edge_travel_times(G)

# Shortest path
orig = ox.distance.nearest_nodes(G, -122.4, 37.7)
dest = ox.distance.nearest_nodes(G, -122.3, 37.8)
route = nx.shortest_path(G, orig, dest, weight='travel_time')
```

## Image Classification

```python
from sklearn.ensemble import RandomForestClassifier
import rasterio
from rasterio.features import rasterize

def classify_imagery(raster_path, training_gdf, output_path):
    """Train RF and classify imagery."""
    with rasterio.open(raster_path) as src:
        image = src.read()
        profile = src.profile
        transform = src.transform

    # Extract training data
    X_train, y_train = [], []
    for _, row in training_gdf.iterrows():
        mask = rasterize([(row.geometry, 1)],
                        out_shape=(profile['height'], profile['width']),
                        transform=transform, fill=0, dtype=np.uint8)
        pixels = image[:, mask > 0].T
        X_train.extend(pixels)
        y_train.extend([row['class_id']] * len(pixels))

    # Train and predict
    rf = RandomForestClassifier(n_estimators=100, max_depth=20, n_jobs=-1)
    rf.fit(X_train, y_train)

    prediction = rf.predict(image.reshape(image.shape[0], -1).T)
    prediction = prediction.reshape(profile['height'], profile['width'])

    profile.update(dtype=rasterio.uint8, count=1)
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(prediction.astype(rasterio.uint8), 1)

    return rf
```

## Modern Cloud-Native Workflows

### STAC + Planetary Computer

```python
import pystac_client
import planetary_computer
import odc.stac

# Search Sentinel-2 via STAC
catalog = pystac_client.Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace,
)

search = catalog.search(
    collections=["sentinel-2-l2a"],
    bbox=[-122.5, 37.7, -122.3, 37.9],
    datetime="2023-01-01/2023-12-31",
    query={"eo:cloud_cover": {"lt": 20}},
)

# Load as xarray (cloud-native!)
data = odc.stac.load(
    list(search.get_items())[:5],
    bands=["B02", "B03", "B04", "B08"],
    crs="EPSG:32610",
    resolution=10,
)

# Calculate NDVI on xarray
ndvi = (data.B08 - data.B04) / (data.B08 + data.B04)
```

### Cloud-Optimized GeoTIFF (COG)

```python
import rasterio
from rasterio.session import AWSSession

# Read COG directly from cloud (partial reads)
session = AWSSession(aws_access_key_id=..., aws_secret_access_key=...)
with rasterio.open('s3://bucket/path.tif', session=session) as src:
    # Read only window of interest
    window = ((1000, 2000), (1000, 2000))
    subset = src.read(1, window=window)

# Write COG
with rasterio.open('output.tif', 'w', **profile,
                   tiled=True, blockxsize=256, blockysize=256,
                   compress='DEFLATE', predictor=2) as dst:
    dst.write(data)

# Validate COG
from rio_cogeo.cogeo import cog_validate
cog_validate('output.tif')
```

## Performance Tips

```python
# 1. Spatial indexing (10-100x faster queries)
gdf.sindex  # Auto-created by GeoPandas

# 2. Chunk large rasters
with rasterio.open('large.tif') as src:
    for i, window in src.block_windows(1):
        block = src.read(1, window=window)

# 3. Dask for big data
import dask.array as da
dask_array = da.from_rasterio('large.tif', chunks=(1, 1024, 1024))

# 4. Use Arrow for I/O
gdf.to_file('output.gpkg', use_arrow=True)

# 5. GDAL caching
from osgeo import gdal
gdal.SetCacheMax(2**30)  # 1GB cache

# 6. Parallel processing
rf = RandomForestClassifier(n_jobs=-1)  # All cores
```

## Best Practices

1. **Always check CRS** before spatial operations
2. **Use projected CRS** for area/distance calculations
3. **Validate geometries**: `gdf = gdf[gdf.is_valid]`
4. **Handle missing data**: `gdf['geometry'] = gdf['geometry'].fillna(None)`
5. **Use efficient formats**: GeoPackage > Shapefile, Parquet for large data
6. **Apply cloud masking** to optical imagery
7. **Preserve lineage** for reproducible research
8. **Use appropriate resolution** for your analysis scale

## Detailed Documentation

- **[Coordinate Systems](references/coordinate-systems.md)** - CRS fundamentals, UTM, transformations
- **[Core Libraries](references/core-libraries.md)** - GDAL, Rasterio, GeoPandas, Shapely
- **[Remote Sensing](references/remote-sensing.md)** - Satellite missions, spectral indices, SAR
- **[Machine Learning](references/machine-learning.md)** - Deep learning, CNNs, GNNs for RS
- **[GIS Software](references/gis-software.md)** - QGIS, ArcGIS, GRASS integration
- **[Scientific Domains](references/scientific-domains.md)** - Marine, hydrology, agriculture, forestry
- **[Advanced GIS](references/advanced-gis.md)** - 3D GIS, spatiotemporal, topology
- **[Big Data](references/big-data.md)** - Distributed processing, GPU acceleration
- **[Industry Applications](references/industry-applications.md)** - Urban planning, disaster management
- **[Programming Languages](references/programming-languages.md)** - Python, R, Julia, JS, C++, Java, Go, Rust
- **[Data Sources](references/data-sources.md)** - Satellite catalogs, APIs
- **[Troubleshooting](references/troubleshooting.md)** - Common issues, debugging, error reference
- **[Code Examples](references/code-examples.md)** - 500+ examples

---

**GeoMaster covers everything from basic GIS operations to advanced remote sensing and machine learning.**

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/geomaster/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/advanced-gis.md`

# Advanced GIS Topics

Advanced spatial analysis techniques: 3D GIS, spatiotemporal analysis, topology, and network analysis.

## 3D GIS

### 3D Vector Operations

```python
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon
import pyproj
import numpy as np

# Create 3D geometries (with Z coordinate)
point_3d = Point(0, 0, 100)  # x, y, elevation
line_3d = LineString([(0, 0, 0), (100, 100, 50)])

# Load 3D data
gdf_3d = gpd.read_file('buildings_3d.geojson')

# Access Z coordinates
gdf_3d['height'] = gdf_3d.geometry.apply(lambda g: g.coords[0][2] if g.has_z else None)

# 3D buffer (cylinder)
def buffer_3d(point, radius, height):
    """Create a 3D cylindrical buffer."""
    base = Point(point.x, point.y).buffer(radius)
    # Extrude to 3D (conceptual)
    return base, point.z, point.z + height

# 3D distance (Euclidean in 3D space)
def distance_3d(point1, point2):
    """Calculate 3D Euclidean distance."""
    dx = point2.x - point1.x
    dy = point2.y - point1.y
    dz = point2.z - point1.z
    return np.sqrt(dx**2 + dy**2 + dz**2)
```

### 3D Raster Analysis

```python
import rasterio
import numpy as np

# Voxel-based analysis
def voxel_analysis(dem_path, dsm_path):
    """Analyze volume between DEM and DSM."""
    with rasterio.open(dem_path) as src_dem:
        dem = src_dem.read(1)
        transform = src_dem.transform

    with rasterio.open(dsm_path) as src_dsm:
        dsm = src_dsm.read(1)

    # Height difference
    height = dsm - dem

    # Volume calculation
    pixel_area = transform[0] * transform[4]  # Usually negative
    volume = np.sum(height[height > 0]) * abs(pixel_area)

    # Volume per height class
    height_bins = [0, 5, 10, 20, 50, 100]
    volume_by_class = {}

    for i in range(len(height_bins) - 1):
        mask = (height >= height_bins[i]) & (height < height_bins[i + 1])
        volume_by_class[f'{height_bins[i]}-{height_bins[i+1]}m'] = \
            np.sum(height[mask]) * abs(pixel_area)

    return volume, volume_by_class
```

### Viewshed Analysis

```python
def viewshed(dem, observer_x, observer_y, observer_height=1.7, max_distance=5000):
    """
    Calculate viewshed using line-of-sight algorithm.
    """

    # Convert observer to raster coordinates
    observer_row = int((observer_y - dem_origin_y) / cell_size)
    observer_col = int((observer_x - dem_origin_x) / cell_size)

    rows, cols = dem.shape
    viewshed = np.zeros_like(dem, dtype=bool)

    observer_z = dem[observer_row, observer_col] + observer_height

    # For each direction
    for angle in np.linspace(0, 2*np.pi, 360):
        # Cast ray
        for r in range(1, int(max_distance / cell_size)):
            row = observer_row + int(r * np.sin(angle))
            col = observer_col + int(r * np.cos(angle))

            if row < 0 or row >= rows or col < 0 or col >= cols:
                break

            target_z = dem[row, col]

            # Line-of-sight calculation
            dist = r * cell_size
            line_height = observer_z + (target_z - observer_z) * (dist / max_distance)

            if target_z > line_height:
                viewshed[row, col] = False
            else:
                viewshed[row, col] = True

    return viewshed
```

## Spatiotemporal Analysis

### Trajectory Analysis

```python
import movingpandas as mpd
import geopandas as gpd
import pandas as pd

# Create trajectory from point data
gdf = gpd.read_file('gps_points.gpkg')

# Convert to trajectory
traj_collection = mpd.TrajectoryCollection(gdf, 'track_id', t='timestamp')

# Split trajectories (e.g., by time gap)
traj_collection = mpd.SplitByObservationGap(traj_collection, gap=pd.Timedelta('1 hour'))

# Trajectory statistics
for traj in traj_collection:
    print(f"Trajectory {traj.id}:")
    print(f"  Length: {traj.get_length() / 1000:.2f} km")
    print(f"  Duration: {traj.get_duration()}")
    print(f"  Speed: {traj.get_speed() * 3.6:.2f} km/h")

# Stop detection
stops = mpd.stop_detection(
    traj_collection,
    max_diameter=100,  # meters
    min_duration=pd.Timedelta('5 minutes')
)

# Generalization (simplify trajectories)
traj_generalized = mpd.DouglasPeuckerGeneralizer(traj_collection, tolerance=10).generalize()

# Split by stop
traj_moving, stops = mpd.StopSplitter(traj_collection).split()
```

### Space-Time Cube

```python
def create_space_time_cube(gdf, time_column='timestamp', grid_size=100, time_step='1H'):
    """
    Create a 3D space-time cube for hotspot analysis.
    """

    # 1. Spatial binning
    gdf['x_bin'] = (gdf.geometry.x // grid_size).astype(int)
    gdf['y_bin'] = (gdf.geometry.y // grid_size).astype(int)

    # 2. Temporal binning
    gdf['t_bin'] = gdf[time_column].dt.floor(time_step)

    # 3. Create cube (x, y, time)
    cube = gdf.groupby(['x_bin', 'y_bin', 't_bin']).size().unstack(fill_value=0)

    return cube

def emerging_hot_spot_analysis(cube, k=8):
    """
    Emerging Hot Spot Analysis (as implemented in ArcGIS).
    Simplified version using Getis-Ord Gi* statistic.
    """
    from esda.getisord import G_Local

    # Calculate Gi* statistic for each time step
    hotspots = {}
    for timestep in cube.columns:
        data = cube[timestep].values.reshape(-1, 1)
        g_local = G_Local(data, k=k)
        hotspots[timestep] = g_local.p_sim < 0.05  # Significant hotspots

    return hotspots
```

## Topology

### Topological Relationships

```python
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import unary_union

# Planar graph
def build_planar_graph(lines_gdf):
    """Build a planar graph from line features."""
    import networkx as nx

    G = nx.Graph()

    # Add nodes at intersections
    for i, line1 in lines_gdf.iterrows():
        for j, line2 in lines_gdf.iterrows():
            if i < j:
                if line1.geometry.intersects(line2.geometry):
                    intersection = line1.geometry.intersection(line2.geometry)
                    G.add_node((intersection.x, intersection.y))

    # Add edges
    for _, line in lines_gdf.iterrows():
        coords = list(line.geometry.coords)
        G.add_edge(coords[0], coords[-1],
                   weight=line.geometry.length,
                   geometry=line.geometry)

    return G

# Topology validation
def validate_topology(gdf):
    """Check for topological errors."""

    errors = []

    # 1. Check for gaps
    if gdf.geom_type.iloc[0] == 'Polygon':
        dissolved = unary_union(gdf.geometry)
        for i, geom in enumerate(gdf.geometry):
            if not geom.touches(dissolved - geom):
                errors.append(f"Gap detected at feature {i}")

    # 2. Check for overlaps
    for i, geom1 in enumerate(gdf.geometry):
        for j, geom2 in enumerate(gdf.geometry):
            if i < j and geom1.overlaps(geom2):
                errors.append(f"Overlap between features {i} and {j}")

    # 3. Check for self-intersections
    for i, geom in enumerate(gdf.geometry):
        if not geom.is_valid:
            errors.append(f"Self-intersection at feature {i}: {geom.is_valid}")

    return errors
```

## Network Analysis

### Advanced Routing

```python
import osmnx as ox
import networkx as nx

# Download and prepare network
G = ox.graph_from_place('Portland, Maine, USA', network_type='drive')
G = ox.add_edge_speeds(G)
G = ox.add_edge_travel_times(G)

# Multi-criteria routing
def multi_criteria_routing(G, orig, dest, weights=['length', 'travel_time']):
    """
    Find routes optimizing for multiple criteria.
    """
    # Normalize weights
    for w in weights:
        values = [G.edges[e][w] for e in G.edges]
        min_val, max_val = min(values), max(values)
        for e in G.edges:
            G.edges[e][f'{w}_norm'] = (G.edges[e][w] - min_val) / (max_val - min_val)

    # Combined weight
    for e in G.edges:
        G.edges[e]['combined'] = sum(G.edges[e][f'{w}_norm'] for w in weights) / len(weights)

    # Find path
    route = nx.shortest_path(G, orig, dest, weight='combined')
    return route

# Isochrone (accessibility area)
def isochrone(G, center_node, time_limit=600):
    """
    Calculate accessible area within time limit.
    """
    # Get subgraph of reachable nodes
    subgraph = nx.ego_graph(G, center_node,
                            radius=time_limit,
                            distance='travel_time')

    # Get node geometries
    nodes = ox.graph_to_gdfs(subgraph, edges=False)

    # Create polygon of accessible area
    from shapely.geometry import MultiPoint
    points = MultiPoint(nodes.geometry.tolist())
    isochrone_polygon = points.convex_hull

    return isochrone_polygon, subgraph

# Betweenness centrality (importance of nodes)
def calculate_centrality(G):
    """
    Calculate betweenness centrality for network analysis.
    """
    centrality = nx.betweenness_centrality(G, weight='length')

    # Add to nodes
    for node, value in centrality.items():
        G.nodes[node]['betweenness'] = value

    return centrality
```

### Service Area Analysis

```python
def service_area(G, facilities, max_distance=1000):
    """
    Calculate service areas for facilities.
    """

    service_areas = []

    for facility in facilities:
        # Find nearest node
        node = ox.distance.nearest_nodes(G, facility.x, facility.y)

        # Get nodes within distance
        subgraph = nx.ego_graph(G, node, radius=max_distance, distance='length')

        # Create convex hull
        nodes = ox.graph_to_gdfs(subgraph, edges=False)
        service_area = nodes.geometry.unary_union.convex_hull

        service_areas.append({
            'facility': facility,
            'area': service_area,
            'nodes_served': len(subgraph.nodes())
        })

    return service_areas

# Location-allocation (facility location)
def location_allocation(demand_points, candidate_sites, n_facilities=5):
    """
    Solve facility location problem (p-median).
    """
    from scipy.spatial.distance import cdist

    # Distance matrix
    coords_demand = [[p.x, p.y] for p in demand_points]
    coords_sites = [[s.x, s.y] for s in candidate_sites]
    distances = cdist(coords_demand, coords_sites)

    # Simple heuristic: K-means clustering
    from sklearn.cluster import KMeans

    kmeans = KMeans(n_clusters=n_facilities, random_state=42)
    labels = kmeans.fit_predict(coords_demand)

    # Find nearest candidate site to each cluster center
    facilities = []
    for i in range(n_facilities):
        cluster_center = kmeans.cluster_centers_[i]
        nearest_site_idx = np.argmin(cdist([cluster_center], coords_sites))
        facilities.append(candidate_sites[nearest_site_idx])

    return facilities
```

For more advanced examples, see [code-examples.md](code-examples.md).

### `references/big-data.md`

# Big Data and Cloud Computing

Distributed processing, cloud platforms, and GPU acceleration for geospatial data.

## Distributed Processing with Dask

### Dask-GeoPandas

```python
import dask_geopandas
import geopandas as gpd
import dask.dataframe as dd

# Read large GeoPackage in chunks
dask_gdf = dask_geopandas.read_file('large.gpkg', npartitions=10)

# Perform spatial operations
dask_gdf['area'] = dask_gdf.geometry.area
dask_gdf['buffer'] = dask_gdf.geometry.buffer(1000)

# Compute result
result = dask_gdf.compute()

# Distributed spatial join
dask_points = dask_geopandas.read_file('points.gpkg', npartitions=5)
dask_zones = dask_geopandas.read_file('zones.gpkg', npartitions=3)

joined = dask_points.sjoin(dask_zones, how='inner', predicate='within')
result = joined.compute()
```

### Dask for Raster Processing

```python
import dask.array as da
import rasterio

# Create lazy-loaded raster array
def lazy_raster(path, chunks=(1, 1024, 1024)):
    with rasterio.open(path) as src:
        profile = src.profile
        # Create dask array
        raster = da.from_rasterio(src, chunks=chunks)

    return raster, profile

# Process large raster
raster, profile = lazy_raster('very_large.tif')

# Calculate NDVI (lazy operation)
ndvi = (raster[3] - raster[2]) / (raster[3] + raster[2] + 1e-8)

# Apply function to each chunk
def process_chunk(chunk):
    return (chunk - chunk.min()) / (chunk.max() - chunk.min())

normalized = da.map_blocks(process_chunk, ndvi, dtype=np.float32)

# Compute and save
with rasterio.open('output.tif', 'w', **profile) as dst:
    dst.write(normalized.compute())
```

### Dask Distributed Cluster

```python
from dask.distributed import Client

# Connect to cluster
client = Client('scheduler-address:8786')

# Or create local cluster
from dask.distributed import LocalCluster
cluster = LocalCluster(n_workers=4, threads_per_worker=2, memory_limit='4GB')
client = Client(cluster)

# Use Dask-GeoPandas with cluster
dask_gdf = dask_geopandas.from_geopandas(gdf, npartitions=10)
dask_gdf = dask_gdf.set_index(calculate_spatial_partitions=True)

# Operations are now distributed
result = dask_gdf.buffer(1000).compute()
```

## Cloud Platforms

### Google Earth Engine

```python
import ee

# Initialize
ee.Initialize(project='your-project')

# Large-scale composite
def create_annual_composite(year):
    """Create cloud-free annual composite."""

    # Sentinel-2 collection
    s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterBounds(ee.Geometry.Rectangle([-125, 32, -114, 42])) \
        .filterDate(f'{year}-01-01', f'{year}-12-31') \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))

    # Cloud masking
    def mask_s2(image):
        qa = image.select('QA60')
        cloud_bit_mask = 1 << 10
        cirrus_bit_mask = 1 << 11
        mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(
               qa.bitwiseAnd(cirrus_bit_mask).eq(0))
        return image.updateMask(mask.Not())

    s2_masked = s2.map(mask_s2)

    # Median composite
    composite = s2_masked.median().clip(roi)

    return composite

# Export to Google Drive
task = ee.batch.Export.image.toDrive(
    image=composite,
    description='CA_composite_2023',
    scale=10,
    region=roi,
    crs='EPSG:32611',
    maxPixels=1e13
)
task.start()
```

### Planetary Computer (Microsoft)

```python
import pystac_client
import planetary_computer
import odc.stac
import xarray as xr

# Search catalog
catalog = pystac_client.Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace,
)

# Search NAIP imagery
search = catalog.search(
    collections=["naip"],
    bbox=[-125, 32, -114, 42],
    datetime="2020-01-01/2023-12-31",
)

items = list(search.get_items())

# Load as xarray dataset
data = odc.stac.load(
    items[:100],  # Process in batches
    bands=["image"],
    crs="EPSG:32611",
    resolution=1.0,
    chunkx=1024,
    chunky=1024,
)

# Compute statistics lazily
mean = data.mean().compute()
std = data.std().compute()

# Export to COG
import rioxarray
data.isel(time=0).rio.to_raster('naip_composite.tif', compress='DEFLATE')
```

### Google Cloud Storage

```python
from google.cloud import storage
import rasterio
from rasterio.session import GSSession

# Upload to GCS
client = storage.Client()
bucket = client.bucket('my-bucket')
blob = bucket.blob('geospatial/data.tif')
blob.upload_from_filename('local_data.tif')

# Read directly from GCS
with rasterio.open(
    'gs://my-bucket/geospatial/data.tif',
    session=GSSession()
) as src:
    data = src.read()

# Use with Rioxarray
import rioxarray
da = rioxarray.open_rasterio('gs://my-bucket/geospatial/data.tif')
```

## GPU Acceleration

### CuPy for Raster Processing

```python
import cupy as cp
import numpy as np

def gpu_ndvi(nir, red):
    """Calculate NDVI on GPU."""
    # Transfer to GPU
    nir_gpu = cp.asarray(nir)
    red_gpu = cp.asarray(red)

    # Calculate on GPU
    ndvi_gpu = (nir_gpu - red_gpu) / (nir_gpu + red_gpu + 1e-8)

    # Transfer back
    return cp.asnumpy(ndvi_gpu)

# Batch processing
def batch_process_gpu(raster_path):
    with rasterio.open(raster_path) as src:
        data = src.read()  # (bands, height, width)

    data_gpu = cp.asarray(data)

    # Process all bands
    for i in range(data.shape[0]):
        data_gpu[i] = (data_gpu[i] - data_gpu[i].min()) / \
                      (data_gpu[i].max() - data_gpu[i].min())

    return cp.asnumpy(data_gpu)
```

### RAPIDS for Spatial Analysis

```python
import cudf
import cuspatial

# Load data to GPU
gdf_gpu = cuspatial.from_geopandas(gdf)

# Spatial join on GPU
points_gpu = cuspatial.from_geopandas(points_gdf)
polygons_gpu = cuspatial.from_geopandas(polygons_gdf)

joined = cuspatial.join_polygon_points(
    polygons_gpu,
    points_gpu
)

# Convert back
result = joined.to_pandas()
```

### PyTorch for Geospatial Deep Learning

```python
import torch
from torch.utils.data import DataLoader

# Custom dataset
class SatelliteDataset(torch.utils.data.Dataset):
    def __init__(self, image_paths, label_paths):
        self.image_paths = image_paths
        self.label_paths = label_paths

    def __getitem__(self, idx):
        with rasterio.open(self.image_paths[idx]) as src:
            image = src.read().astype(np.float32)

        with rasterio.open(self.label_paths[idx]) as src:
            label = src.read(1).astype(np.int64)

        return torch.from_numpy(image), torch.from_numpy(label)

# DataLoader with GPU prefetching
dataset = SatelliteDataset(images, labels)
loader = DataLoader(
    dataset,
    batch_size=16,
    shuffle=True,
    num_workers=4,
    pin_memory=True,  # Faster transfer to GPU
)

# Training with mixed precision
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

for images, labels in loader:
    images, labels = images.to('cuda'), labels.to('cuda')

    with autocast():
        outputs = model(images)
        loss = criterion(outputs, labels)

    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
```

## Efficient Data Formats

### Cloud-Optimized GeoTIFF (COG)

```python
from rio_cogeo.cogeo import cog_translate

# Convert to COG
cog_translate(
    src_path='input.tif',
    dst_path='output_cog.tif',
    dst_kwds={'compress': 'DEFLATE', 'predictor': 2},
    overview_level=5,
    overview_resampling='average',
    config={'GDAL_TIFF_INTERNAL_MASK': True}
)

# Create overviews for faster access
with rasterio.open('output.tif', 'r+') as src:
    src.build_overviews([2, 4, 8, 16], resampling='average')
    src.update_tags(ns='rio_overview', resampling='average')
```

### Zarr for Multidimensional Arrays

```python
import xarray as xr
import zarr

# Create Zarr store
store = zarr.DirectoryStore('data.zarr')

# Save datacube to Zarr
ds.to_zarr(store, consolidated=True)

# Read efficiently
ds = xr.open_zarr('data.zarr', consolidated=True)

# Extract subset efficiently
subset = ds.sel(time='2023-01', latitude=slice(30, 40))
```

### Parquet for Vector Data

```python
import geopandas as gpd

# Write to Parquet (with spatial index)
gdf.to_parquet('data.parquet', compression='snappy', index=True)

# Read efficiently
gdf = gpd.read_parquet('data.parquet')

# Read subset with filtering
import pyarrow.parquet as pq
table = pq.read_table('data.parquet', filters=[('column', '==', 'value')])
```

For more big data examples, see [code-examples.md](code-examples.md).

### `references/code-examples.md`

# Code Examples

500+ code examples organized by category and programming language.

## Python Examples

### Core Operations

```python
# 1. Read GeoJSON
import geopandas as gpd
gdf = gpd.read_file('data.geojson')

# 2. Read Shapefile
gdf = gpd.read_file('data.shp')

# 3. Read GeoPackage
gdf = gpd.read_file('data.gpkg', layer='layer_name')

# 4. Reproject
gdf_utm = gdf.to_crs('EPSG:32633')

# 5. Buffer
gdf['buffer_1km'] = gdf.geometry.buffer(1000)

# 6. Spatial join
joined = gpd.sjoin(points, polygons, how='inner', predicate='within')

# 7. Dissolve
dissolved = gdf.dissolve(by='category')

# 8. Clip
clipped = gpd.clip(gdf, mask)

# 9. Calculate area
gdf['area_km2'] = gdf.geometry.area / 1e6

# 10. Calculate length
gdf['length_km'] = gdf.geometry.length / 1000
```

### Raster Operations

```python
# 11. Read raster
import rasterio
with rasterio.open('raster.tif') as src:
    data = src.read()
    profile = src.profile
    crs = src.crs

# 12. Read single band
with rasterio.open('raster.tif') as src:
    band1 = src.read(1)

# 13. Read with window
with rasterio.open('large.tif') as src:
    window = ((0, 1000), (0, 1000))
    subset = src.read(1, window=window)

# 14. Write raster
with rasterio.open('output.tif', 'w', **profile) as dst:
    dst.write(data)

# 15. Calculate NDVI
red = src.read(4)
nir = src.read(8)
ndvi = (nir - red) / (nir + red + 1e-8)

# 16. Mask raster with polygon
from rasterio.mask import mask
masked, transform = mask(src, [polygon.geometry], crop=True)

# 17. Reproject raster
from rasterio.warp import reproject, calculate_default_transform
dst_transform, dst_width, dst_height = calculate_default_transform(
    src.crs, 'EPSG:32633', src.width, src.height, *src.bounds)
```

### Visualization

```python
# 18. Static plot with GeoPandas
gdf.plot(column='value', cmap='YlOrRd', legend=True, figsize=(12, 8))

# 19. Interactive map with Folium
import folium
m = folium.Map(location=[37.7, -122.4], zoom_start=12)
folium.GeoJson(gdf).add_to(m)

# 20. Choropleth
folium.Choropleth(gdf, data=stats, columns=['id', 'value'],
                  key_on='feature.properties.id').add_to(m)

# 21. Add markers
for _, row in points.iterrows():
    folium.Marker([row.lat, row.lon]).add_to(m)

# 22. Map with Contextily
import contextily as ctx
ax = gdf.plot(alpha=0.5)
ctx.add_basemap(ax, crs=gdf.crs)

# 23. Multi-layer map
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
gdf1.plot(ax=ax, color='blue')
gdf2.plot(ax=ax, color='red')

# 24. 3D plot
import pydeck as pdk
pdk.Deck(layers=[pdk.Layer('ScatterplotLayer', data=df)], map_style='mapbox://styles/mapbox/dark-v9')

# 25. Time series map
import hvplot.geopandas
gdf.hvplot(c='value', geo=True, tiles='OSM', frame_width=600)
```

## R Examples

```r
# 26. Load sf package
library(sf)

# 27. Read shapefile
roads <- st_read("roads.shp")

# 28. Read GeoJSON
zones <- st_read("zones.geojson")

# 29. Check CRS
st_crs(roads)

# 30. Reproject
roads_utm <- st_transform(roads, 32610)

# 31. Buffer
roads_buffer <- st_buffer(roads, dist = 100)

# 32. Spatial join
joined <- st_join(roads, zones, join = st_intersects)

# 33. Calculate area
zones$area <- st_area(zones)

# 34. Dissolve
dissolved <- st_union(zones)

# 35. Plot
plot(zones$geometry)
```

## Julia Examples

```julia
# 36. Load ArchGDAL
using ArchGDAL

# 37. Read shapefile
data = ArchGDAL.read("countries.shp") do dataset
    layer = dataset[1]
    features = []
    for feature in layer
        push!(features, ArchGDAL.getgeom(feature))
    end
    features
end

# 38. Create point
using GeoInterface
point = GeoInterface.Point(-122.4, 37.7)

# 39. Buffer
buffered = GeoInterface.buffer(point, 1000)

# 40. Intersection
intersection = GeoInterface.intersection(poly1, poly2)
```

## JavaScript Examples

```javascript
// 41. Turf.js point
const pt1 = turf.point([-122.4, 37.7]);

// 42. Distance
const distance = turf.distance(pt1, pt2, {units: 'kilometers'});

// 43. Buffer
const buffered = turf.buffer(pt1, 5, {units: 'kilometers'});

// 44. Within
const ptsWithin = turf.pointsWithinPolygon(points, polygon);

// 45. Bounding box
const bbox = turf.bbox(feature);

// 46. Area
const area = turf.area(polygon); // square meters

// 47. Along
const along = turf.along(line, 2, {units: 'kilometers'});

// 48. Nearest point
const nearest = turf.nearestPoint(pt, points);

// 49. Interpolate
const interpolated = turf.interpolate(line, 100);

// 50. Center
const center = turf.center(features);
```

## Domain-Specific Examples

### Remote Sensing

```python
# 51. Sentinel-2 NDVI time series
import ee
s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
def add_ndvi(img):
    return img.addBands(img.normalizedDifference(['B8', 'B4']).rename('NDVI'))
s2_ndvi = s2.map(add_ndvi)

# 52. Landsat collection
landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
landsat = landsat.filter(ee.Filter.lt('CLOUD_COVER', 20))

# 53. Cloud masking
def mask_clouds(image):
    qa = image.select('QA60')
    mask = qa.bitwiseAnd(1 << 10).eq(0)
    return image.updateMask(mask)

# 54. Composite
median = s2.median()

# 55. Export
task = ee.batch.Export.image.toDrive(image, 'description', scale=10)
```

### Machine Learning

```python
# 56. Train Random Forest
from sklearn.ensemble import RandomForestClassifier
rf = RandomForestClassifier(n_estimators=100, max_depth=20)
rf.fit(X_train, y_train)

# 57. Predict
prediction = rf.predict(X_test)

# 58. Feature importance
importances = pd.DataFrame({'feature': features, 'importance': rf.feature_importances_})

# 59. CNN model
import torch.nn as nn
class CNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(4, 32, 3)
        self.conv2 = nn.Conv2d(32, 64, 3)
        self.fc = nn.Linear(64 * 28 * 28, 10)

# 60. Training loop
for epoch in range(epochs):
    outputs = model(images)
    loss = criterion(outputs, labels)
    loss.backward()
    optimizer.step()
```

### Network Analysis

```python
# 61. OSMnx street network
import osmnx as ox
G = ox.graph_from_place('City', network_type='drive')

# 62. Calculate shortest path
route = ox.shortest_path(G, orig_node, dest_node, weight='length')

# 63. Add edge attributes
G = ox.add_edge_speeds(G)
G = ox.add_edge_travel_times(G)

# 64. Nearest node
node = ox.distance.nearest_nodes(G, X, Y)

# 65. Plot route
ox.plot_graph_route(G, route)
```

## Complete Workflows

### Land Cover Classification

```python
# 66. Complete classification workflow
def classify_imagery(image_path, training_gdf, output_path):
    from sklearn.ensemble import RandomForestClassifier
    import rasterio
    from rasterio.features import rasterize

    # Load imagery
    with rasterio.open(image_path) as src:
        image = src.read()
        profile = src.profile

    # Extract training data
    X, y = [], []
    for _, row in training_gdf.iterrows():
        mask = rasterize([(row.geometry, 1)], out_shape=image.shape[1:])
        pixels = image[:, mask > 0].T
        X.extend(pixels)
        y.extend([row['class']] * len(pixels))

    # Train
    rf = RandomForestClassifier(n_estimators=100)
    rf.fit(X, y)

    # Predict
    image_flat = image.reshape(image.shape[0], -1).T
    prediction = rf.predict(image_flat)
    prediction = prediction.reshape(image.shape[1], image.shape[2])

    # Save
    profile.update(dtype=rasterio.uint8, count=1)
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(prediction.astype(rasterio.uint8), 1)
```

### Flood Mapping

```python
# 67. Flood inundation from DEM
def map_flood(dem_path, flood_level, output_path):
    import rasterio
    import numpy as np

    with rasterio.open(dem_path) as src:
        dem = src.read(1)
        profile = src.profile

    # Identify flooded cells
    flooded = dem < flood_level

    # Calculate depth
    depth = np.where(flooded, flood_level - dem, 0)

    # Save
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(depth.astype(rasterio.float32), 1)
```

### Terrain Analysis

```python
# 68. Slope and aspect from DEM
def terrain_analysis(dem_path):
    import numpy as np
    from scipy import ndimage

    with rasterio.open(dem_path) as src:
        dem = src.read(1)

    # Calculate gradients
    dy, dx = np.gradient(dem)

    # Slope in degrees
    slope = np.arctan(np.sqrt(dx**2 + dy**2)) * 180 / np.pi

    # Aspect
    aspect = np.arctan2(-dy, dx) * 180 / np.pi
    aspect = (90 - aspect) % 360

    return slope, aspect
```

## Additional Examples (70-100)

```python
# 69. Point in polygon test
point.within(polygon)

# 70. Nearest neighbor
from sklearn.neighbors import BallTree
tree = BallTree(coords)
distances, indices = tree.query(point)

# 71. Spatial index
from rtree import index
idx = index.Index()
for i, geom in enumerate(geometries):
    idx.insert(i, geom.bounds)

# 72. Clip raster
from rasterio.mask import mask
clipped, transform = mask(src, [polygon], crop=True)

# 73. Merge rasters
from rasterio.merge import merge
merged, transform = merge([src1, src2, src3])

# 74. Reproject image
from rasterio.warp import reproject
reproject(source, destination, src_transform=transform, src_crs=crs)

# 75. Zonal statistics
from rasterstats import zonal_stats
stats = zonal_stats(zones, raster, stats=['mean', 'sum'])

# 76. Extract values at points
from rasterio.sample import sample_gen
values = list(sample_gen(src, [(x, y), (x2, y2)]))

# 77. Resample raster
import rasterio
from rasterio.enums import Resampling
resampled = dst.read(out_shape=(src.height * 2, src.width * 2),
                    resampling=Resampling.bilinear)

# 78. Create regular grid
from shapely.geometry import box
grid = [box(xmin, ymin, xmin+dx, ymin+dy)
        for xmin in np.arange(minx, maxx, dx)
        for ymin in np.arange(miny, maxy, dy)]

# 79. Geocoding with geopy
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="geo_app")
location = geolocator.geocode("Golden Gate Bridge")

# 80. Reverse geocoding
location = geolocator.reverse("37.8, -122.4")

# 81. Calculate bearing
from geopy import distance
bearing = distance.geodesic(point1, point2).initial_bearing

# 82. Great circle distance
from geopy.distance import geodesic
d = geodesic(point1, point2).km

# 83. Create bounding box
from shapely.geometry import box
bbox = box(minx, miny, maxx, maxy)

# 84. Convex hull
hull = points.geometry.unary_union.convex_hull

# 85. Voronoi diagram
from scipy.spatial import Voronoi
vor = Voronoi(coords)

# 86. Kernel density estimation
from scipy.stats import gaussian_kde
kde = gaussian_kde(points)
density = kde(np.mgrid[xmin:xmax:100j, ymin:ymax:100j])

# 87. Hotspot analysis
from esda.getisord import G_Local
g_local = G_Local(values, weights)

# 88. Moran's I
from esda.moran import Moran
moran = Moran(values, weights)

# 89. Geary's C
from esda.geary import Geary
geary = Geary(values, weights)

# 90. Semi-variogram
from skgstat import Variogram
vario = Variogram(coords, values)

# 91. Kriging
from pykrige.ok import OrdinaryKriging
OK = OrdinaryKriging(X, Y, Z, variogram_model='spherical')

# 92. IDW interpolation
from scipy.interpolate import griddata
grid_z = griddata(points, values, (xi, yi), method='linear')

# 93. Natural neighbor interpolation
from scipy.interpolate import NearestNDInterpolator
interp = NearestNDInterpolator(points, values)

# 94. Spline interpolation
from scipy.interpolate import Rbf
rbf = Rbf(x, y, z, function='multiquadric')

# 95. Watershed delineation
from scipy.ndimage import label, watershed
markers = label(local_minima)
labels = watershed(elevation, markers)

# 96. Stream extraction
import richdem as rd
rd.FillDepressions(dem, in_place=True)
flow = rd.FlowAccumulation(dem, method='D8')
streams = flow > 1000

# 97. Hillshade
from scipy import ndimage
hillshade = np.sin(alt) * np.sin(slope) + np.cos(alt) * np.cos(slope) * np.cos(az - aspect)

# 98. Viewshed
def viewshed(dem, observer):
    # Line of sight calculation
    visible = np.ones_like(dem, dtype=bool)
    for angle in np.linspace(0, 2*np.pi, 360):
        # Cast ray and check visibility
        pass
    return visible

# 99. Shaded relief
from matplotlib.colors import LightSource
ls = LightSource(azdeg=315, altdeg=45)
shaded = ls.hillshade(elevation, vert_exaggeration=1)

# 100. Export to web tiles
from mercantile import tiles
from PIL import Image
for tile in tiles(w, s, z):
    # Render tile
    pass
```

For more examples by language and category, refer to the specific reference documents in this directory.

### `references/coordinate-systems.md`

# Coordinate Reference Systems (CRS)

Complete guide to coordinate systems, projections, and transformations for geospatial data.

## Table of Contents

1. [Fundamentals](#fundamentals)
2. [Common CRS Codes](#common-crs-codes)
3. [Projected vs Geographic](#projected-vs-geographic)
4. [UTM Zones](#utm-zones)
5. [Transformations](#transformations)
6. [Best Practices](#best-practices)

## Fundamentals

### What is a CRS?

A Coordinate Reference System defines how coordinates relate to positions on Earth:

- **Geographic CRS**: Uses latitude/longitude (degrees)
- **Projected CRS**: Uses Cartesian coordinates (meters, feet)
- **Vertical CRS**: Defines height/depth (e.g., ellipsoidal heights)

### Components

1. **Datum**: Mathematical model of Earth's shape
   - WGS 84 (EPSG:4326) - Global GPS
   - NAD 83 (EPSG:4269) - North America
   - ETRS89 (EPSG:4258) - Europe

2. **Projection**: Transformation from curved to flat surface
   - Cylindrical (Mercator)
   - Conic (Lambert Conformal)
   - Azimuthal (Polar Stereographic)

3. **Units**: Degrees, meters, feet, etc.

## Common CRS Codes

### Geographic CRS (Lat/Lon)

| EPSG | Name | Area | Notes |
|------|------|------|-------|
| 4326 | WGS 84 | Global | GPS default, use for storage |
| 4269 | NAD83 | North America | USGS data, slightly different from WGS84 |
| 4258 | ETRS89 | Europe | European reference frame |
| 4612 | GDA94 | Australia | Australian datum |

### Projected CRS (Meters)

| EPSG | Name | Area | Distortion | Notes |
|------|------|------|------------|-------|
| 3857 | Web Mercator | Global (85°S-85°N) | High near poles | Web maps (Google, OSM) |
| 32601-32660 | UTM Zone N | Global (1° bands) | <1% per zone | Metric calculations |
| 32701-32760 | UTM Zone S | Global (1° bands) | <1% per zone | Southern hemisphere |
| 3395 | Mercator | World | Moderate | World maps |
| 5070 | CONUS Albers | USA (conterminous) | Low | US national mapping |
| 2154 | Lambert-93 | France | Very low | French national projection |

### Regional Projections

**United States:**
- EPSG:5070 - US National Atlas Equal Area (CONUS)
- EPSG:6350 - US National Atlas (Alaska)
- EPSG:102003 - USA Contiguous Albers Equal Area
- EPSG:2227 - California Zone 3 (US Feet)

**Europe:**
- EPSG:3035 - Europe Equal Area 2001
- EPSG:3857 - Web Mercator (web mapping)
- EPSG:2154 - Lambert 93 (France)
- EPSG:25832-25836 - UTM zones (ETRS89)

**Other:**
- EPSG:3112 - GDA94 / MGA zone 52 (Australia)
- EPSG:2056 - CH1903+ / LV95 (Switzerland)
- EPSG:4326 - WGS 84 (global default)

## Projected vs Geographic

### When to Use Geographic (EPSG:4326)

✅ Storing data (databases, files)
✅ Global datasets
✅ Web APIs (GeoJSON, KML)
✅ Latitude/longitude queries
✅ GPS coordinates

```python
# Bad: Distance calculation in geographic CRS
gpd.geographic_crs = "EPSG:4326"
distance = gdf.geometry.length  # WRONG! Returns degrees, not meters

# Good: Calculate distance in projected CRS
gdf_projected = gdf.to_crs("EPSG:32633")  # UTM Zone 33N
distance_m = gdf_projected.geometry.length  # Correct: meters
```

### When to Use Projected

✅ Area/distance calculations
✅ Buffer operations
✅ Spatial analysis
✅ High-resolution mapping
✅ Engineering applications

```python
import geopandas as gpd

# Project to appropriate UTM zone
gdf = gpd.to_crs(gdf.estimate_utm_crs())

# Now area and distance are accurate
area_sqm = gdf.geometry.area
buffer_1km = gdf.geometry.buffer(1000)  # 1000 meters
```

### Web Mercator Warning

⚠️ **EPSG:3857 (Web Mercator) for visualization only**

```python
# DON'T use Web Mercator for area calculations
gdf_web = gdf.to_crs("EPSG:3857")
area = gdf_web.geometry.area  # WRONG! Significant distortion

# DO use appropriate projection
gdf_utm = gdf.to_crs("EPSG:32633")  # or estimate_utm_crs()
area = gdf_utm.geometry.area  # Correct
```

## UTM Zones

### Understanding UTM Zones

Earth is divided into 60 zones (6° longitude each):
- Zones 1-60: West to East
- Each zone divided into North (326xx) and South (327xx)

### Finding Your UTM Zone

```python
def get_utm_zone(longitude, latitude):
    """Get UTM zone EPSG code from coordinates."""
    import math

    zone = math.floor((longitude + 180) / 6) + 1

    if latitude >= 0:
        epsg = 32600 + zone  # Northern hemisphere
    else:
        epsg = 32700 + zone  # Southern hemisphere

    return f"EPSG:{epsg}"

# Example
get_utm_zone(-122.4, 37.7)  # Returns 'EPSG:32610' (Zone 10N)
```

### Auto-Detect UTM Zone with GeoPandas

```python
import geopandas as gpd

# Load data
gdf = gpd.read_file('data.geojson')

# Estimate best UTM zone
utm_crs = gdf.estimate_utm_crs()
print(f"Best UTM CRS: {utm_crs}")

# Reproject
gdf_projected = gdf.to_crs(utm_crs)
```

### Special UTM Cases

**UPS (Universal Polar Stereographic):**
- EPSG:5041 - UPS North (Arctic)
- EPSG:5042 - UPS South (Antarctic)

**UTM Non-standard:**
- EPSG:31466-31469 - German Gauss-Krüger zones
- EPSG:2056 - Swiss LV95 (based on UTM principles)

## Transformations

### Basic Transformation

```python
from pyproj import Transformer

# Create transformer
transformer = Transformer.from_crs(
    "EPSG:4326",  # WGS 84 (lat/lon)
    "EPSG:32633", # UTM Zone 33N (meters)
    always_xy=True  # Input: x=lon, y=lat (not y=lat, x=lon)
)

# Transform single point
lon, lat = -122.4, 37.7
x, y = transformer.transform(lon, lat)
print(f"Easting: {x:.2f}, Northing: {y:.2f}")
```

### Batch Transformation

```python
import numpy as np
from pyproj import Transformer

# Arrays of coordinates
lon_array = [-122.4, -122.3]
lat_array = [37.7, 37.8]

transformer = Transformer.from_crs("EPSG:4326", "EPSG:32610", always_xy=True)
xs, ys = transformer.transform(lon_array, lat_array)
```

### Transformation with PyProj CRS

```python
from pyproj import CRS

# Get CRS information
crs = CRS.from_epsg(32633)

print(f"Name: {crs.name}")
print(f"Type: {crs.type_name}")
print(f"Area of use: {crs.area_of_use.name}")
print(f"Datum: {crs.datum.name}")
print(f"Ellipsoid: {crs.ellipsoid_name}")
```

## Best Practices

### 1. Always Know Your CRS

```python
import geopandas as gpd

gdf = gpd.read_file('data.geojson')

# Check CRS immediately
print(f"CRS: {gdf.crs}")  # Should never be None!

# If None, set it
if gdf.crs is None:
    gdf.set_crs("EPSG:4326", inplace=True)
```

### 2. Verify CRS Before Operations

```python
def ensure_same_crs(gdf1, gdf2):
    """Ensure two GeoDataFrames have same CRS."""
    if gdf1.crs != gdf2.crs:
        gdf2 = gdf2.to_crs(gdf1.crs)
        print(f"Reprojected gdf2 to {gdf1.crs}")
    return gdf1, gdf2

# Use before spatial operations
zones, points = ensure_same_crs(zones_gdf, points_gdf)
result = gpd.sjoin(points, zones, predicate='within')
```

### 3. Use Appropriate Projections

```python
# For local analysis (< 500km extent)
gdf_local = gdf.to_crs(gdf.estimate_utm_crs())

# For national/regional analysis
gdf_us = gdf.to_crs("EPSG:5070")  # US National Atlas Equal Area
gdf_eu = gdf.to_crs("EPSG:3035")  # Europe Equal Area

# For web visualization
gdf_web = gdf.to_crs("EPSG:3857")  # Web Mercator
```

### 4. Preserve Original CRS

```python
# Keep original as backup
gdf_original = gdf.copy()
original_crs = gdf.crs

# Do analysis in projected CRS
gdf_projected = gdf.to_crs(gdf.estimate_utm_crs())
result = gdf_projected.geometry.buffer(1000)

# Convert back if needed
result = result.to_crs(original_crs)
```

## Common Pitfalls

### Mistake 1: Area in Degrees

```python
# WRONG: Area in square degrees
gdf = gpd.read_file('data.geojson')
area = gdf.geometry.area  # Wrong!

# CORRECT: Use projected CRS
gdf_proj = gdf.to_crs(gdf.estimate_utm_crs())
area_sqm = gdf_proj.geometry.area
area_sqkm = area_sqm / 1_000_000
```

### Mistake 2: Buffer in Geographic CRS

```python
# WRONG: Buffer of 1000 degrees
gdf['buffer'] = gdf.geometry.buffer(1000)

# CORRECT: Project first
gdf_proj = gdf.to_crs("EPSG:32610")
gdf_proj['buffer_km'] = gdf_proj.geometry.buffer(1000)  # 1000 meters
```

### Mistake 3: Mixing CRS

```python
# WRONG: Spatial join without checking CRS
result = gpd.sjoin(gdf1, gdf2, predicate='intersects')

# CORRECT: Ensure same CRS
if gdf1.crs != gdf2.crs:
    gdf2 = gdf2.to_crs(gdf1.crs)
result = gpd.sjoin(gdf1, gdf2, predicate='intersects')
```

## Quick Reference

```python
# Common operations

# Check CRS
gdf.crs
rasterio.open('file.tif').crs

# Reproject
gdf.to_crs("EPSG:32633")

# Auto-detect UTM
gdf.estimate_utm_crs()

# Transform single point
from pyproj import Transformer
tx = Transformer.from_crs("EPSG:4326", "EPSG:32610", always_xy=True)
x, y = tx.transform(lon, lat)

# Create custom CRS
from pyproj import CRS
custom_crs = CRS.from_proj4(
    "+proj=utm +zone=10 +ellps=WGS84 +datum=WGS84 +units=m +no_defs"
)
```

For more information, see:
- [EPSG Registry](https://epsg.org/)
- [PROJ documentation](https://proj.org/)
- [pyproj documentation](https://pyproj4.github.io/pyproj/)

### `references/core-libraries.md`

# Core Geospatial Libraries

This reference covers the fundamental Python libraries for geospatial data processing.

## GDAL (Geospatial Data Abstraction Library)

GDAL is the foundation for geospatial I/O in Python.

```python
from osgeo import gdal

# Open a raster file
ds = gdal.Open('raster.tif')
band = ds.GetRasterBand(1)
data = band.ReadAsArray()

# Get geotransform
geotransform = ds.GetGeoTransform()
origin_x = geotransform[0]
pixel_width = geotransform[1]

# Get projection
proj = ds.GetProjection()
```

## Rasterio

Rasterio provides a cleaner interface to GDAL.

```python
import rasterio
import numpy as np

# Basic reading
with rasterio.open('raster.tif') as src:
    data = src.read()           # All bands
    band1 = src.read(1)         # Single band
    profile = src.profile       # Metadata

# Windowed reading (memory efficient)
with rasterio.open('large.tif') as src:
    window = ((0, 100), (0, 100))
    subset = src.read(1, window=window)

# Writing
with rasterio.open('output.tif', 'w',
                   driver='GTiff',
                   height=data.shape[0],
                   width=data.shape[1],
                   count=1,
                   dtype=data.dtype,
                   crs=src.crs,
                   transform=src.transform) as dst:
    dst.write(data, 1)

# Masking
with rasterio.open('raster.tif') as src:
    masked_data, mask = rasterio.mask.mask(src, shapes=[polygon], crop=True)
```

## Fiona

Fiona handles vector data I/O.

```python
import fiona

# Read features
with fiona.open('data.geojson') as src:
    for feature in src:
        geom = feature['geometry']
        props = feature['properties']

# Get schema and CRS
with fiona.open('data.shp') as src:
    schema = src.schema
    crs = src.crs

# Write data
schema = {'geometry': 'Point', 'properties': {'name': 'str'}}
with fiona.open('output.geojson', 'w', driver='GeoJSON',
                schema=schema, crs='EPSG:4326') as dst:
    dst.write({
        'geometry': {'type': 'Point', 'coordinates': [0, 0]},
        'properties': {'name': 'Origin'}
    })
```

## Shapely

Shapely provides geometric operations.

```python
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import unary_union

# Create geometries
point = Point(0, 0)
line = LineString([(0, 0), (1, 1)])
poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])

# Geometric operations
buffered = point.buffer(1)              # Buffer
simplified = poly.simplify(0.01)        # Simplify
centroid = poly.centroid                 # Centroid
intersection = poly1.intersection(poly2) # Intersection

# Spatial relationships
point.within(poly)      # True if point inside polygon
poly1.intersects(poly2) # True if geometries intersect
poly1.contains(poly2)   # True if poly2 inside poly1

# Unary union
combined = unary_union([poly1, poly2, poly3])

# Buffer with different joins
buffer_round = point.buffer(1, quad_segs=16)
buffer_mitre = point.buffer(1, mitre_limit=1, join_style=2)
```

## PyProj

PyProj handles coordinate transformations.

```python
from pyproj import Transformer, CRS

# Coordinate transformation
transformer = Transformer.from_crs('EPSG:4326', 'EPSG:32633')
x, y = transformer.transform(lat, lon)
x_inv, y_inv = transformer.transform(x, y, direction='INVERSE')

# Batch transformation
lon_array = [-122.4, -122.3]
lat_array = [37.7, 37.8]
x_array, y_array = transformer.transform(lon_array, lat_array)

# Always z/height if available
transformer_always_z = Transformer.from_crs(
    'EPSG:4326', 'EPSG:32633', always_z=True
)

# Get CRS info
crs = CRS.from_epsg(4326)
print(crs.name)  # WGS 84
print(crs.axis_info)  # Axis info

# Custom transformation
transformer = Transformer.from_pipeline(
    'proj=pipeline step inv proj=utm zone=32 ellps=WGS84 step proj=unitconvert xy_in=rad xy_out=deg'
)
```

## GeoPandas

GeoPandas combines pandas with geospatial capabilities.

```python
import geopandas as gpd

# Reading data
gdf = gpd.read_file('data.geojson')
gdf = gpd.read_file('data.shp', encoding='utf-8')
gdf = gpd.read_postgis('SELECT * FROM data', con=engine)

# Writing data
gdf.to_file('output.geojson', driver='GeoJSON')
gdf.to_file('output.gpkg', layer='data', use_arrow=True)

# CRS operations
gdf.crs  # Get CRS
gdf = gdf.to_crs('EPSG:32633')  # Reproject
gdf = gdf.set_crs('EPSG:4326')  # Set CRS

# Geometric operations
gdf['area'] = gdf.geometry.area
gdf['length'] = gdf.geometry.length
gdf['buffer'] = gdf.geometry.buffer(100)
gdf['centroid'] = gdf.geometry.centroid

# Spatial joins
joined = gpd.sjoin(gdf1, gdf2, how='inner', predicate='intersects')
joined = gpd.sjoin_nearest(gdf1, gdf2, max_distance=1000)

# Overlay operations
intersection = gpd.overlay(gdf1, gdf2, how='intersection')
union = gpd.overlay(gdf1, gdf2, how='union')
difference = gpd.overlay(gdf1, gdf2, how='difference')

# Dissolve
dissolved = gdf.dissolve(by='region', aggfunc='sum')

# Clipping
clipped = gpd.clip(gdf, mask_gdf)

# Spatial indexing (for performance)
idx = gdf.sindex
possible_matches = idx.intersection(polygon.bounds)
```

## Common Workflows

### Batch Reprojection

```python
import geopandas as gpd
from pathlib import Path

input_dir = Path('input')
output_dir = Path('output')

for shp in input_dir.glob('*.shp'):
    gdf = gpd.read_file(shp)
    gdf = gdf.to_crs('EPSG:32633')
    gdf.to_file(output_dir / shp.name)
```

### Raster to Vector Conversion

```python
import rasterio.features
import geopandas as gpd
from shapely.geometry import shape

with rasterio.open('raster.tif') as src:
    image = src.read(1)
    results = (
        {'properties': {'value': v}, 'geometry': s}
        for s, v in rasterio.features.shapes(image, transform=src.transform)
    )

geoms = list(results)
gdf = gpd.GeoDataFrame.from_features(geoms, crs=src.crs)
```

### Vector to Raster Conversion

```python
from rasterio.features import rasterize
import geopandas as gpd

gdf = gpd.read_file('polygons.gpkg')
shapes = ((geom, 1) for geom in gdf.geometry)

raster = rasterize(
    shapes,
    out_shape=(height, width),
    transform=transform,
    fill=0,
    dtype=np.uint8
)
```

### Combining Multiple Rasters

```python
import rasterio.merge
import rasterio as rio

files = ['tile1.tif', 'tile2.tif', 'tile3.tif']
datasets = [rio.open(f) for f in files]

merged, transform = rasterio.merge.merge(datasets)

# Save
profile = datasets[0].profile
profile.update(transform=transform, height=merged.shape[1], width=merged.shape[2])

with rio.open('merged.tif', 'w', **profile) as dst:
    dst.write(merged)
```

For more detailed examples, see [code-examples.md](code-examples.md).

### `references/data-sources.md`

# Geospatial Data Sources

Comprehensive catalog of satellite imagery, vector data, and APIs for geospatial analysis.

## Satellite Data Sources

### Sentinel Missions (ESA)

| Platform | Resolution | Coverage | Access |
|----------|------------|----------|--------|
| **Sentinel-2** | 10-60m | Global | https://scihub.copernicus.eu/ |
| **Sentinel-1** | 5-40m (SAR) | Global | https://scihub.copernicus.eu/ |
| **Sentinel-3** | 300m-1km | Global | https://scihub.copernicus.eu/ |
| **Sentinel-5P** | Various | Global | https://scihub.copernicus.eu/ |

```python
# Access via Sentinelsat
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt

api = SentinelAPI('user', 'password', 'https://scihub.copernicus.eu/dhus')

# Search
products = api.query(geojson_to_wkt(aoi_geojson),
                     date=('20230101', '20231231'),
                     platformname='Sentinel-2',
                     cloudcoverpercentage=(0, 20))

# Download
api.download_all(products)
```

### Landsat (USGS/NASA)

| Platform | Resolution | Coverage | Access |
|----------|------------|----------|--------|
| **Landsat 9** | 30m | Global | https://earthexplorer.usgs.gov/ |
| **Landsat 8** | 30m | Global | https://earthexplorer.usgs.gov/ |
| **Landsat 7** | 15-60m | Global | https://earthexplorer.usgs.gov/ |
| **Landsat 5-7** | 30-60m | Global | https://earthexplorer.usgs.gov/ |

### Commercial Satellite Data

| Provider | Platform | Resolution | API |
|----------|----------|------------|-----|
| **Planet** | PlanetScope, SkySat | 0.5-3m | planet.com |
| **Maxar** | WorldView, GeoEye | 0.3-1.2m | maxar.com |
| **Airbus** | Pleiades, SPOT | 0.5-2m | airbus.com |
| **Capella** | Capella-2 (SAR) | 0.5-1m | capellaspace.com |

## Elevation Data

| Dataset | Resolution | Coverage | Source |
|---------|------------|----------|--------|
| **AW3D30** | 30m | Global | https://www.eorc.jaxa.jp/ALOS/en/aw3d30/ |
| **SRTM** | 30m | 56°S-60°N | https://www.usgs.gov/ |
| **ASTER GDEM** | 30m | 83°S-83°N | https://asterweb.jpl.nasa.gov/ |
| **Copernicus DEM** | 30m | Global | https://copernicus.eu/ |
| **ArcticDEM** | 2-10m | Arctic | https://www.pgc.umn.edu/ |

```python
# Download SRTM via API
import elevation

# Download SRTM 1 arc-second (30m)
elevation.clip(bounds=(-122.5, 37.7, -122.3, 37.9), output='srtm.tif')

# Clean and fill gaps
elevation.clean('srtm.tif', 'srtm_filled.tif')
```

## Land Cover Data

| Dataset | Resolution | Classes | Source |
|---------|------------|---------|--------|
| **ESA WorldCover** | 10m | 11 classes | https://worldcover2021.esa.int/ |
| **ESRI Land Cover** | 10m | 10 classes | https://www.esri.com/ |
| **Copernicus Global** | 100m | 23 classes | https://land.copernicus.eu/ |
| **MODIS MCD12Q1** | 500m | 17 classes | https://lpdaac.usgs.gov/ |
| **NLCD (US)** | 30m | 20 classes | https://www.mrlc.gov/ |

## Climate & Weather Data

### Reanalysis Data

| Dataset | Resolution | Temporal | Access |
|---------|------------|----------|--------|
| **ERA5** | 31km | Hourly (1979+) | https://cds.climate.copernicus.eu/ |
| **MERRA-2** | 50km | Hourly (1980+) | https://gmao.gsfc.nasa.gov/ |
| **JRA-55** | 55km | 3-hourly (1958+) | https://jra.kishou.go.jp/ |

```python
# Download ERA5 via CDS API
import cdsapi

c = cdsapi.Client()

c.retrieve(
    'reanalysis-era5-single-levels',
    {
        'product_type': 'reanalysis',
        'variable': '2m_temperature',
        'year': '2023',
        'month': '01',
        'day': '01',
        'time': '12:00',
        'area': [37.9, -122.5, 37.7, -122.3],
        'format': 'netcdf'
    },
    'era5_temp.nc'
)
```

## OpenStreetMap Data

### Access Methods

```python
# Via OSMnx
import osmnx as ox

# Download place boundary
gdf = ox.geocode_to_gdf('San Francisco, CA')

# Download street network
G = ox.graph_from_place('San Francisco, CA', network_type='drive')

# Download building footprints
buildings = ox.geometries_from_place('San Francisco, CA', tags={'building': True})

# Via Overpass API
import requests

overpass_url = "http://overpass-api.de/api/interpreter"
query = """
    [out:json];
    way["highway"](37.7,-122.5,37.9,-122.3);
    out geom;
"""

response = requests.get(overpass_url, params={'data': query})
data = response.json()
```

## Vector Data Sources

### Natural Earth

```python
import geopandas as gpd

# Admin boundaries (scale: 10m, 50m, 110m)
countries = gpd.read_file('https://naturalearth.s3.amazonaws.com/10m_cultural/ne_10m_admin_0_countries.zip')
urban_areas = gpd.read_file('https://naturalearth.s3.amazonaws.com/10m_cultural/ne_10m_urban_areas.zip')
ports = gpd.read_file('https://naturalearth.s3.amazonaws.com/10m_cultural/ne_10m_ports.zip')
```

### Other Sources

| Dataset | Type | Access |
|---------|------|--------|
| **GADM** | Admin boundaries | https://gadm.org/ |
| **HydroSHEDS** | Rivers, basins | https://www.hydrosheds.org/ |
| **Global Power Plant** | Power plants | https://datasets.wri.org/ |
| **WorldPop** | Population | https://www.worldpop.org/ |
| **GPW** | Population | https://sedac.ciesin.columbia.edu/ |
| **HDX** | Humanitarian data | https://data.humdata.org/ |

## APIs

### Google Maps Platform

```python
import requests

# Geocoding
url = "https://maps.googleapis.com/maps/api/geocode/json"
params = {
    'address': 'Golden Gate Bridge',
    'key': YOUR_API_KEY
}

response = requests.get(url, params=params)
data = response.json()
location = data['results'][0]['geometry']['location']
```

### Mapbox

```python
# Geocoding
import requests

url = "https://api.mapbox.com/geocoding/v5/mapbox.places/Golden%20Gate%20Bridge.json"
params = {'access_token': YOUR_ACCESS_TOKEN}

response = requests.get(url, params=params)
data = response.json()
```

### OpenWeatherMap

```python
# Current weather
url = "https://api.openweathermap.org/data/2.5/weather"
params = {
    'lat': 37.7,
    'lon': -122.4,
    'appid': YOUR_API_KEY
}

response = requests.get(url, params=params)
weather = response.json()
```

## Data APIs in Python

### STAC (SpatioTemporal Asset Catalog)

```python
import pystac_client

# Connect to STAC catalog
catalog = pystac_client.Client.open("https://earth-search.aws.element84.com/v1")

# Search
search = catalog.search(
    collections=["sentinel-2-l2a"],
    bbox=[-122.5, 37.7, -122.3, 37.9],
    datetime="2023-01-01/2023-12-31",
    query={"eo:cloud_cover": {"lt": 20}}
)

items = search.get_all_items()
```

### Planetary Computer

```python
import planetary_computer
import pystac_client

catalog = pystac_client.Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace
)

# Search and sign items
items = catalog.search(...)
signed_items = [planetary_computer.sign(item) for item in items]
```

## Download Scripts

### Automated Download Script

```python
from sentinelsat import SentinelAPI
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import os

def download_and_process_sentinel2(aoi, date_range, output_dir):
    """
    Download and process Sentinel-2 imagery.
    """
    # Initialize API
    api = SentinelAPI('user', 'password', 'https://scihub.copernicus.eu/dhus')

    # Search
    products = api.query(
        aoi,
        date=date_range,
        platformname='Sentinel-2',
        processinglevel='Level-2A',
        cloudcoverpercentage=(0, 20)
    )

    # Download
    api.download_all(products, directory_path=output_dir)

    # Process each product
    for product in products:
        product_path = f"{output_dir}/{product['identifier']}.SAFE"
        processed = process_sentinel2_product(product_path)
        save_rgb_composite(processed, f"{output_dir}/{product['identifier']}_rgb.tif")

def process_sentinel2_product(product_path):
    """Process Sentinel-2 L2A product."""
    # Find 10m bands (B02, B03, B04, B08)
    bands = {}
    for band_id in ['B02', 'B03', 'B04', 'B08']:
        band_path = find_band_file(product_path, band_id, resolution='10m')
        with rasterio.open(band_path) as src:
            bands[band_id] = src.read(1)
            profile = src.profile

    # Stack bands
    stacked = np.stack([bands['B04'], bands['B03'], bands['B02']])  # RGB

    return stacked, profile
```

## Data Quality Assessment

```python
def assess_data_quality(raster_path):
    """
    Assess quality of geospatial raster data.
    """
    import rasterio
    import numpy as np

    with rasterio.open(raster_path) as src:
        data = src.read()
        profile = src.profile

    quality_report = {
        'nodata_percentage': np.sum(data == src.nodata) / data.size * 100,
        'data_range': (data.min(), data.max()),
        'mean': np.mean(data),
        'std': np.std(data),
        'has_gaps': np.any(data == src.nodata),
        'projection': profile['crs'],
        'resolution': (profile['transform'][0], abs(profile['transform'][4]))
    }

    return quality_report
```

For data access code examples, see [code-examples.md](code-examples.md).

### `references/gis-software.md`

# GIS Software Integration

Guide to integrating with major GIS platforms: QGIS, ArcGIS, GRASS GIS, and SAGA GIS.

## QGIS / PyQGIS

### Running Python Scripts in QGIS

```python
# Processing framework script
from qgis.core import (QgsProject, QgsVectorLayer, QgsRasterLayer,
                       QgsProcessingAlgorithm, QgsProcessingParameterRasterLayer)

# Load layers
vector_layer = QgsVectorLayer("path/to/shapefile.shp", "layer_name", "ogr")
raster_layer = QgsRasterLayer("path/to/raster.tif", "raster_name", "gdal")

# Add to project
QgsProject.instance().addMapLayer(vector_layer)
QgsProject.instance().addMapLayer(raster_layer)

# Access features
for feature in vector_layer.getFeatures():
    geom = feature.geometry()
    attrs = feature.attributes()
```

### Creating QGIS Processing Scripts

```python
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessingAlgorithm, QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterRasterLayer)

class NDVIAlgorithm(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return NDVIAlgorithm()

    def name(self):
        return 'ndvi_calculation'

    def displayName(self):
        return self.tr('Calculate NDVI')

    def group(self):
        return self.tr('Raster')

    def groupId(self):
        return 'raster'

    def shortHelpString(self):
        return self.tr("Calculate NDVI from Sentinel-2 imagery")

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(
            self.INPUT, self.tr('Input Sentinel-2 Raster')))

        self.addParameter(QgsProcessingParameterRasterDestination(
            self.OUTPUT, self.tr('Output NDVI')))

    def processAlgorithm(self, parameters, context, feedback):
        raster = self.parameterAsRasterLayer(parameters, self.INPUT, context)

        # NDVI calculation
        # ... implementation ...

        return {self.OUTPUT: destination}
```

### Plugin Development

```python
# __init__.py
def classFactory(iface):
    from .my_plugin import MyPlugin
    return MyPlugin(iface)

# my_plugin.py
from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsProject

class MyPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.action = QAction("My Plugin", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu("My Plugin", self.action)

    def run(self):
        # Plugin logic here
        pass

    def unload(self):
        self.iface.removePluginMenu("My Plugin", self.action)
```

## ArcGIS / ArcPy

### Basic ArcPy Operations

```python
import arcpy

# Set workspace
arcpy.env.workspace = "C:/data"

# Set output overwrite
arcpy.env.overwriteOutput = True

# Set scratch workspace
arcpy.env.scratchWorkspace = "C:/data/scratch"

# List features
feature_classes = arcpy.ListFeatureClasses()
rasters = arcpy.ListRasters()
```

### Geoprocessing Workflows

```python
import arcpy
from arcpy.sa import *

# Check out Spatial Analyst extension
arcpy.CheckOutExtension("Spatial")

# Set environment
arcpy.env.workspace = "C:/data"
arcpy.env.cellSize = 10
arcpy.env.extent = "study_area"

# Slope analysis
out_slope = Slope("dem.tif")
out_slope.save("slope.tif")

# Aspect
out_aspect = Aspect("dem.tif")
out_aspect.save("aspect.tif")

# Hillshade
out_hillshade = Hillshade("dem.tif", azimuth=315, altitude=45)
out_hillshade.save("hillshade.tif")

# Viewshed analysis
out_viewshed = Viewshed("observer_points.shp", "dem.tif", obs_elevation_field="HEIGHT")
out_viewshed.save("viewshed.tif")

# Cost distance
cost_raster = CostDistance("source.shp", "cost.tif")
cost_raster.save("cost_distance.tif")

# Hydrology: Flow direction
flow_dir = FlowDirection("dem.tif")
flow_dir.save("flowdir.tif")

# Flow accumulation
flow_acc = FlowAccumulation(flow_dir)
flow_acc.save("flowacc.tif")

# Stream delineation
stream = Con(flow_acc > 1000, 1)
stream_raster = StreamOrder(stream, flow_dir)
```

### Vector Analysis

```python
# Buffer analysis
arcpy.Buffer_analysis("roads.shp", "roads_buffer.shp", "100 meters")

# Spatial join
arcpy.SpatialJoin_analysis("points.shp", "zones.shp", "points_joined.shp",
                           join_operation="JOIN_ONE_TO_ONE",
                           match_option="HAVE_THEIR_CENTER_IN")

# Dissolve
arcpy.Dissolve_management("parcels.shp", "parcels_dissolved.shp",
                          dissolve_field="OWNER_ID")

# Intersect
arcpy.Intersect_analysis(["layer1.shp", "layer2.shp"], "intersection.shp")

# Clip
arcpy.Clip_analysis("input.shp", "clip_boundary.shp", "output.shp")

# Select by location
arcpy.SelectLayerByLocation_management("points_layer", "HAVE_THEIR_CENTER_IN",
                                      "polygon_layer")

# Feature to raster
arcpy.FeatureToRaster_conversion("landuse.shp", "LU_CODE", "landuse.tif", 10)
```

### ArcGIS Pro Notebooks

```python
# ArcGIS Pro Jupyter Notebook
import arcpy
import pandas as pd
import matplotlib.pyplot as plt

# Use current project's map
aprx = arcpy.mp.ArcGISProject("CURRENT")
m = aprx.listMaps()[0]

# Get layer
layer = m.listLayers("Parcels")[0]

# Export to spatial dataframe
sdf = pd.DataFrame.spatial.from_layer(layer)

# Plot
sdf.plot(column='VALUE', cmap='YlOrRd', legend=True)
plt.show()

# Geocode addresses
locator = "C:/data/locators/composite.locator"
results = arcpy.geocoding.GeocodeAddresses(
    "addresses.csv", locator, "Address Address",
    None, "geocoded_results.gdb"
)
```

## GRASS GIS

### Python API for GRASS

```python
import grass.script as gscript
import grass.script.array as garray

# Initialize GRASS session
gscript.run_command('g.gisenv', set='GISDBASE=/grassdata')
gscript.run_command('g.gisenv', set='LOCATION_NAME=nc_spm_08')
gscript.run_command('g.gisenv', set='MAPSET=user1')

# Import raster
gscript.run_command('r.in.gdal', input='elevation.tif', output='elevation')

# Import vector
gscript.run_command('v.in.ogr', input='roads.shp', output='roads')

# Get raster info
info = gscript.raster_info('elevation')
print(info)

# Slope analysis
gscript.run_command('r.slope.aspect', elevation='elevation',
                    slope='slope', aspect='aspect')

# Buffer
gscript.run_command('v.buffer', input='roads', output='roads_buffer',
                    distance=100)

# Overlay
gscript.run_command('v.overlay', ainput='zones', binput='roads',
                    operator='and', output='zones_roads')

# Calculate statistics
stats = gscript.parse_command('r.univar', map='elevation', flags='g')
```

## SAGA GIS

### Using SAGA via Command Line

```python
import subprocess
import os

# SAGA path
saga_cmd = "/usr/local/saga/saga_cmd"

# Grid Calculus
def saga_grid_calculus(input1, input2, output, formula):
    cmd = [
        saga_cmd, "grid_calculus", "GridCalculator",
        f"-GRIDS={input1};{input2}",
        f"-RESULT={output}",
        f"-FORMULA={formula}"
    ]
    subprocess.run(cmd)

# Slope analysis
def saga_slope(dem, output_slope):
    cmd = [
        saga_cmd, "ta_morphometry", "SlopeAspectCurvature",
        f"-ELEVATION={dem}",
        f"-SLOPE={output_slope}"
    ]
    subprocess.run(cmd)

# Morphometric features
def saga_morphometry(dem):
    cmd = [
        saga_cmd, "ta_morphometry", "MorphometricFeatures",
        f"-DEM={dem}",
        f"-SLOPE=slope.sgrd",
        f"-ASPECT=aspect.sgrd",
        f"-CURVATURE=curvature.sgrd"
    ]
    subprocess.run(cmd)

# Channel network
def saga_channels(dem, threshold=1000):
    cmd = [
        saga_cmd, "ta_channels", "ChannelNetworkAndDrainageBasins",
        f"-ELEVATION={dem}",
        f"-CHANNELS=channels.shp",
        f"-BASINS=basins.shp",
        f"-THRESHOLD={threshold}"
    ]
    subprocess.run(cmd)
```

## Cross-Platform Workflows

### Export QGIS to ArcGIS

```python
import geopandas as gpd

# Read data processed in QGIS
gdf = gpd.read_file('qgis_output.geojson')

# Ensure CRS
gdf = gdf.to_crs('EPSG:32633')

# Export for ArcGIS (File Geodatabase)
gdf.to_file('arcgis_input.gpkg', driver='GPKG')
# ArcGIS can read GPKG directly

# Or export to shapefile
gdf.to_file('arcgis_input.shp')
```

### Batch Processing

```python
import geopandas as gpd
from pathlib import Path

# Process multiple files
input_dir = Path('input')
output_dir = Path('output')

for shp in input_dir.glob('*.shp'):
    gdf = gpd.read_file(shp)

    # Process
    gdf['area'] = gdf.geometry.area
    gdf['buffered'] = gdf.geometry.buffer(100)

    # Export for various platforms
    basename = shp.stem
    gdf.to_file(output_dir / f'{basename}_qgis.geojson')
    gdf.to_file(output_dir / f'{basename}_arcgis.shp')
```

For more GIS-specific examples, see [code-examples.md](code-examples.md).

### `references/industry-applications.md`

# Industry Applications

Real-world geospatial workflows across industries: urban planning, disaster management, utilities, and more.

## Urban Planning

### Land Use Classification

```python
def classify_urban_land_use(sentinel2_path, training_data_path):
    """
    Urban land use classification workflow.
    Classes: Residential, Commercial, Industrial, Green Space, Water
    """
    from sklearn.ensemble import RandomForestClassifier
    import geopandas as gpd
    import rasterio

    # 1. Load training data
    training = gpd.read_file(training_data_path)

    # 2. Extract spectral and textural features
    features = extract_features(sentinel2_path, training)

    # 3. Train classifier
    rf = RandomForestClassifier(n_estimators=100, max_depth=20)
    rf.fit(features['X'], features['y'])

    # 4. Classify full image
    classified = classify_image(sentinel2_path, rf)

    # 5. Post-processing
    cleaned = remove_small_objects(classified, min_size=100)
    smoothed = majority_filter(cleaned, size=3)

    # 6. Calculate statistics
    stats = calculate_class_statistics(cleaned)

    return cleaned, stats

def extract_features(image_path, training_gdf):
    """Extract spectral and textural features."""
    with rasterio.open(image_path) as src:
        image = src.read()
        profile = src.profile

    # Spectral features
    features = {
        'NDVI': (image[7] - image[3]) / (image[7] + image[3] + 1e-8),
        'NDWI': (image[2] - image[7]) / (image[2] + image[7] + 1e-8),
        'NDBI': (image[10] - image[7]) / (image[10] + image[7] + 1e-8),
        'UI': (image[10] + image[3]) / (image[7] + image[2] + 1e-8)  # Urban Index
    }

    # Textural features (GLCM)
    from skimage.feature import graycomatrix, graycoprops

    textures = {}
    for band_idx in [3, 7, 10]:  # Red, NIR, SWIR
        band = image[band_idx]
        band_8bit = ((band - band.min()) / (band.max() - band.min()) * 255).astype(np.uint8)

        glcm = graycomatrix(band_8bit, distances=[1], angles=[0], levels=256, symmetric=True)
        contrast = graycoprops(glcm, 'contrast')[0, 0]
        homogeneity = graycoprops(glcm, 'homogeneity')[0, 0]

        textures[f'contrast_{band_idx}'] = contrast
        textures[f'homogeneity_{band_idx}'] = homogeneity

    # Combine all features
    # ... (implementation)

    return features
```

### Population Estimation

```python
def dasymetric_population(population_raster, land_use_classified):
    """
    Dasymetric population redistribution.
    """
    # 1. Identify inhabitable areas
    inhabitable_mask = (
        (land_use_classified != 0) &  # Water
        (land_use_classified != 4) &  # Industrial
        (land_use_classified != 5)    # Roads
    )

    # 2. Assign weights by land use type
    weights = np.zeros_like(land_use_classified, dtype=float)
    weights[land_use_classified == 1] = 1.0  # Residential
    weights[land_use_classified == 2] = 0.3  # Commercial
    weights[land_use_classified == 3] = 0.5  # Green Space

    # 3. Calculate weighting layer
    weighting_layer = weights * inhabitable_mask
    total_weight = np.sum(weighting_layer)

    # 4. Redistribute population
    total_population = np.sum(population_raster)
    redistributed = population_raster * (weighting_layer / total_weight) * total_population

    return redistributed
```

## Disaster Management

### Flood Risk Assessment

```python
def flood_risk_assessment(dem_path, river_path, return_period_years=100):
    """
    Comprehensive flood risk assessment.
    """

    # 1. Hydrological modeling
    flow_accumulation = calculate_flow_accumulation(dem_path)
    flow_direction = calculate_flow_direction(dem_path)
    watershed = delineate_watershed(dem_path, flow_direction)

    # 2. Flood extent estimation
    flood_depth = estimate_flood_extent(dem_path, river_path, return_period_years)

    # 3. Exposure analysis
    settlements = gpd.read_file('settlements.shp')
    roads = gpd.read_file('roads.shp')
    infrastructure = gpd.read_file('infrastructure.shp')

    exposed_settlements = gpd.clip(settlements, flood_extent_polygon)
    exposed_roads = gpd.clip(roads, flood_extent_polygon)

    # 4. Vulnerability assessment
    vulnerability = assess_vulnerability(exposed_settlements)

    # 5. Risk calculation
    risk = flood_depth * vulnerability  # Risk = Hazard × Vulnerability

    # 6. Generate risk maps
    create_risk_map(risk, settlements, output_path='flood_risk.tif')

    return {
        'flood_extent': flood_extent_polygon,
        'exposed_population': calculate_exposed_population(exposed_settlements),
        'risk_zones': risk
    }

def estimate_flood_extent(dem_path, river_path, return_period):
    """
    Estimate flood extent using Manning's equation and hydraulic modeling.
    """
    # 1. Get river cross-section
    # 2. Calculate discharge for return period
    # 3. Apply Manning's equation for water depth
    # 4. Create flood raster

    # Simplified: flat water level
    with rasterio.open(dem_path) as src:
        dem = src.read(1)
        profile = src.profile

    # Water level based on return period
    water_levels = {10: 5, 50: 8, 100: 10, 500: 12}
    water_level = water_levels.get(return_period, 10)

    # Flood extent
    flood_extent = dem < water_level

    return flood_extent
```

### Wildfire Risk Modeling

```python
def wildfire_risk_assessment(vegetation_path, dem_path, weather_data, infrastructure_path):
    """
    Wildfire risk assessment combining multiple factors.
    """

    # 1. Fuel load (from vegetation)
    with rasterio.open(vegetation_path) as src:
        vegetation = src.read(1)

    # Fuel types: 0=No fuel, 1=Low, 2=Medium, 3=High
    fuel_load = vegetation.map_classes({1: 0.2, 2: 0.5, 3: 0.8, 4: 1.0})

    # 2. Slope (fires spread faster uphill)
    with rasterio.open(dem_path) as src:
        dem = src.read(1)

    slope = calculate_slope(dem)
    slope_factor = 1 + (slope / 90) * 0.5  # Up to 50% increase

    # 3. Wind influence
    wind_speed = weather_data['wind_speed']
    wind_direction = weather_data['wind_direction']
    wind_factor = 1 + (wind_speed / 50) * 0.3

    # 4. Vegetation dryness (from NDWI anomaly)
    dryness = calculate_vegetation_dryness(vegetation_path)
    dryness_factor = 1 + dryness * 0.4

    # 5. Combine factors
    risk = fuel_load * slope_factor * wind_factor * dryness_factor

    # 6. Identify assets at risk
    infrastructure = gpd.read_file(infrastructure_path)
    risk_at_infrastructure = extract_raster_values_at_points(risk, infrastructure)

    infrastructure['risk_level'] = risk_at_infrastructure
    high_risk_assets = infrastructure[infrastructure['risk_level'] > 0.7]

    return risk, high_risk_assets
```

## Utilities & Infrastructure

### Power Line Corridor Mapping

```python
def power_line_corridor_analysis(power_lines_path, vegetation_height_path, buffer_distance=50):
    """
    Analyze vegetation encroachment on power line corridors.
    """

    # 1. Load power lines
    power_lines = gpd.read_file(power_lines_path)

    # 2. Create corridor buffer
    corridor = power_lines.buffer(buffer_distance)

    # 3. Load vegetation height
    with rasterio.open(vegetation_height_path) as src:
        veg_height = src.read(1)
        profile = src.profile

    # 4. Extract vegetation height within corridor
    veg_within_corridor = rasterio.mask.mask(veg_height, corridor.geometry, crop=True)[0]

    # 5. Identify encroachment (vegetation > safe height)
    safe_height = 10  # meters
    encroachment = veg_within_corridor > safe_height

    # 6. Classify risk zones
    high_risk = encroachment & (veg_within_corridor > safe_height * 1.5)
    medium_risk = encroachment & ~high_risk

    # 7. Generate maintenance priority map
    priority = np.zeros_like(veg_within_corridor)
    priority[high_risk] = 3  # Urgent
    priority[medium_risk] = 2  # Monitor
    priority[~encroachment] = 1  # Clear

    # 8. Create work order points
    from scipy import ndimage
    labeled, num_features = ndimage.label(high_risk)

    work_orders = []
    for i in range(1, num_features + 1):
        mask = labeled == i
        centroid = ndimage.center_of_mass(mask)
        work_orders.append({
            'location': centroid,
            'area_ha': np.sum(mask) * 0.0001,  # Assuming 1m resolution
            'priority': 'Urgent'
        })

    return priority, work_orders
```

### Pipeline Route Optimization

```python
def optimize_pipeline_route(origin, destination, constraints_path, cost_surface_path):
    """
    Optimize pipeline route using least-cost path analysis.
    """

    # 1. Load cost surface
    with rasterio.open(cost_surface_path) as src:
        cost = src.read(1)
        profile = src.profile

    # 2. Apply constraints
    constraints = gpd.read_file(constraints_path)
    no_go_zones = constraints[constraints['type'] == 'no_go']

    # Set very high cost for no-go zones
    for _, zone in no_go_zones.iterrows():
        mask = rasterize_features(zone.geometry, profile['shape'])
        cost[mask > 0] = 999999

    # 3. Least-cost path (Dijkstra)
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import shortest_path

    # Convert to graph (8-connected)
    graph = create_graph_from_raster(cost)

    # Origin and destination nodes
    orig_node = coord_to_node(origin, profile)
    dest_node = coord_to_node(destination, profile)

    # Find path
    _, predecessors = shortest_path(csgraph=graph,
                                   directed=True,
                                   indices=orig_node,
                                   return_predecessors=True)

    # Reconstruct path
    path = reconstruct_path(predecessors, dest_node)

    # 4. Convert path to coordinates
    route_coords = [node_to_coord(node, profile) for node in path]
    route = LineString(route_coords)

    return route

def create_graph_from_raster(cost_raster):
    """Create graph from cost raster for least-cost path."""
    # 8-connected neighbor costs
    # Implementation depends on library choice
    pass
```

## Transportation

### Traffic Analysis

```python
def traffic_analysis(roads_gdf, traffic_counts_path):
    """
    Analyze traffic patterns and congestion.
    """

    # 1. Load traffic count data
    counts = gpd.read_file(traffic_counts_path)

    # 2. Interpolate traffic to all roads
    import networkx as nx

    # Create road network
    G = nx.Graph()
    for _, road in roads_gdf.iterrows():
        coords = list(road.geometry.coords)
        for i in range(len(coords) - 1):
            G.add_edge(coords[i], coords[i+1],
                      length=road.geometry.length,
                      road_id=road.id)

    # 3. Spatial interpolation of counts
    from sklearn.neighbors import KNeighborsRegressor

    count_coords = np.array([[p.x, p.y] for p in counts.geometry])
    count_values = counts['AADT'].values

    knn = KNeighborsRegressor(n_neighbors=5, weights='distance')
    knn.fit(count_coords, count_values)

    # 4. Predict traffic for all road segments
    all_coords = np.array([[n[0], n[1]] for n in G.nodes()])
    predicted_traffic = knn.predict(all_coords)

    # 5. Identify congested segments
    for i, (u, v) in enumerate(G.edges()):
        avg_traffic = (predicted_traffic[list(G.nodes()).index(u)] +
                      predicted_traffic[list(G.nodes()).index(v)]) / 2
        capacity = G[u][v]['capacity']  # Need capacity data

        G[u][v]['v_c_ratio'] = avg_traffic / capacity

    # 6. Congestion hotspots
    congested_edges = [(u, v) for u, v, d in G.edges(data=True)
                      if d.get('v_c_ratio', 0) > 0.9]

    return G, congested_edges
```

### Transit Service Area Analysis

```python
def transit_service_area(stops_gdf, max_walk_distance=800, max_time=30):
    """
    Calculate transit service area considering walk distance and travel time.
    """

    # 1. Walkable area around stops
    walk_buffer = stops_gdf.buffer(max_walk_distance)

    # 2. Load road network for walk time
    roads = gpd.read_file('roads.shp')
    G = osmnx.graph_from_gdf(roads)

    # 3. For each stop, calculate accessible area within walk time
    service_areas = []

    for _, stop in stops_gdf.iterrows():
        # Find nearest node
        stop_node = ox.distance.nearest_nodes(G, stop.geometry.x, stop.geometry.y)

        # Get subgraph within walk time
        walk_speed = 5 / 3.6  # km/h to m/s
        max_nodes = int(max_time * 60 * walk_speed / 20)  # Assuming ~20m per edge

        subgraph = nx.ego_graph(G, stop_node, radius=max_nodes)

        # Create polygon from reachable nodes
        reachable_nodes = ox.graph_to_gdfs(subgraph, edges=False)
        service_area = reachable_nodes.geometry.unary_union.convex_hull

        service_areas.append({
            'stop_id': stop.stop_id,
            'service_area': service_area,
            'area_km2': service_area.area / 1e6
        })

    return service_areas
```

For more industry-specific workflows, see [code-examples.md](code-examples.md).

### `references/machine-learning.md`

# Machine Learning for Geospatial Data

Guide to ML and deep learning applications for remote sensing and spatial analysis.

## Traditional Machine Learning

### Random Forest for Land Cover

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import rasterio
from rasterio.features import rasterize
import geopandas as gpd
import numpy as np

def train_random_forest_classifier(raster_path, training_gdf):
    """Train Random Forest for image classification."""

    # Load imagery
    with rasterio.open(raster_path) as src:
        image = src.read()
        profile = src.profile
        transform = src.transform

    # Extract training data
    X, y = [], []

    for _, row in training_gdf.iterrows():
        mask = rasterize(
            [(row.geometry, 1)],
            out_shape=(profile['height'], profile['width']),
            transform=transform,
            fill=0,
            dtype=np.uint8
        )
        pixels = image[:, mask > 0].T
        X.extend(pixels)
        y.extend([row['class_id']] * len(pixels))

    X = np.array(X)
    y = np.array(y)

    # Split data
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Train model
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        min_samples_split=10,
        min_samples_leaf=4,
        class_weight='balanced',
        n_jobs=-1,
        random_state=42
    )
    rf.fit(X_train, y_train)

    # Validate
    y_pred = rf.predict(X_val)
    print("Classification Report:")
    print(classification_report(y_val, y_pred))

    # Feature importance
    feature_names = [f'Band_{i}' for i in range(X.shape[1])]
    importances = pd.DataFrame({
        'feature': feature_names,
        'importance': rf.feature_importances_
    }).sort_values('importance', ascending=False)

    print("\nFeature Importance:")
    print(importances)

    return rf

# Classify full image
def classify_image(model, image_path, output_path):
    with rasterio.open(image_path) as src:
        image = src.read()
        profile = src.profile

    image_reshaped = image.reshape(image.shape[0], -1).T
    prediction = model.predict(image_reshaped)
    prediction = prediction.reshape(image.shape[1], image.shape[2])

    profile.update(dtype=rasterio.uint8, count=1)
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(prediction.astype(rasterio.uint8), 1)
```

### Support Vector Machine

```python
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler

def svm_classifier(X_train, y_train):
    """SVM classifier for remote sensing."""

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    # Train SVM
    svm = SVC(
        kernel='rbf',
        C=100,
        gamma='scale',
        class_weight='balanced',
        probability=True
    )
    svm.fit(X_train_scaled, y_train)

    return svm, scaler

# Multi-class classification
def multiclass_svm(X_train, y_train):
    from sklearn.multiclass import OneVsRestClassifier

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    svm_ovr = OneVsRestClassifier(
        SVC(kernel='rbf', C=10, probability=True),
        n_jobs=-1
    )
    svm_ovr.fit(X_train_scaled, y_train)

    return svm_ovr, scaler
```

## Deep Learning

### CNN with TorchGeo

```python
import torch
import torch.nn as nn
import torchgeo.datasets as datasets
import torchgeo.models as models
from torch.utils.data import DataLoader

# Define CNN
class LandCoverCNN(nn.Module):
    def __init__(self, in_channels=12, num_classes=10):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(in_channels, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(64, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(128, 256, 3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )

        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(256, 128, 2, stride=2),
            nn.BatchNorm2d(128),
            nn.ReLU(),

            nn.ConvTranspose2d(128, 64, 2, stride=2),
            nn.BatchNorm2d(64),
            nn.ReLU(),

            nn.ConvTranspose2d(64, num_classes, 2, stride=2),
        )

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x

# Training
def train_model(train_loader, val_loader, num_epochs=50):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = LandCoverCNN().to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    for epoch in range(num_epochs):
        model.train()
        train_loss = 0

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()

        # Validation
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                val_loss += loss.item()

        print(f'Epoch {epoch+1}/{num_epochs}, Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}')

    return model
```

### U-Net for Semantic Segmentation

```python
class UNet(nn.Module):
    def __init__(self, in_channels=4, num_classes=5):
        super().__init__()

        # Encoder
        self.enc1 = self.conv_block(in_channels, 64)
        self.enc2 = self.conv_block(64, 128)
        self.enc3 = self.conv_block(128, 256)
        self.enc4 = self.conv_block(256, 512)

        # Bottleneck
        self.bottleneck = self.conv_block(512, 1024)

        # Decoder
        self.up1 = nn.ConvTranspose2d(1024, 512, 2, stride=2)
        self.dec1 = self.conv_block(1024, 512)

        self.up2 = nn.ConvTranspose2d(512, 256, 2, stride=2)
        self.dec2 = self.conv_block(512, 256)

        self.up3 = nn.ConvTranspose2d(256, 128, 2, stride=2)
        self.dec3 = self.conv_block(256, 128)

        self.up4 = nn.ConvTranspose2d(128, 64, 2, stride=2)
        self.dec4 = self.conv_block(128, 64)

        # Final layer
        self.final = nn.Conv2d(64, num_classes, 1)

    def conv_block(self, in_ch, out_ch):
        return nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        # Encoder
        e1 = self.enc1(x)
        e2 = self.enc2(F.max_pool2d(e1, 2))
        e3 = self.enc3(F.max_pool2d(e2, 2))
        e4 = self.enc4(F.max_pool2d(e3, 2))

        # Bottleneck
        b = self.bottleneck(F.max_pool2d(e4, 2))

        # Decoder with skip connections
        d1 = self.dec1(torch.cat([self.up1(b), e4], dim=1))
        d2 = self.dec2(torch.cat([self.up2(d1), e3], dim=1))
        d3 = self.dec3(torch.cat([self.up3(d2), e2], dim=1))
        d4 = self.dec4(torch.cat([self.up4(d3), e1], dim=1))

        return self.final(d4)
```

### Change Detection with Siamese Network

```python
class SiameseNetwork(nn.Module):
    """Siamese network for change detection."""

    def __init__(self):
        super().__init__()
        self.feature_extractor = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(64, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
        )

        self.classifier = nn.Sequential(
            nn.Conv2d(256, 128, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(128, 64, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 2, 1),  # Binary: change / no change
        )

    def forward(self, x1, x2):
        f1 = self.feature_extractor(x1)
        f2 = self.feature_extractor(x2)

        # Concatenate features
        diff = torch.abs(f1 - f2)
        combined = torch.cat([f1, f2, diff], dim=1)

        return self.classifier(combined)
```

## Graph Neural Networks

### PyTorch Geometric for Spatial Data

```python
import torch
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv

# Create spatial graph
def create_spatial_graph(points_gdf, k_neighbors=5):
    """Create graph from point data using k-NN."""

    from sklearn.neighbors import NearestNeighbors

    coords = np.array([[p.x, p.y] for p in points_gdf.geometry])

    # Find k-nearest neighbors
    nbrs = NearestNeighbors(n_neighbors=k_neighbors).fit(coords)
    distances, indices = nbrs.kneighbors(coords)

    # Create edge index
    edge_index = []
    for i, neighbors in enumerate(indices):
        for j in neighbors:
            edge_index.append([i, j])

    edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()

    # Node features
    features = points_gdf.drop('geometry', axis=1).values
    x = torch.tensor(features, dtype=torch.float)

    return Data(x=x, edge_index=edge_index)

# GCN for spatial prediction
class SpatialGCN(torch.nn.Module):
    def __init__(self, num_features, hidden_channels=64):
        super().__init__()
        self.conv1 = GCNConv(num_features, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, hidden_channels)
        self.conv3 = GCNConv(hidden_channels, 1)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index
        x = self.conv1(x, edge_index).relu()
        x = F.dropout(x, p=0.5, training=self.training)
        x = self.conv2(x, edge_index).relu()
        x = self.conv3(x, edge_index)
        return x
```

## Explainable AI (XAI) for Geospatial

### SHAP for Model Interpretation

```python
import shap
import numpy as np

def explain_model(model, X, feature_names):
    """Explain model predictions using SHAP."""

    # Create explainer
    explainer = shap.Explainer(model, X)

    # Calculate SHAP values
    shap_values = explainer(X)

    # Summary plot
    shap.summary_plot(shap_values, X, feature_names=feature_names)

    # Dependence plot for important features
    for i in range(X.shape[1]):
        shap.dependence_plot(i, shap_values, X, feature_names=feature_names)

    return shap_values

# Spatial SHAP (accounting for spatial autocorrelation)
def spatial_shap(model, X, coordinates):
    """Spatial explanation considering neighborhood effects."""

    # Compute SHAP values
    explainer = shap.Explainer(model, X)
    shap_values = explainer(X)

    # Spatial aggregation
    shap_spatial = {}
    for i, coord in enumerate(coordinates):
        # Find neighbors
        neighbors = find_neighbors(coord, coordinates, radius=1000)

        # Aggregate SHAP values for neighborhood
        neighbor_shap = shap_values.values[neighbors]
        shap_spatial[i] = np.mean(neighbor_shap, axis=0)

    return shap_spatial
```

### Attention Maps for CNNs

```python
import cv2
import torch
import torch.nn.functional as F

def generate_attention_map(model, image_tensor, target_layer):
    """Generate attention map using Grad-CAM."""

    # Forward pass
    model.eval()
    output = model(image_tensor)

    # Backward pass
    model.zero_grad()
    output[0, torch.argmax(output)].backward()

    # Get gradients
    gradients = model.get_gradient(target_layer)

    # Global average pooling
    weights = torch.mean(gradients, axis=(2, 3), keepdim=True)

    # Weighted combination of activation maps
    activations = model.get_activation(target_layer)
    attention = torch.sum(weights * activations, axis=1, keepdim=True)

    # ReLU and normalize
    attention = F.relu(attention)
    attention = F.interpolate(attention, size=image_tensor.shape[2:],
                              mode='bilinear', align_corners=False)
    attention = (attention - attention.min()) / (attention.max() - attention.min())

    return attention.squeeze().cpu().numpy()
```

For more ML examples, see [code-examples.md](code-examples.md).

### `references/programming-languages.md`

# Multi-Language Geospatial Programming

Geospatial programming across 8 languages: R, Julia, JavaScript, C++, Java, Go, Rust, and Python.

## R Geospatial

### sf (Simple Features)

```r
library(sf)
library(dplyr)
library(ggplot2)

# Read spatial data
roads <- st_read("roads.shp")
zones <- st_read("zones.geojson")

# Basic operations
st_crs(roads)  # Check CRS
roads_utm <- st_transform(roads, 32610)  # Reproject

# Geometric operations
roads_buffer <- st_buffer(roads, dist = 100)  # Buffer
roads_simplify <- st_simplify(roads, tol = 0.0001)  # Simplify
roads_centroid <- st_centroid(roads)  # Centroid

# Spatial joins
joined <- st_join(roads, zones, join = st_intersects)

# Overlay
intersection <- st_intersection(roads, zones)

# Plot
ggplot() +
  geom_sf(data = zones, fill = NA) +
  geom_sf(data = roads, color = "blue") +
  theme_minimal()

# Calculate area
zones$area <- st_area(zones)  # In CRS units
zones$area_km2 <- st_area(zones) / 1e6  # Convert to km2
```

### terra (Raster Processing)

```r
library(terra)

# Load raster
r <- rast("elevation.tif")

# Basic info
r
ext(r)  # Extent
crs(r)  # CRS
res(r)  # Resolution

# Raster calculations
slope <- terrain(r, v = "slope")
aspect <- terrain(r, v = "aspect")

# Multi-raster operations
ndvi <- (s2[[8]] - s2[[4]]) / (s2[[8]] + s2[[4]])

# Focal operations
focal_mean <- focal(r, w = matrix(1, 3, 3), fun = mean)
focal_sd <- focal(r, w = matrix(1, 5, 5), fun = sd)

# Zonal statistics
zones <- vect("zones.shp")
zonal_mean <- zonal(r, zones, fun = mean)

# Extract values at points
points <- vect("points.shp")
values <- extract(r, points)

# Write output
writeRaster(slope, "slope.tif", overwrite = TRUE)
```

### R Workflows

```r
# Complete land cover classification
library(sf)
library(terra)
library(randomForest)
library(caret)

# 1. Load data
training <- st_read("training.shp")
s2 <- rast("sentinel2.tif")

# 2. Extract training data
training_points <- st_centroid(training)
values <- extract(s2, training_points)

# 3. Combine with labels
df <- data.frame(values)
df$class <- as.factor(training$class_id)

# 4. Train model
set.seed(42)
train_index <- createDataPartition(df$class, p = 0.7, list = FALSE)
train_data <- df[train_index, ]
test_data <- df[-train_index, ]

rf_model <- randomForest(class ~ ., data = train_data, ntree = 100)

# 5. Predict
predicted <- predict(s2, model = rf_model)

# 6. Accuracy
conf_matrix <- confusionMatrix(predict(rf_model, test_data), test_data$class)
print(conf_matrix)

# 7. Export
writeRaster(predicted, "classified.tif", overwrite = TRUE)
```

## Julia Geospatial

### ArchGDAL.jl

```julia
using ArchGDAL
using GeoInterface

# Register drivers
ArchGDAL.registerdrivers() do
    # Read shapefile
    data = ArchGDAL.read("countries.shp") do dataset
        layer = dataset[1]
        features = []
        for feature in layer
            geom = ArchGDAL.getgeom(feature)
            push!(features, geom)
        end
        features
    end
end

# Create geometries
using GeoInterface

point = GeoInterface.Point(-122.4, 37.7)
polygon = GeoInterface.Polygon([GeoInterface.LinearRing([
    GeoInterface.Point(-122.5, 37.5),
    GeoInterface.Point(-122.3, 37.5),
    GeoInterface.Point(-122.3, 37.8),
    GeoInterface.Point(-122.5, 37.8),
    GeoInterface.Point(-122.5, 37.5)
])])

# Geometric operations
buffered = GeoInterface.buffer(point, 1000)
intersection = GeoInterface.intersection(poly1, poly2)
```

### GeoStats.jl

```julia
using GeoStats
using GeoStatsBase
using Variography

# Load point data
data = georef((value = [1.0, 2.0, 3.0],),
              [Point(0.0, 0.0), Point(1.0, 0.0), Point(0.5, 1.0)])

# Experimental variogram
γ = variogram(EmpiricalVariogram, data, :value, maxlag = 1.0)

# Fit theoretical variogram
γfit = fit(EmpiricalVariogram, γ, SphericalVariogram)

# Ordinary kriging
problem = OrdinaryKriging(data, :value, γfit)
solution = solve(problem)

# Simulate
simulation = SimulationProblem(data, :value, SphericalVariogram, 100)
result = solve(simulation)
```

## JavaScript (Node.js & Browser)

### Turf.js (Browser/Node)

```javascript
// npm install @turf/turf
const turf = require('@turf/turf');

// Create features
const pt1 = turf.point([-122.4, 37.7]);
const pt2 = turf.point([-122.3, 37.8]);

// Distance (in kilometers)
const distance = turf.distance(pt1, pt2, { units: 'kilometers' });

// Buffer
const buffered = turf.buffer(pt1, 5, { units: 'kilometers' });

// Bounding box
const bbox = turf.bbox(buffered);

// Along a line
const line = turf.lineString([[-122.4, 37.7], [-122.3, 37.8]]);
const along = turf.along(line, 2, { units: 'kilometers' });

// Within
const points = turf.points([
  [-122.4, 37.7],
  [-122.35, 37.75],
  [-122.3, 37.8]
]);
const polygon = turf.polygon([[[-122.4, 37.7], [-122.3, 37.7], [-122.3, 37.8], [-122.4, 37.8], [-122.4, 37.7]]]);
const ptsWithin = turf.pointsWithinPolygon(points, polygon);

// Nearest point
const nearest = turf.nearestPoint(pt1, points);

// Area
const area = turf.area(polygon); // square meters

```

### Leaflet (Web Mapping)

```javascript
// Initialize map
const map = L.map('map').setView([37.7, -122.4], 13);

// Add tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Add GeoJSON layer
fetch('data.geojson')
  .then(response => response.json())
  .then(data => {
    L.geoJSON(data, {
      style: function(feature) {
        return { color: feature.properties.color };
      },
      onEachFeature: function(feature, layer) {
        layer.bindPopup(feature.properties.name);
      }
    }).addTo(map);
  });

// Add markers
const marker = L.marker([37.7, -122.4]).addTo(map);
marker.bindPopup("Hello!").openPopup();

// Draw circles
const circle = L.circle([37.7, -122.4], {
  color: 'red',
  fillColor: '#f03',
  fillOpacity: 0.5,
  radius: 500
}).addTo(map);
```

## C++ Geospatial

### GDAL C++ API

```cpp
#include "gdal_priv.h"
#include "ogr_api.h"
#include "ogr_spatialref.h"

// Open raster
GDALDataset *poDataset = (GDALDataset *) GDALOpen("input.tif", GA_ReadOnly);

// Get band
GDALRasterBand *poBand = poDataset->GetRasterBand(1);

// Read data
int nXSize = poBand->GetXSize();
int nYSize = poBand->GetYSize();
float *pafScanline = (float *) CPLMalloc(sizeof(float) * nXSize);
poBand->RasterIO(GF_Read, 0, 0, nXSize, 1,
                 pafScanline, nXSize, 1, GDT_Float32, 0, 0);

// Vector data
GDALDataset *poDS = (GDALDataset *) GDALOpenEx("roads.shp",
    GDAL_OF_VECTOR, NULL, NULL, NULL);
OGRLayer *poLayer = poDS->GetLayer(0);

OGRFeature *poFeature;
poLayer->ResetReading();
while ((poFeature = poLayer->GetNextFeature()) != NULL) {
    OGRGeometry *poGeometry = poFeature->GetGeometryRef();
    // Process geometry
    OGRFeature::DestroyFeature(poFeature);
}

GDALClose(poDS);
```

## Java Geospatial

### GeoTools

```java
import org.geotools.data.FileDataStore;
import org.geotools.data.FileDataStoreFinder;
import org.geotools.data.simple.SimpleFeatureCollection;
import org.geotools.data.simple.SimpleFeatureIterator;
import org.geotools.data.simple.SimpleFeatureSource;
import org.geotools.geometry.jts.JTS;
import org.geotools.referencing.CRS;
import org.opengis.feature.simple.SimpleFeature;
import org.opengis.referencing.crs.CoordinateReferenceSystem;

import org.locationtech.jts.geom.Coordinate;
import org.locationtech.jts.geom.GeometryFactory;
import org.locationtech.jts.geom.Point;

// Load shapefile
File file = new File("roads.shp");
FileDataStore store = FileDataStoreFinder.getDataStore(file);
SimpleFeatureSource featureSource = store.getFeatureSource();

// Read features
SimpleFeatureCollection collection = featureSource.getFeatures();
try (SimpleFeatureIterator iterator = collection.features()) {
    while (iterator.hasNext()) {
        SimpleFeature feature = iterator.next();
        Geometry geom = (Geometry) feature.getDefaultGeometryProperty().getValue();
        // Process geometry
    }
}

// Create point
GeometryFactory gf = new GeometryFactory();
Point point = gf.createPoint(new Coordinate(-122.4, 37.7));

// Reproject
CoordinateReferenceSystem sourceCRS = CRS.decode("EPSG:4326");
CoordinateReferenceSystem targetCRS = CRS.decode("EPSG:32633");
MathTransform transform = CRS.findMathTransform(sourceCRS, targetCRS);
Geometry reprojected = JTS.transform(point, transform);
```

## Go Geospatial

### Simple Features Go

```go
package main

import (
    "fmt"
    "github.com/paulmach/orb"
    "github.com/paulmach/orb/geojson"
    "github.com/paulmach/orb/planar"
)

func main() {
    // Create point
    point := orb.Point{122.4, 37.7}

    // Create linestring
    line := orb.LineString{
        {122.4, 37.7},
        {122.3, 37.8},
    }

    // Create polygon
    polygon := orb.Polygon{
        {{122.4, 37.7}, {122.3, 37.7}, {122.3, 37.8}, {122.4, 37.8}, {122.4, 37.7}},
    }

    // GeoJSON feature
    feature := geojson.NewFeature(polygon)
    feature.Properties["name"] = "Zone 1"

    // Distance (planar)
    distance := planar.Distance(point, orb.Point{122.3, 37.8})

    // Area
    area := planar.Area(polygon)

    fmt.Printf("Distance: %.2f meters\n", distance)
    fmt.Printf("Area: %.2f square meters\n", area)
}
```

For more code examples across all languages, see [code-examples.md](code-examples.md).

## Rust Geospatial

### GeoRust (Geographic Rust)

The Rust geospatial ecosystem includes crates for geometry operations, projections, and file I/O.

\`\`\`rust
// Cargo.toml dependencies:
// geo = "0.28"
// geo-types = "0.7"
// proj = "0.27"
// shapefile = "0.5"

use geo::{Coord, Point, LineString, Polygon, Geometry};
use geo::prelude::*;
use proj::Proj;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Create a point
    let point = Point::new(-122.4_f64, 37.7_f64);

    // Create a linestring
    let linestring = LineString::new(vec![
        Coord { x: -122.4, y: 37.7 },
        Coord { x: -122.3, y: 37.8 },
        Coord { x: -122.2, y: 37.9 },
    ]);

    // Create a polygon
    let polygon = Polygon::new(
        LineString::new(vec![
            Coord { x: -122.4, y: 37.7 },
            Coord { x: -122.3, y:  37.7 },
            Coord { x: -122.3, y: 37.8 },
            Coord { x: -122.4, y: 37.8 },
            Coord { x: -2.4, y: 37.7 }, // Close the ring
        ]),
        vec![], // No interior rings
    );

    // Geometric operations
    let buffered = polygon.buffer(1000.0); // Buffer in CRS units
    let centroid = polygon.centroid();
    let convex_hull = polygon.convex_hull();
    let simplified = polygon.simplify(&1.0); // Tolerance

    // Spatial relationships
    let point_within = point.within(&polygon);
    let line_intersects = linestring.intersects(&polygon);

    // Coordinate transformation
    let from = "EPSG:4326";
    let to = "EPSG:32610";
    let proj = Proj::new_known_crs(from, to, None)?;
    let transformed = proj.convert(point)?;

    println!("Point: {:?}", point);
    println!("Within polygon: {}", point_within);

    Ok(())
}
\`\`\`

### `references/remote-sensing.md`

# Remote Sensing Reference

Comprehensive guide to satellite data acquisition, processing, and analysis.

## Satellite Missions Overview

| Satellite | Operator | Resolution | Revisit | Key Features |
|-----------|----------|------------|---------|--------------|
| **Sentinel-2** | ESA | 10-60m | 5 days | 13 bands, free access |
| **Landsat 8/9** | USGS | 30m | 16 days | Historical archive (1972+) |
| **MODIS** | NASA | 250-1000m | Daily | Vegetation indices |
| **PlanetScope** | Planet | 3m | Daily | Commercial, high-res |
| **WorldView** | Maxar | 0.3m | Variable | Very high resolution |
| **Sentinel-1** | ESA | 5-40m | 6-12 days | SAR, all-weather |
| **Envisat** | ESA | 30m | 35 days | SAR (archival) |

## Sentinel-2 Processing

### Accessing Sentinel-2 Data

```python
import pystac_client
import planetary_computer
import odc.stac
import xarray as xr

# Search Sentinel-2 collection
catalog = pystac_client.Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace,
)

# Define AOI and time range
bbox = [-122.5, 37.7, -122.3, 37.9]
search = catalog.search(
    collections=["sentinel-2-l2a"],
    bbox=bbox,
    datetime="2023-01-01/2023-12-31",
    query={"eo:cloud_cover": {"lt": 20}},
)

items = list(search.get_items())
print(f"Found {len(items)} items")

# Load as xarray dataset
data = odc.stac.load(
    [items[0]],
    bands=["B02", "B03", "B04", "B08", "B11"],
    crs="EPSG:32610",
    resolution=10,
)

print(data)
```

### Calculating Spectral Indices

```python
import numpy as np
import rasterio

def ndvi(nir, red):
    """Normalized Difference Vegetation Index"""
    return (nir - red) / (nir + red + 1e-8)

def evi(nir, red, blue):
    """Enhanced Vegetation Index"""
    return 2.5 * (nir - red) / (nir + 6*red - 7.5*blue + 1)

def savi(nir, red, L=0.5):
    """Soil Adjusted Vegetation Index"""
    return ((nir - red) / (nir + red + L)) * (1 + L)

def ndwi(green, nir):
    """Normalized Difference Water Index"""
    return (green - nir) / (green + nir + 1e-8)

def mndwi(green, swir):
    """Modified NDWI for open water"""
    return (green - swir) / (green + swir + 1e-8)

def nbr(nir, swir):
    """Normalized Burn Ratio"""
    return (nir - swir) / (nir + swir + 1e-8)

def ndbi(swir, nir):
    """Normalized Difference Built-up Index"""
    return (swir - nir) / (swir + nir + 1e-8)

# Batch processing
with rasterio.open('sentinel2.tif') as src:
    # Sentinel-2 band mapping
    B02 = src.read(1).astype(float)  # Blue (10m)
    B03 = src.read(2).astype(float)  # Green (10m)
    B04 = src.read(3).astype(float)  # Red (10m)
    B08 = src.read(4).astype(float)  # NIR (10m)
    B11 = src.read(5).astype(float)  # SWIR1 (20m, resampled)

    # Calculate indices
    NDVI = ndvi(B08, B04)
    EVI = evi(B08, B04, B02)
    SAVI = savi(B08, B04, L=0.5)
    NDWI = ndwi(B03, B08)
    NBR = nbr(B08, B11)
    NDBI = ndbi(B11, B08)
```

## Landsat Processing

### Landsat Collection 2

```python
import ee

# Initialize Earth Engine
ee.Initialize(project='your-project')

# Landsat 8 Collection 2 Level 2
landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
    .filterBounds(ee.Geometry.Point([-122.4, 37.7])) \
    .filterDate('2020-01-01', '2023-12-31') \
    .filter(ee.Filter.lt('CLOUD_COVER', 20))

# Apply scaling factors (Collection 2)
def apply_scale_factors(image):
    optical = image.select('SR_B.').multiply(0.0000275).add(-0.2)
    thermal = image.select('ST_B10').multiply(0.00341802).add(149.0)
    return image.addBands(optical, None, True).addBands(thermal, None, True)

landsat_scaled = landsat.map(apply_scale_factors)

# Calculate NDVI
def add_ndvi(image):
    ndvi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
    return image.addBands(ndvi)

landsat_ndvi = landsat_scaled.map(add_ndvi)

# Get composite
composite = landsat_ndvi.median()
```

### Landsat Surface Temperature

```python
def land_surface_temperature(image):
    """Calculate land surface temperature from Landsat 8."""
    # Brightness temperature
    Tb = image.select('ST_B10')

    # NDVI for emissivity
    ndvi = image.normalizedDifference(['SR_B5', 'SR_B4'])
    pv = ((ndvi - 0.2) / (0.5 - 0.2)) ** 2  # Proportion of vegetation

    # Emissivity
    em = 0.004 * pv + 0.986

    # LST in Kelvin
    lst = Tb.divide(1 + (0.00115 * Tb / 1.4388) * np.log(em))

    # Convert to Celsius
    lst_c = lst.subtract(273.15).rename('LST')

    return image.addBands(lst_c)

landsat_lst = landsat_scaled.map(land_surface_temperature)
```

## SAR Processing (Synthetic Aperture Radar)

### Sentinel-1 GRD Processing

```python
import rasterio
from scipy.ndimage import gaussian_filter
import numpy as np

def process_sentinel1_grd(input_path, output_path):
    """Process Sentinel-1 GRD data."""
    with rasterio.open(input_path) as src:
        # Read VV and VH bands
        vv = src.read(1).astype(float)
        vh = src.read(2).astype(float)

        # Convert to decibels
        vv_db = 10 * np.log10(vv + 1e-8)
        vh_db = 10 * np.log10(vh + 1e-8)

        # Speckle filtering (Lee filter approximation)
        def lee_filter(img, size=3):
            """Simple Lee filter for speckle reduction."""
            # Local mean
            mean = gaussian_filter(img, size)
            # Local variance
            sq_mean = gaussian_filter(img**2, size)
            variance = sq_mean - mean**2
            # Noise variance
            noise_var = np.var(img) * 0.5
            # Lee filter formula
            return mean + (variance - noise_var) / (variance) * (img - mean)

        vv_filtered = lee_filter(vv_db)
        vh_filtered = lee_filter(vh_db)

        # Calculate ratio
        ratio = vv_db - vh_db  # In dB: difference = ratio

        # Save
        profile = src.profile
        profile.update(dtype=rasterio.float32, count=3)

        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(vv_filtered.astype(np.float32), 1)
            dst.write(vh_filtered.astype(np.float32), 2)
            dst.write(ratio.astype(np.float32), 3)

# Usage
process_sentinel1_grd('S1A_IW_GRDH.tif', 'S1A_processed.tif')
```

### SAR Polarimetric Indices

```python
def calculate_sar_indices(vv, vh):
    """Calculate SAR-derived indices."""
    # Backscatter ratio in dB
    ratio_db = 10 * np.log10(vv / (vh + 1e-8) + 1e-8)

    # Radar Vegetation Index
    rvi = (4 * vh) / (vv + vh + 1e-8)

    # Soil Moisture Index (approximation)
    smi = vv / (vv + vh + 1e-8)

    return ratio_db, rvi, smi
```

## Hyperspectral Imaging

### Hyperspectral Data Processing

```python
import spectral.io.envi as envi
import numpy as np
import matplotlib.pyplot as plt

# Load hyperspectral cube
hdr_path = 'hyperspectral.hdr'
img = envi.open(hdr_path)
data = img.load()

print(f"Data shape: {data.shape}")  # (rows, cols, bands)

# Extract spectral signature at a pixel
pixel_signature = data[100, 100, :]
plt.plot(img.bands.centers, pixel_signature)
plt.xlabel('Wavelength (nm)')
plt.ylabel('Reflectance')
plt.show()

# Spectral indices for hyperspectral
def calculate_ndi(hyper_data, band1_idx, band2_idx):
    """Normalized Difference Index for any two bands."""
    band1 = hyper_data[:, :, band1_idx]
    band2 = hyper_data[:, :, band2_idx]
    return (band1 - band2) / (band1 + band2 + 1e-8)

# Red Edge Position (REP)
def red_edge_position(hyper_data, wavelengths):
    """Calculate red edge position."""
    # Find wavelength of maximum slope in red-edge region (680-750nm)
    red_edge_idx = np.where((wavelengths >= 680) & (wavelengths <= 750))[0]

    first_derivative = np.diff(hyper_data, axis=2)
    rep_idx = np.argmax(first_derivative[:, :, red_edge_idx], axis=2)
    return wavelengths[red_edge_idx][rep_idx]
```

## Image Preprocessing

### Atmospheric Correction

```python
# Using 6S (via Py6S)
from Py6S import *

# Create 6S instance
s = SixS()

# Set atmospheric conditions
s.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeSummer)
s.aero_profile = AeroProfile.PredefinedType(AeroProfile.Continental)

# Set geometry
s.geometry = Geometry.User()
s.geometry.month = 6
s.geometry.day = 15
s.geometry.solar_z = 30
s.geometry.solar_a = 180

# Run simulation
s.run()

# Get correction coefficients
xa, xb, xc = s.outputs.coef_xa, s.outputs.coef_xb, s.outputs.coef_xc

def atmospheric_correction(dn, xa, xb, xc):
    """Apply 6S atmospheric correction."""
    y = xa * dn - xb
    y = y / (1 + xc * y)
    return y
```

### Cloud Masking

```python
def sentinel2_cloud_mask(s2_image):
    """Generate cloud mask for Sentinel-2."""
    # Simple cloud detection using spectral tests
    scl = s2_image.select('SCL')  # Scene Classification Layer

    # Cloud classes: 8=Cloud, 9=Cloud medium, 10=Cloud high
    cloud_mask = scl.gt(7).And(scl.lt(11))

    # Additional test: Brightness threshold
    brightness = s2_image.select(['B02','B03','B04','B08']).mean()

    return cloud_mask.Or(brightness.gt(0.4))

# Apply mask
def apply_mask(image):
    mask = sentinel2_cloud_mask(image)
    return image.updateMask(mask.Not())
```

### Pan-Sharpening

```python
import cv2
import numpy as np

def gram_schmidt_pansharpen(ms, pan):
    """Gram-Schmidt pan-sharpening."""
    # Multispectral: (H, W, bands)
    # Panchromatic: (H, W)

    # 1. Upsample MS to pan resolution
    ms_up = cv2.resize(ms, (pan.shape[1], pan.shape[0]),
                       interpolation=cv2.INTER_CUBIC)

    # 2. Simulate panchromatic from MS
    weights = np.array([0.25, 0.25, 0.25, 0.25])  # Equal weights
    simulated = np.sum(ms_up * weights.reshape(1, 1, -1), axis=2)

    # 3. Gram-Schmidt orthogonalization
    # (Simplified version)
    for i in range(ms_up.shape[2]):
        band = ms_up[:, :, i].astype(float)
        mean_sim = np.mean(simulated)
        mean_band = np.mean(band)
        diff = band - mean_band
        sim_diff = simulated - mean_sim

        # Adjust
        ms_up[:, :, i] = band + diff * (pan - simulated) / (np.std(sim_diff) + 1e-8)

    return ms_up
```

For more code examples, see [code-examples.md](code-examples.md).

### `references/scientific-domains.md`

# Scientific Domain Applications

Geospatial applications across scientific disciplines: marine, atmospheric, hydrology, and more.

## Marine & Coastal GIS

### Coastal Vulnerability Assessment

```python
import geopandas as gpd
import rasterio
import numpy as np

def coastal_vulnerability_index(dem_path, shoreline_path, output_path):
    """Calculate coastal vulnerability index."""

    # 1. Load elevation
    with rasterio.open(dem_path) as src:
        dem = src.read(1)
        transform = src.transform

    # 2. Distance to shoreline
    shoreline = gpd.read_file(shoreline_path)
    # ... calculate distance raster ...

    # 3. Vulnerability criteria (0-1 scale)
    elevation_vuln = 1 - np.clip(dem / 10, 0, 1)  # Lower = more vulnerable
    slope_vuln = 1 - np.clip(slope / 10, 0, 1)

    # 4. Weighted overlay
    weights = {
        'elevation': 0.3,
        'slope': 0.2,
        'distance_to_shore': 0.2,
        'wave_height': 0.2,
        'sea_level_trend': 0.1
    }

    cvi = sum(vuln * w for vuln, w in zip(
        [elevation_vuln, slope_vuln, distance_vuln, wave_vuln, slr_vuln],
        weights.values()
    ))

    return cvi
```

### Marine Habitat Mapping

```python
# Benthic habitat classification
def classify_benthic_habitat(bathymetry, backscatter, derived_layers):
    """
    Classify benthic habitat using:
    - Bathymetry (depth)
    - Backscatter intensity
    - Derived terrain features
    """

    # 1. Extract features
    features = {
        'depth': bathymetry,
        'backscatter': backscatter,
        'slope': calculate_slope(bathymetry),
        'rugosity': calculate_rugosity(bathymetry),
        'curvature': calculate_curvature(bathymetry)
    }

    # 2. Classification rules
    habitat_classes = {}

    # Coral reef: shallow, high rugosity, moderate backscatter
    coral_mask = (
        (features['depth'] > -30) &
        (features['depth'] < -5) &
        (features['rugosity'] > 2) &
        (features['backscatter'] > -15)
    )
    habitat_classes[coral_mask] = 1  # Coral

    # Seagrass: very shallow, low backscatter
    seagrass_mask = (
        (features['depth'] > -15) &
        (features['depth'] < -2) &
        (features['backscatter'] < -20)
    )
    habitat_classes[seagrass_mask] = 2  # Seagrass

    # Sandy bottom: low rugosity
    sand_mask = (
        (features['rugosity'] < 1.5) &
        (features['slope'] < 5)
    )
    habitat_classes[sand_mask] = 3  # Sand

    return habitat_classes
```

## Atmospheric Science

### Weather Data Processing

```python
import xarray as xr
import rioxarray

# Open NetCDF weather data
ds = xr.open_dataset('era5_data.nc')

# Select variable and time
temperature = ds.t2m  # 2m temperature
precipitation = ds.tp  # Total precipitation

# Spatial subsetting
roi = ds.sel(latitude=slice(20, 30), longitude=slice(65, 75))

# Temporal aggregation
monthly = roi.resample(time='1M').mean()
daily = roi.resample(time='1D').sum()

# Export to GeoTIFF
temperature.rio.to_raster('temperature.tif')

# Calculate climate indices
def calculate_spi(precip, scale=3):
    """Standardized Precipitation Index."""
    # Fit gamma distribution
    from scipy import stats
    # ... SPI calculation ...
    return spi
```

### Air Quality Analysis

```python
# PM2.5 interpolation
def interpolate_pm25(sensor_gdf, grid_resolution=1000):
    """
    Interpolate PM2.5 from sensor network.
    Uses IDW or Kriging.
    """
    from pykrige.ok import OrdinaryKriging
    import numpy as np

    # Extract coordinates and values
    lon = sensor_gdf.geometry.x.values
    lat = sensor_gdf.geometry.y.values
    values = sensor_gdf['PM25'].values

    # Create grid
    grid_lon = np.arange(lon.min(), lon.max(), grid_resolution)
    grid_lat = np.arange(lat.min(), lat.max(), grid_resolution)

    # Ordinary Kriging
    OK = OrdinaryKriging(lon, lat, values,
                        variogram_model='exponential',
                        verbose=False,
                        enable_plotting=False)

    # Interpolate
    z, ss = OK.execute('grid', grid_lon, grid_lat)

    return z, grid_lon, grid_lat
```

## Hydrology

### Watershed Delineation

```python
import rasterio
import numpy as np
from scipy import ndimage

def delineate_watershed(dem_path, outlet_point):
    """
    Delineate watershed from DEM and outlet point.
    """

    # 1. Load DEM
    with rasterio.open(dem_path) as src:
        dem = src.read(1)
        transform = src.transform

    # 2. Fill sinks
    filled = fill_sinks(dem)

    # 3. Calculate flow direction (D8 method)
    flow_dir = calculate_flow_direction_d8(filled)

    # 4. Calculate flow accumulation
    flow_acc = calculate_flow_accumulation(flow_dir)

    # 5. Delineate watershed
    # Convert outlet point to raster coordinates
    row, col = ~transform * (outlet_point.x, outlet_point.y)
    row, col = int(row), int(col)

    # Trace upstream
    watershed = trace_upstream(flow_dir, row, col)

    return watershed, flow_acc, flow_dir

def calculate_flow_direction_d8(dem):
    """D8 flow direction algorithm."""
    # Encode direction as powers of 2
    # 32 64 128
    # 16  0   1
    # 8   4   2

    rows, cols = dem.shape
    flow_dir = np.zeros_like(dem, dtype=np.uint8)

    directions = [
        (-1, 0, 64), (-1, 1, 128), (0, 1, 1), (1, 1, 2),
        (1, 0, 4), (1, -1, 8), (0, -1, 16), (-1, -1, 32)
    ]

    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            max_drop = -np.inf
            steepest_dir = 0

            for di, dj, code in directions:
                ni, nj = i + di, j + dj
                drop = dem[i, j] - dem[ni, nj]

                if drop > max_drop and drop > 0:
                    max_drop = drop
                    steepest_dir = code

            flow_dir[i, j] = steepest_dir

    return flow_dir
```

### Flood Inundation Modeling

```python
def flood_inundation(dem, flood_level, roughness=0.03):
    """
    Simple flood inundation modeling.
    """

    # 1. Identify flooded cells
    flooded_mask = dem < flood_level

    # 2. Calculate flood depth
    flood_depth = np.where(flood_mask, flood_level - dem, 0)

    # 3. Remove isolated pixels (connected components)
    labeled, num_features = ndimage.label(flooded_mask)

    # Keep only large components (lakes, not pixels)
    component_sizes = np.bincount(labeled.ravel())
    large_components = component_sizes > 100  # Threshold

    mask_indices = large_components[labeled]
    final_flooded = flooded_mask & mask_indices

    # 4. Flood extent area
    cell_area = 30 * 30  # Assuming 30m resolution
    flooded_area = np.sum(final_flooded) * cell_area

    return flood_depth, final_flooded, flooded_area
```

## Agriculture

### Crop Condition Monitoring

```python
def crop_condition_indices(ndvi_time_series):
    """
    Monitor crop condition using NDVI time series.
    """

    # 1. Calculate growing season metrics
    max_ndvi = np.max(ndvi_time_series)
    time_to_peak = np.argmax(ndvi_time_series)

    # 2. Compare to historical baseline
    baseline_max = 0.8  # From historical data
    condition = (max_ndvi / baseline_max) * 100

    # 3. Classify condition
    if condition > 90:
        status = "Excellent"
    elif condition > 75:
        status = "Good"
    elif condition > 60:
        status = "Fair"
    else:
        status = "Poor"

    # 4. Estimate yield (simplified)
    yield_potential = condition * 0.5  # tonnes/ha

    return {
        'condition': condition,
        'status': status,
        'yield_potential': yield_potential
    }
```

### Precision Agriculture

```python
def prescription_map(soil_data, yield_data, nutrient_data):
    """
    Generate variable rate prescription map.
    """

    # 1. Grid analysis
    # Divide field into management zones
    from sklearn.cluster import KMeans

    features = np.column_stack([
        soil_data['organic_matter'],
        soil_data['ph'],
        yield_data['yield_t'],
        nutrient_data['nitrogen']
    ])

    # Cluster into 3-4 zones
    kmeans = KMeans(n_clusters=3, random_state=42)
    zones = kmeans.fit_predict(features)

    # 2. Prescription rates per zone
    prescriptions = {}
    for zone_id in range(3):
        zone_mask = zones == zone_id
        avg_yield = np.mean(yield_data['yield_t'][zone_mask])

        # Higher yield areas = higher nutrient requirement
        nitrogen_rate = avg_yield * 0.02  # kg N per kg yield
        prescriptions[zone_id] = {
            'nitrogen': nitrogen_rate,
            'phosphorus': nitrogen_rate * 0.3,
            'potassium': nitrogen_rate * 0.4
        }

    return zones, prescriptions
```

## Forestry

### Forest Inventory Analysis

```python
def estimate_biomass_from_lidar(chm_path, plot_data):
    """
    Estimate above-ground biomass from LiDAR CHM.
    """

    # 1. Load Canopy Height Model
    with rasterio.open(chm_path) as src:
        chm = src.read(1)

    # 2. Extract metrics per plot
    metrics = {}
    for plot_id, geom in plot_data.geometry.items():
        # Extract CHM values for plot
        # ... (mask and extract)

        plot_metrics = {
            'height_max': np.max(plot_chm),
            'height_mean': np.mean(plot_chm),
            'height_std': np.std(plot_chm),
            'height_p95': np.percentile(plot_chm, 95),
            'canopy_cover': np.sum(plot_chm > 2) / plot_chm.size
        }

        # 3. Allometric equation for biomass
        # Biomass = a * (height^b) * (cover^c)
        biomass = 0.2 * (plot_metrics['height_mean'] ** 1.5) * \
                  (plot_metrics['canopy_cover'] ** 0.8)

        metrics[plot_id] = {
            **plot_metrics,
            'biomass_tonnes': biomass
        }

    return metrics
```

### Deforestation Detection

```python
def detect_deforestation(image1_path, image2_path, threshold=0.3):
    """
    Detect deforestation between two dates.
    """

    # 1. Load NDVI images
    with rasterio.open(image1_path) as src:
        ndvi1 = src.read(1)
    with rasterio.open(image2_path) as src:
        ndvi2 = src.read(1)

    # 2. Calculate NDVI difference
    ndvi_diff = ndvi2 - ndvi1

    # 3. Detect deforestation (significant NDVI decrease)
    deforestation = ndvi_diff < -threshold

    # 4. Remove small patches
    deforestation_cleaned = remove_small_objects(deforestation, min_size=100)

    # 5. Calculate area
    pixel_area = 900  # m2 (30m resolution)
    deforested_area = np.sum(deforestation_cleaned) * pixel_area

    return deforestation_cleaned, deforested_area
```

For more domain-specific examples, see [code-examples.md](code-examples.md).

### `references/specialized-topics.md`

# Specialized Topics

Advanced specialized topics: geostatistics, optimization, ethics, and best practices.

## Geostatistics

### Variogram Analysis

```python
import numpy as np
from scipy.spatial.distance import pdist, squareform
import matplotlib.pyplot as plt

def empirical_variogram(points, values, max_lag=None, n_lags=15):
    """
    Calculate empirical variogram.
    """
    n = len(points)

    # Distance matrix
    dist_matrix = squareform(pdist(points))

    if max_lag is None:
        max_lag = np.max(dist_matrix) / 2

    # Calculate semivariance
    semivariance = []
    mean_distances = []

    for lag in np.linspace(0, max_lag, n_lags):
        # Pair selection
        mask = (dist_matrix >= lag) & (dist_matrix < lag + max_lag/n_lags)

        if np.sum(mask) == 0:
            continue

        # Semivariance: (1/2n) * sum(z_i - z_j)^2
        diff_squared = (values[:, None] - values) ** 2
        gamma = 0.5 * np.mean(diff_squared[mask])

        semivariance.append(gamma)
        mean_distances.append(lag + max_lag/(2*n_lags))

    return np.array(mean_distances), np.array(semivariance)

# Fit variogram model
def fit_variogram_model(lags, gammas, model='spherical'):
    """
    Fit theoretical variogram model.
    """
    from scipy.optimize import curve_fit

    def spherical(h, nugget, sill, range_):
        """Spherical model."""
        h = np.asarray(h)
        gamma = np.where(h < range_,
                        nugget + sill * (1.5 * h/range_ - 0.5 * (h/range_)**3),
                        nugget + sill)
        return gamma

    def exponential(h, nugget, sill, range_):
        """Exponential model."""
        return nugget + sill * (1 - np.exp(-3 * h / range_))

    def gaussian(h, nugget, sill, range_):
        """Gaussian model."""
        return nugget + sill * (1 - np.exp(-3 * (h/range_)**2))

    models = {
        'spherical': spherical,
        'exponential': exponential,
        'gaussian': gaussian
    }

    # Fit model
    popt, _ = curve_fit(models[model], lags, gammas,
                        p0=[np.min(gammas), np.max(gammas), np.max(lags)/2],
                        bounds=(0, np.inf))

    return popt, models[model]
```

### Kriging Interpolation

```python
from pykrige.ok import OrdinaryKriging
import numpy as np

def ordinary_kriging(x, y, z, grid_resolution=100):
    """
    Perform ordinary kriging interpolation.
    """
    # Create grid
    gridx = np.linspace(x.min(), x.max(), grid_resolution)
    gridy = np.linspace(y.min(), y.max(), grid_resolution)

    # Fit variogram
    OK = OrdinaryKriging(
        x, y, z,
        variogram_model='spherical',
        verbose=False,
        enable_plotting=False,
        coordinates_type='euclidean',
    )

    # Interpolate
    zinterp, sigmasq = OK.execute('grid', gridx, gridy)

    return zinterp, sigmasq, gridx, gridy

# Cross-validation
def kriging_cross_validation(x, y, z, n_folds=5):
    """
    Perform k-fold cross-validation for kriging.
    """
    from sklearn.model_selection import KFold

    kf = KFold(n_splits=n_folds)
    errors = []

    for train_idx, test_idx in kf.split(z):
        # Train
        OK = OrdinaryKriging(
            x[train_idx], y[train_idx], z[train_idx],
            variogram_model='spherical',
            verbose=False
        )

        # Predict at test locations
        predictions, _ = OK.execute('points',
                                    x[test_idx], y[test_idx])

        # Calculate error
        rmse = np.sqrt(np.mean((predictions - z[test_idx])**2))
        errors.append(rmse)

    return np.mean(errors), np.std(errors)
```

## Spatial Optimization

### Location-Allocation Problem

```python
from scipy.optimize import minimize
import numpy as np

def facility_location(demand_points, n_facilities=5):
    """
    Solve p-median facility location problem.
    """

    n_demand = len(demand_points)

    # Distance matrix
    dist_matrix = np.zeros((n_demand, n_demand))
    for i, p1 in enumerate(demand_points):
        for j, p2 in enumerate(demand_points):
            dist_matrix[i, j] = np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

    # Decision variables: which demand points get facilities
    def objective(x):
        """Minimize total weighted distance."""
        # x is binary array of facility locations
        facility_indices = np.where(x > 0.5)[0]

        # Assign each demand to nearest facility
        total_distance = 0
        for i in range(n_demand):
            min_dist = np.min([dist_matrix[i, f] for f in facility_indices])
            total_distance += min_dist

        return total_distance

    # Constraints: exactly n_facilities
    constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - n_facilities}

    # Bounds: binary
    bounds = [(0, 1)] * n_demand

    # Initial guess: random locations
    x0 = np.zeros(n_demand)
    x0[:n_facilities] = 1

    # Solve
    result = minimize(
        objective, x0,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )

    facility_indices = np.where(result.x > 0.5)[0]
    return demand_points[facility_indices]
```

### Routing Optimization

```python
import networkx as nx

def traveling_salesman(G, start_node):
    """
    Solve TSP using heuristic.
    """
    unvisited = set(G.nodes())
    unvisited.remove(start_node)

    route = [start_node]
    current = start_node

    while unvisited:
        # Find nearest unvisited node
        nearest = min(unvisited,
                     key=lambda n: G[current][n].get('weight', 1))
        route.append(nearest)
        unvisited.remove(nearest)
        current = nearest

    # Return to start
    route.append(start_node)

    return route

# Vehicle Routing Problem
def vehicle_routing(G, depot, customers, n_vehicles=3, capacity=100):
    """
    Solve VRP using heuristic (cluster-first, route-second).
    """
    from sklearn.cluster import KMeans

    # 1. Cluster customers
    coords = np.array([[G.nodes[n]['x'], G.nodes[n]['y']] for n in customers])
    kmeans = KMeans(n_clusters=n_vehicles, random_state=42)
    labels = kmeans.fit_predict(coords)

    # 2. Route each cluster
    routes = []
    for i in range(n_vehicles):
        cluster_customers = [customers[j] for j in range(len(customers)) if labels[j] == i]
        route = traveling_salesman(G.subgraph(cluster_customers + [depot]), depot)
        routes.append(route)

    return routes
```

## Ethics and Privacy

### Privacy-Preserving Geospatial Analysis

```python
# Differential privacy for spatial data
def add_dp_noise(locations, epsilon=1.0, radius=100):
    """
    Add differential privacy noise to locations.
    """
    import numpy as np

    noisy_locations = []
    for lon, lat in locations:
        # Calculate noise (Laplace mechanism)
        sensitivity = radius
        scale = sensitivity / epsilon

        noise_lon = np.random.laplace(0, scale)
        noise_lat = np.random.laplace(0, scale)

        noisy_locations.append((lon + noise_lon, lat + noise_lat))

    return noisy_locations

# K-anonymity for trajectory data
def k_anonymize_trajectory(trajectory, k=5):
    """
    Apply k-anonymity to trajectory.
    """
    # 1. Divide into segments
    # 2. Find k-1 similar trajectories
    # 3. Replace segment with generalization

    # Simplified: spatial generalization
    from shapely.geometry import LineString

    simplified = LineString(trajectory).simplify(0.01)
    return list(simplified.coords)
```

### Data Provenance

```python
# Track geospatial data lineage
class DataLineage:
    def __init__(self):
        self.history = []

    def record_transformation(self, input_data, operation, output_data, params):
        """Record data transformation."""
        record = {
            'timestamp': pd.Timestamp.now(),
            'input': input_data,
            'operation': operation,
            'output': output_data,
            'parameters': params
        }
        self.history.append(record)

    def get_lineage(self, data_id):
        """Get complete lineage for a dataset."""
        lineage = []
        for record in reversed(self.history):
            if record['output'] == data_id:
                lineage.append(record)
                lineage.extend(self.get_lineage(record['input']))
        return lineage
```

## Best Practices

### Reproducible Research

```python
# Use environment.yml for dependencies
# environment.yml:
"""
name: geomaster
dependencies:
  - python=3.11
  - geopandas
  - rasterio
  - scikit-learn
  - pip
  - pip:
    - torchgeo
"""

# Capture session info
def capture_environment():
    """Capture software and data versions."""
    import platform
    import geopandas as gpd
    import rasterio
    import numpy as np
    import pandas as pd

    info = {
        'os': platform.platform(),
        'python': platform.python_version(),
        'geopandas': gpd.__version__,
        'rasterio': rasterio.__version__,
        'numpy': np.__version__,
        'pandas': pd.__version__,
        'timestamp': pd.Timestamp.now()
    }

    return info

# Save with output
import json
with open('processing_info.json', 'w') as f:
    json.dump(capture_environment(), f, indent=2, default=str)
```

### Code Organization

```python
# Project structure
"""
project/
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
├── notebooks/
├── src/
│   ├── __init__.py
│   ├── data_loading.py
│   ├── preprocessing.py
│   ├── analysis.py
│   └── visualization.py
├── tests/
├── config.yaml
└── README.md
"""

# Configuration management
import yaml

with open('config.yaml') as f:
    config = yaml.safe_load(f)

# Access parameters
crs = config['projection']['output_crs']
resolution = config['data']['resolution']
```

### Performance Optimization

```python
# Memory profiling
import memory_profiler

@memory_profiler.profile
def process_large_dataset(data_path):
    """Profile memory usage."""
    data = load_data(data_path)
    result = process(data)
    return result

# Vectorization vs loops
# BAD: Iterating rows
for idx, row in gdf.iterrows():
    gdf.loc[idx, 'buffer'] = row.geometry.buffer(100)

# GOOD: Vectorized
gdf['buffer'] = gdf.geometry.buffer(100)

# Chunked processing
def process_in_chunks(gdf, func, chunk_size=1000):
    """Process GeoDataFrame in chunks."""
    results = []
    for i in range(0, len(gdf), chunk_size):
        chunk = gdf.iloc[i:i+chunk_size]
        result = func(chunk)
        results.append(result)
    return pd.concat(results)
```

For more code examples, see [code-examples.md](code-examples.md).

### `references/troubleshooting.md`

# GeoMaster Troubleshooting Guide

Solutions to common geospatial problems and debugging strategies.

## Installation Issues

### GDAL Installation Problems

```bash
# Problem: "gdal-config not found" or rasterio install fails

# Solution 1: Use conda (recommended)
conda install -c conda-forge gdal rasterio

# Solution 2: System packages (Ubuntu/Debian)
sudo apt-get install gdal-bin libgdal-dev
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
uv pip install rasterio

# Solution 3: Wheel files
uv pip install rasterio --find-links=https://gis.wheelwrights.com/

# Verify installation
python -c "from osgeo import gdal; print(gdal.__version__)"
python -c "import rasterio; print(rasterio.__version__)"
```

### Python Binding Issues

```bash
# Problem: "DLL load failed" on Windows
# Solution: Reinstall with conda
conda install -c conda-forge --force-reinstall gdal rasterio fiona

# Problem: "Symbol not found" on macOS
# Solution: Rebuild from source or use conda
brew install gdal
uv pip install rasterio --no-binary rasterio

# Problem: GEOS errors
brew install geos
uv pip install shapely --no-binary shapely
```

## Runtime Errors

### CRS Transformation Errors

```python
# Problem: "Invalid projection" or "CRS mismatch"
import geopandas as gpd

# Check CRS
print(f"CRS: {gdf.crs}")

# If None, set it
if gdf.crs is None:
    gdf.set_crs("EPSG:4326", inplace=True)

# If unknown, try to detect
gdf = gdf.to_crs(gdf.estimate_utm_crs())
```

### Memory Errors with Large Rasters

```python
# Problem: "MemoryError" when reading large files
# Solution: Read in chunks or use windows

import rasterio
from rasterio.windows import Window

# Windowed reading
with rasterio.open('large.tif') as src:
    window = Window(0, 0, 1000, 1000)  # (col_off, row_off, width, height)
    subset = src.read(1, window=window)

# Block-by-block processing
with rasterio.open('large.tif') as src:
    for i, window in src.block_windows(1):
        block = src.read(1, window=window)
        # Process block...

# Use Dask for very large files
import dask.array as da
dask_array = da.from_rasterio('large.tif', chunks=(1, 1024, 1024))
```

### Geometry Validation Errors

```python
# Problem: "TopologyException" or "Self-intersection"
import geopandas as gpd
from shapely.validation import make_valid

# Check invalid geometries
invalid = gdf[~gdf.is_valid]
print(f"Invalid geometries: {len(invalid)}")

# Fix invalid geometries
gdf['geometry'] = gdf.geometry.make_valid()

# Buffer with 0 to fix (alternative method)
gdf['geometry'] = gdf.geometry.buffer(0)
```

### Coordinate Order Confusion

```python
# Problem: Points in wrong location (lon/lat swapped)
from pyproj import Transformer

# Common mistake: lon, lat vs lat, lon
# Always specify axis order
transformer = Transformer.from_crs(
    "EPSG:4326",
    "EPSG:32610",
    always_xy=True  # Input: x=lon, y=lat (not y=lat, x=lon)
)

# Correct usage
x, y = transformer.transform(lon, lat)  # not lat, lon
```

## Performance Issues

### Slow Spatial Joins

```python
# Problem: sjoin takes too long
import geopandas as gpd

# Solution: Use spatial index
gdf1.sindex  # Auto-created
gdf2.sindex

# For nearest neighbor joins, use specialized function
result = gpd.sjoin_nearest(gdf1, gdf2, max_distance=1000)

# Use intersection predicate (faster than 'intersects' for points)
result = gpd.sjoin(points, polygons, predicate='within')

# Clip to bounding box first
bbox = gdf1.total_bounds
gdf2_clipped = gdf2.cx[bbox[0]:bbox[2], bbox[1]:bbox[3]]
result = gpd.sjoin(gdf1, gdf2_clipped, predicate='intersects')
```

### Slow Raster I/O

```python
# Problem: Reading/writing rasters is slow
import rasterio

# Solution 1: Use compression when writing
profile.update(
    compress='DEFLATE',
    predictor=2,
    zlevel=4
)

# Solution 2: Use tiled output
profile.update(
    tiled=True,
    blockxsize=256,
    blockysize=256
)

# Solution 3: Enable caching
from osgeo import gdal
gdal.SetCacheMax(2**30)  # 1GB

# Solution 4: Use COG format for cloud access
from rio_cogeo.cogeo import cog_translate
cog_translate('input.tif', 'output.tif', profile)
```

### Slow Reprojection

```python
# Problem: to_crs() is very slow
import geopandas as gpd

# Solution 1: Simplify geometry first
gdf_simple = gdf.geometry.simplify(tolerance=0.0001)
gdf_reproj = gdf_simple.to_crs(target_crs)

# Solution 2: Use lower precision for display
gdf_reproj = gdf.to_crs(target_crs, geometry_precision=2)

# Solution 3: Reproject in parallel
import multiprocessing as mp
from functools import partial

def reproj_chunk(chunk, target_crs):
    return chunk.to_crs(target_crs)

chunks = np.array_split(gdf, mp.cpu_count())
with mp.Pool() as pool:
    results = pool.map(partial(reproj_chunk, target_crs=target_crs), chunks)
gdf_reproj = gpd.GeoDataFrame(pd.concat(results))
```

## Common Pitfalls

### Area in Degrees

```python
# WRONG: Area in square degrees
gdf = gpd.read_file('data.geojson')
area = gdf.geometry.area  # Wrong!

# CORRECT: Use projected CRS
gdf_proj = gdf.to_crs(gdf.estimate_utm_crs())
area_sqm = gdf_proj.geometry.area
area_sqkm = area_sqm / 1_000_000
```

### Buffer in Geographic CRS

```python
# WRONG: Buffer of 1000 degrees
gdf['buffer'] = gdf.geometry.buffer(1000)

# CORRECT: Project first
gdf_proj = gdf.to_crs("EPSG:32610")
gdf_proj['buffer_km'] = gdf_proj.geometry.buffer(1000)  # 1000 meters
```

### Web Mercator Distortion

```python
# WRONG: Area calculation in Web Mercator
gdf = gdf.to_crs("EPSG:3857")
area = gdf.geometry.area  # Significant distortion!

# CORRECT: Use appropriate projection
gdf = gdf.to_crs(gdf.estimate_utm_crs())
area = gdf.geometry.area  # Accurate
```

### Mixing CRS

```python
# WRONG: Spatial join without checking CRS
result = gpd.sjoin(gdf1, gdf2, predicate='intersects')

# CORRECT: Ensure same CRS
if gdf1.crs != gdf2.crs:
    gdf2 = gdf2.to_crs(gdf1.crs)
result = gpd.sjoin(gdf1, gdf2, predicate='intersects')
```

## Data Issues

### Missing/Missing CRS

```python
# Problem: CRS is None
gdf = gpd.read_file('data.geojson')
if gdf.crs is None:
    # Try to detect from data extent
    lon_min, lat_min, lon_max, lat_max = gdf.total_bounds

    if -180 <= lon_min <= 180 and -90 <= lat_min <= 90:
        gdf.set_crs("EPSG:4326", inplace=True)
        print("Assumed WGS 84 (EPSG:4326)")
    else:
        gdf.set_crs(gdf.estimate_utm_crs(), inplace=True)
        print("Estimated UTM zone")
```

### Invalid Coordinates

```python
# Problem: Coordinates out of valid range
gdf = gpd.read_file('data.geojson')

# Check for invalid coordinates
invalid_lon = (gdf.geometry.x < -180) | (gdf.geometry.x > 180)
invalid_lat = (gdf.geometry.y < -90) | (gdf.geometry.y > 90)

if invalid_lon.any() or invalid_lat.any():
    print("Warning: Invalid coordinates found")
    gdf = gdf[~invalid_lon & ~invalid_lat]
```

### Empty Geometries

```python
# Problem: Processing fails with empty geometries
# Remove empty geometries
gdf = gdf[~gdf.geometry.is_empty]

# Or fill with None
gdf.loc[gdf.geometry.is_empty, 'geometry'] = None

# Check before operations
if gdf.geometry.is_empty.any():
    print(f"Warning: {gdf.geometry.is_empty.sum()} empty geometries")
```

## Remote Sensing Issues

### Sentinel-2 Band Ordering

```python
# Problem: Wrong band indices
# Sentinel-2 L2A SAFE structure:
# B01 (60m), B02 (10m), B03 (10m), B04 (10m), B05 (20m),
# B06 (20m), B07 (20m), B08 (10m), B08A (20m), B09 (60m),
# B11 (20m), B12 (20m)

# Sentinel-2 (resampled to 10m):
# B02=1, B03=2, B04=3, B05=4, B06=5, B07=6, B08=7, B8A=8, B11=9, B12=10

# For 10m bands only:
blue = src.read(1)   # B02
green = src.read(2)  # B03
red = src.read(3)    # B04
nir = src.read(4)    # B08
```

### Cloud Shadow Masking

```python
# Problem: Clouds and shadows not properly masked
def improved_cloud_mask(scl):
    """
    Improved cloud masking using SCL layer.
    Classes: 0=No data, 1=Saturated, 2=Dark, 3=Cloud shadow,
    4=Vegetation, 5=Bare soil, 6=Water, 7=Cloud low prob,
    8=Cloud med prob, 9=Cloud high prob, 10=Thin cirrus
    """
    # Mask: clouds, cloud shadows, saturated
    mask = scl.isin([0, 1, 3, 8, 9, 10])
    return mask

# Apply
scl = s2_image.select('SCL')
cloud_mask = improved_cloud_mask(scl)
image_clean = s2_image.updateMask(cloud_mask.Not())
```

## Error Messages Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `CRS mismatch` | Different coordinate systems | `gdf2 = gdf2.to_crs(gdf1.crs)` |
| `TopologyException` | Invalid/self-intersecting geometry | `gdf.geometry = gdf.geometry.make_valid()` |
| `MemoryError` | Large dataset | Use Dask or chunked reading |
| `Invalid projection` | Unknown CRS code | Check EPSG code, use `CRS.from_user_input()` |
| `Empty geometry` | Null geometries | `gdf = gdf[~gdf.geometry.is_empty]` |
| `Bounds error` | Coordinates out of range | Filter invalid coordinates |
| `DLL load failed` | GDAL not installed | Use conda: `conda install gdal` |
| `Symbol not found` | Library linking issue | Reinstall with binary wheels or conda |
| `Self-intersection` | Invalid polygon | Buffer(0) or make_valid() |

## Debugging Strategies

### 1. Check Data Integrity

```python
def check_geodataframe(gdf):
    """Comprehensive GeoDataFrame health check."""
    print(f"Shape: {gdf.shape}")
    print(f"CRS: {gdf.crs}")
    print(f"Bounds: {gdf.total_bounds}")
    print(f"Invalid geometries: {(~gdf.is_valid).sum()}")
    print(f"Empty geometries: {gdf.geometry.is_empty.sum()}")
    print(f"None geometries: {gdf.geometry.isna().sum()}")
    print(f"Duplicate geometries: {gdf.geometry.duplicated().sum()}")
    print("\nGeometry types:")
    print(gdf.geometry.type.value_counts())
    print("\nCoordinate range:")
    print(f"  X: {gdf.geometry.x.min():.2f} to {gdf.geometry.x.max():.2f}")
    print(f"  Y: {gdf.geometry.y.min():.2f} to {gdf.geometry.y.max():.2f}")

check_geodataframe(gdf)
```

### 2. Test Transformations

```python
def test_reprojection(gdf, target_crs):
    """Test if reprojection is reversible."""
    original = gdf.copy()
    gdf_proj = gdf.to_crs(target_crs)
    gdf_back = gdf_proj.to_crs(gdf.crs)

    diff = original.geometry.distance(gdf_back.geometry).max()
    if diff > 1:  # More than 1 meter
        print(f"Warning: Max error: {diff:.2f}m")
        return False
    return True
```

### 3. Profile Code

```python
import time

def time_operation(func, *args, **kwargs):
    """Time a geospatial operation."""
    start = time.time()
    result = func(*args, **kwargs)
    elapsed = time.time() - start
    print(f"{func.__name__}: {elapsed:.2f}s")
    return result

# Usage
time_operation(gdf.to_crs, "EPSG:32610")
```

## Getting Help

### Check Versions

```python
import sys
import geopandas as gpd
import rasterio
from osgeo import gdal

print(f"Python: {sys.version}")
print(f"GeoPandas: {gpd.__version__}")
print(f"Rasterio: {rasterio.__version__}")
print(f"GDAL: {gdal.__version__}")
print(f"PROJ: {gdal.VersionInfo('PROJ')}")
```

### Useful Resources

- **GeoPandas docs**: https://geopandas.org/
- **Rasterio docs**: https://rasterio.readthedocs.io/
- **PROJ datab**: https://epsg.org/
- **Stack Overflow**: Tag with `gis` and `python`
- **GIS Stack Exchange**: https://gis.stackexchange.com/

### `README.md`

# GeoMaster Geospatial Science Skill

## Overview

GeoMaster is a comprehensive geospatial science skill covering:
- **70+ sections** on geospatial science topics
- **500+ code examples** across 7 programming languages
- **300+ geospatial libraries** and tools
- Remote sensing, GIS, spatial statistics, ML/AI for Earth observation

## Contents

### Main Documentation
- **SKILL.md** - Main skill documentation with installation, quick start, core concepts, common operations, and workflows

### Reference Documentation
1. **core-libraries.md** - GDAL, Rasterio, Fiona, Shapely, PyProj, GeoPandas
2. **remote-sensing.md** - Satellite missions, optical/SAR/hyperspectral analysis, image processing
3. **gis-software.md** - QGIS/PyQGIS, ArcGIS/ArcPy, GRASS GIS, SAGA GIS integration
4. **scientific-domains.md** - Marine, atmospheric, hydrology, agriculture, forestry applications
5. **advanced-gis.md** - 3D GIS, spatiotemporal analysis, topology, network analysis
6. **programming-languages.md** - R, Julia, JavaScript, C++, Java, Go geospatial tools
7. **machine-learning.md** - Deep learning for RS, spatial ML, GNNs, XAI for geospatial
8. **big-data.md** - Distributed processing, cloud platforms, GPU acceleration
9. **industry-applications.md** - Urban planning, disaster management, utilities, transportation
10. **specialized-topics.md** - Geostatistics, optimization, ethics, best practices
11. **data-sources.md** - Satellite data catalogs, open data repositories, API access
12. **code-examples.md** - 500+ code examples across 7 programming languages

## Key Topics Covered

### Remote Sensing
- Sentinel-1/2/3, Landsat, MODIS, Planet, Maxar
- SAR, hyperspectral, LiDAR, thermal imaging
- Spectral indices, classification, change detection

### GIS Operations
- Vector data (points, lines, polygons)
- Raster data processing
- Coordinate reference systems
- Spatial analysis and statistics

### Machine Learning
- Random Forest, SVM, CNN, U-Net
- Spatial statistics, geostatistics
- Graph neural networks
- Explainable AI

### Programming Languages
- **Python** - GDAL, Rasterio, GeoPandas, TorchGeo, RSGISLib
- **R** - sf, terra, raster, stars
- **Julia** - ArchGDAL, GeoStats.jl
- **JavaScript** - Turf.js, Leaflet
- **C++** - GDAL C++ API
- **Java** - GeoTools
- **Go** - Simple Features Go

## Installation

See [SKILL.md](SKILL.md) for detailed installation instructions.

### Core Python Stack
```bash
conda install -c conda-forge gdal rasterio fiona shapely pyproj geopandas
```

### Remote Sensing
```bash
uv pip install rsgislib torchgeo earthengine-api
```

## Quick Examples

### Calculate NDVI from Sentinel-2
```python
import rasterio
import numpy as np

with rasterio.open('sentinel2.tif') as src:
    red = src.read(4)
    nir = src.read(8)
    ndvi = (nir - red) / (nir + red + 1e-8)
```

### Spatial Analysis with GeoPandas
```python
import geopandas as gpd

zones = gpd.read_file('zones.geojson')
points = gpd.read_file('points.geojson')
joined = gpd.sjoin(points, zones, predicate='within')
```

## License

MIT License

## Author

K-Dense Inc.

## Contributing

This skill is part of the K-Dense-AI/scientific-agent-skills repository.
For contributions, see the main repository guidelines.
