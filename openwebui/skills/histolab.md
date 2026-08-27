---
name: histolab
description: Lightweight WSI tile extraction and preprocessing. Use for basic slide processing, tissue detection, tile extraction, and stain normalization for H&E images. Best for simple pipelines, dataset preparation, and quick tile-based analysis. For advanced spatial proteomics, multiplexed imaging, or deep learning pipelines use pathml.
---

# Histolab

## Overview

Histolab is a Python library for processing whole slide images (WSI) in digital pathology. It automates tissue detection, extracts informative tiles from gigapixel images, and prepares datasets for deep learning pipelines. The library handles multiple WSI formats, implements sophisticated tissue segmentation, and provides flexible tile extraction strategies.

## Installation

Install OpenSlide system libraries first ([OpenSlide download](https://openslide.org/download/)), then install histolab:

```bash
uv pip install histolab
```

For built-in TCGA sample slides via `histolab.data`, also install pooch:

```bash
uv pip install pooch
```

Histolab 0.7.0 (latest stable) supports Python 3.8–3.11 on Linux and macOS. Windows is not supported as of 0.7.0.

## Quick Start

Basic workflow for extracting tiles from a whole slide image:

```python
from histolab.slide import Slide
from histolab.tiler import RandomTiler

# Load slide
slide = Slide("slide.svs", processed_path="output/")

# Configure tiler
tiler = RandomTiler(
    tile_size=(512, 512),
    n_tiles=100,
    level=0,
    seed=42
)

# Preview tile locations
tiler.locate_tiles(slide, n_tiles=20)

# Extract tiles
tiler.extract(slide)
```

## Core Capabilities

Six capability areas, each with worked code, are documented in
[references/core_capabilities.md](references/core_capabilities.md):

1. **Slide management** — opening slides, properties, levels, thumbnails, and scaled images.
2. **Tissue detection and masks** — `TissueMask` and `BiggestTissueBoxMask`, and custom masks.
3. **Tile extraction** — random, grid, and score-based tilers with size, level, and
   tissue-fraction control.
4. **Filters and preprocessing** — image and morphological filters, and composing them.
5. **Stain normalization** — Reinhard and Macenko normalization against a target image.
6. **Visualization** — locating tiles on the slide and inspecting masks and extractions.

Five end-to-end workflows are in
[references/typical_workflows.md](references/typical_workflows.md). Per-topic detail lives
in [references/slide_management.md](references/slide_management.md),
[references/tissue_masks.md](references/tissue_masks.md),
[references/tile_extraction.md](references/tile_extraction.md),
[references/filters_preprocessing.md](references/filters_preprocessing.md), and
[references/visualization.md](references/visualization.md).

## Best Practices

### Slide Loading and Inspection
1. Always inspect slide properties before processing
2. Save thumbnails with `slide.thumbnail.save()` for quick visual review
3. Check pyramid levels and dimensions
4. Verify tissue is present using thumbnails

### Tissue Detection
1. Preview masks with `locate_mask()` before extraction
2. Use `TissueMask` for multiple sections, `BiggestTissueBoxMask` for single sections
3. Customize filters for specific stains (H&E vs IHC)
4. Handle pen annotations with custom masks
5. Test masks on diverse slides

### Tile Extraction
1. **Always preview with `locate_tiles()` before extracting**
2. Choose appropriate tiler:
   - RandomTiler: Sampling and exploration
   - GridTiler: Complete coverage
   - ScoreTiler: Quality-driven selection
3. Set appropriate `tissue_percent` threshold (70-90% typical)
4. Use seeds for reproducibility in RandomTiler
5. Extract at appropriate pyramid level for analysis resolution
6. Enable logging for large datasets

### Performance
1. Extract at lower levels (1, 2) for faster processing
2. Use `BiggestTissueBoxMask` over `TissueMask` when appropriate
3. Adjust `tissue_percent` to reduce invalid tile attempts
4. Limit `n_tiles` for initial exploration
5. Use `pixel_overlap=0` for non-overlapping grids

### Quality Control
1. Validate tile quality (check for blur, artifacts, focus)
2. Review score distributions for ScoreTiler
3. Inspect top and bottom scoring tiles
4. Monitor tissue coverage statistics
5. Filter extracted tiles by additional quality metrics if needed

## Common Use Cases

### Training Deep Learning Models
- Extract balanced datasets using RandomTiler across multiple slides
- Use ScoreTiler with NucleiScorer to focus on cell-rich regions
- Extract at consistent resolution (level 0 or level 1)
- Generate CSV reports for tracking tile metadata

### Whole Slide Analysis
- Use GridTiler for complete tissue coverage
- Extract at multiple pyramid levels for hierarchical analysis
- Maintain spatial relationships with grid positions
- Use `pixel_overlap` for sliding window approaches

### Tissue Characterization
- Sample diverse regions with RandomTiler
- Quantify tissue coverage with masks
- Extract stain-specific information with HED decomposition
- Compare tissue patterns across slides

### Quality Assessment
- Identify optimal focus regions with ScoreTiler
- Detect artifacts using custom masks and filters
- Assess staining quality across slide collection
- Flag problematic slides for manual review

### Dataset Curation
- Use ScoreTiler to prioritize informative tiles
- Filter tiles by tissue percentage
- Generate reports with tile scores and metadata
- Create stratified datasets across slides and tissue types

## Troubleshooting

### No tiles extracted
- Lower `tissue_percent` threshold
- Verify slide contains tissue (check thumbnail)
- Ensure extraction_mask captures tissue regions
- Check tile_size is appropriate for slide resolution

### Many background tiles
- Enable `check_tissue=True`
- Increase `tissue_percent` threshold
- Use appropriate mask (TissueMask vs BiggestTissueBoxMask)
- Customize mask filters to better detect tissue

### Extraction very slow
- Extract at lower pyramid level (level=1 or 2)
- Reduce `n_tiles` for RandomTiler/ScoreTiler
- Use RandomTiler instead of GridTiler for sampling
- Use BiggestTissueBoxMask instead of TissueMask

### Tiles have artifacts
- Implement custom annotation-exclusion masks
- Adjust filter parameters for artifact removal
- Increase small object removal threshold
- Apply post-extraction quality filtering

### Inconsistent results across slides
- Use same seed for RandomTiler
- Normalize staining with `MacenkoStainNormalizer` or `ReinhardStainNormalizer`
- Adjust `tissue_percent` per staining quality
- Implement slide-specific mask customization

## Resources

This skill includes detailed reference documentation in the `references/` directory:

### references/slide_management.md
Comprehensive guide to loading, inspecting, and working with whole slide images:
- Slide initialization and configuration
- Built-in sample datasets
- Slide properties and metadata
- Thumbnail generation and visualization
- Working with pyramid levels
- Multi-slide processing workflows
- Best practices and common patterns

### references/tissue_masks.md
Complete documentation on tissue detection and masking:
- TissueMask, BiggestTissueBoxMask, BinaryMask classes
- How tissue detection filters work
- Customizing masks with filter chains
- Visualizing masks
- Creating custom rectangular and annotation-exclusion masks
- Integration with tile extraction
- Best practices and troubleshooting

### references/tile_extraction.md
Detailed explanation of tile extraction strategies:
- RandomTiler, GridTiler, ScoreTiler comparison
- Available scorers (NucleiScorer, CellularityScorer, custom)
- Common and strategy-specific parameters
- Tile preview with locate_tiles()
- Extraction workflows and CSV reporting
- Advanced patterns (multi-level, hierarchical)
- Performance optimization
- Troubleshooting common issues

### references/filters_preprocessing.md
Complete filter reference and preprocessing guide:
- Image filters (color conversion, thresholding, contrast)
- Morphological filters (dilation, erosion, opening, closing)
- Filter composition and chaining
- Built-in stain normalization (Macenko, Reinhard) and filter-based alternatives
- Common preprocessing pipelines
- Applying filters to tiles
- Custom mask filters
- Quality control filters
- Best practices and troubleshooting

### references/visualization.md
Comprehensive visualization guide:
- Slide thumbnail display and saving
- Mask visualization techniques
- Tile location preview
- Displaying extracted tiles and creating mosaics
- Quality assessment visualizations
- Multi-slide comparison
- Filter effect visualization
- Exporting high-resolution figures and PDFs
- Interactive visualization in Jupyter notebooks

**Usage pattern:** Reference files contain in-depth information to support workflows described in this main skill document. Load specific reference files as needed for detailed implementation guidance, troubleshooting, or advanced features.

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/histolab/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/core_capabilities.md`

# Histolab Core Capabilities

Slide management, tissue detection and masks, tile extraction, filters and preprocessing,
stain normalization, and visualization, each with worked code.

## Core Capabilities

### 1. Slide Management

Load, inspect, and work with whole slide images in various formats.

**Common operations:**
- Loading WSI files (SVS, TIFF, NDPI, etc.)
- Accessing slide metadata (dimensions, magnification, properties)
- Generating thumbnails for visualization
- Working with pyramidal image structures
- Extracting regions at specific coordinates

**Key classes:** `Slide`

**Reference:** `references/slide_management.md` contains comprehensive documentation on:
- Slide initialization and configuration
- Built-in sample datasets (prostate, ovarian, breast, heart, kidney tissues)
- Accessing slide properties and metadata
- Thumbnail generation and visualization
- Working with pyramid levels
- Multi-slide processing workflows

**Example workflow:**
```python
from histolab.slide import Slide
from histolab.data import prostate_tissue

# Load sample data
prostate_svs, prostate_path = prostate_tissue()

# Initialize slide
slide = Slide(prostate_path, processed_path="output/")

# Inspect properties
print(f"Dimensions: {slide.dimensions}")
print(f"Levels: {slide.levels}")
print(f"Magnification: {slide.properties.get('openslide.objective-power')}")

# Save thumbnail to processed_path
from pathlib import Path
Path(slide.processed_path).mkdir(parents=True, exist_ok=True)
slide.thumbnail.save(Path(slide.processed_path) / f"{slide.name}_thumbnail.png")
```

### 2. Tissue Detection and Masks

Automatically identify tissue regions and filter background/artifacts.

**Common operations:**
- Creating binary tissue masks
- Detecting largest tissue region
- Excluding background and artifacts
- Custom tissue segmentation
- Removing pen annotations

**Key classes:** `TissueMask`, `BiggestTissueBoxMask`, `BinaryMask`

**Reference:** `references/tissue_masks.md` contains comprehensive documentation on:
- TissueMask: Segments all tissue regions using automated filters
- BiggestTissueBoxMask: Returns bounding box of largest tissue region (default)
- BinaryMask: Base class for custom mask implementations
- Visualizing masks with `locate_mask()`
- Creating custom rectangular and annotation-exclusion masks
- Mask integration with tile extraction
- Best practices and troubleshooting

**Example workflow:**
```python
from histolab.masks import TissueMask, BiggestTissueBoxMask

# Create tissue mask for all tissue regions
tissue_mask = TissueMask()

# Visualize mask on slide
slide.locate_mask(tissue_mask)

# Get mask array
mask_array = tissue_mask(slide)

# Use largest tissue region (default for most extractors)
biggest_mask = BiggestTissueBoxMask()
```

**When to use each mask:**
- `TissueMask`: Multiple tissue sections, comprehensive analysis
- `BiggestTissueBoxMask`: Single main tissue section, exclude artifacts (default)
- Custom `BinaryMask`: Specific ROI, exclude annotations, custom segmentation

### 3. Tile Extraction

Extract smaller regions from large WSI using different strategies.

**Three extraction strategies:**

**RandomTiler:** Extract fixed number of randomly positioned tiles
- Best for: Sampling diverse regions, exploratory analysis, training data
- Key parameters: `n_tiles`, `seed` for reproducibility

**GridTiler:** Systematically extract tiles across tissue in grid pattern
- Best for: Complete coverage, spatial analysis, reconstruction
- Key parameters: `pixel_overlap` for sliding windows

**ScoreTiler:** Extract top-ranked tiles based on scoring functions
- Best for: Most informative regions, quality-driven selection
- Key parameters: `scorer` (NucleiScorer, CellularityScorer, custom)

**Common parameters:**
- `tile_size`: Tile dimensions (e.g., (512, 512))
- `level`: Pyramid level for extraction (0 = highest resolution)
- `check_tissue`: Filter tiles by tissue content
- `tissue_percent`: Minimum tissue coverage (default 80%)
- `extraction_mask`: Mask defining extraction region

**Reference:** `references/tile_extraction.md` contains comprehensive documentation on:
- Detailed explanation of each tiler strategy
- Available scorers (NucleiScorer, CellularityScorer, custom)
- Tile preview with `locate_tiles()`
- Extraction workflows and reporting
- Advanced patterns (multi-level, hierarchical extraction)
- Performance optimization and troubleshooting

**Example workflows:**

```python
from histolab.tiler import RandomTiler, GridTiler, ScoreTiler
from histolab.scorer import NucleiScorer

# Random sampling (fast, diverse)
random_tiler = RandomTiler(
    tile_size=(512, 512),
    n_tiles=100,
    level=0,
    seed=42,
    check_tissue=True,
    tissue_percent=80.0
)
random_tiler.extract(slide)

# Grid coverage (comprehensive)
grid_tiler = GridTiler(
    tile_size=(512, 512),
    level=0,
    pixel_overlap=0,
    check_tissue=True
)
grid_tiler.extract(slide)

# Score-based selection (most informative)
score_tiler = ScoreTiler(
    tile_size=(512, 512),
    n_tiles=50,
    scorer=NucleiScorer(),
    level=0
)
score_tiler.extract(slide, report_path="tiles_report.csv")
```

**Always preview before extracting:**
```python
# Preview tile locations on thumbnail
tiler.locate_tiles(slide, n_tiles=20)
```

### 4. Filters and Preprocessing

Apply image processing filters for tissue detection, quality control, and preprocessing.

**Filter categories:**

**Image Filters:** Color space conversions, thresholding, contrast enhancement
- `RgbToGrayscale`, `RgbToHsv`, `RgbToHed`
- `OtsuThreshold`, `AdaptiveThreshold`
- `StretchContrast`, `HistogramEqualization`

**Morphological Filters:** Structural operations on binary images
- `BinaryDilation`, `BinaryErosion`
- `BinaryOpening`, `BinaryClosing`
- `RemoveSmallObjects`, `RemoveSmallHoles`

**Composition:** Chain multiple filters together
- `Compose`: Create filter pipelines

**Reference:** `references/filters_preprocessing.md` contains comprehensive documentation on:
- Detailed explanation of each filter type
- Filter composition and chaining
- Common preprocessing pipelines (tissue detection, pen removal, nuclei enhancement)
- Applying filters to tiles
- Custom mask filters
- Quality control filters (blur detection, tissue coverage)
- Best practices and troubleshooting

**Example workflows:**

```python
from histolab.filters.compositions import Compose
from histolab.filters.image_filters import RgbToGrayscale, OtsuThreshold
from histolab.filters.morphological_filters import (
    BinaryDilation, RemoveSmallHoles, RemoveSmallObjects
)

# Standard tissue detection pipeline
tissue_detection = Compose([
    RgbToGrayscale(),
    OtsuThreshold(),
    BinaryDilation(disk_size=5),
    RemoveSmallHoles(area_threshold=1000),
    RemoveSmallObjects(area_threshold=500)
])

# Use with custom mask
from histolab.masks import TissueMask
custom_mask = TissueMask(filters=tissue_detection)

# Apply filters to tile
from histolab.tile import Tile
filtered_tile = tile.apply_filters(tissue_detection)
```

### 5. Stain Normalization

Standardize staining appearance across slides for deep learning (added in histolab 0.6.0).

**Key classes:** `MacenkoStainNormalizer`, `ReinhardStainNormalizer`

```python
from histolab.stain_normalizer import MacenkoStainNormalizer, ReinhardStainNormalizer
from PIL import Image

target = Image.open("reference_stain.png")  # Style reference slide/tile
source = Image.open("slide_to_normalize.png")

normalizer = MacenkoStainNormalizer()
normalizer.fit(target)
normalized = normalizer.transform(source)
normalized.save("normalized.png")
```

Use `ReinhardStainNormalizer()` for Reinhard color transfer. Fit on a representative target image, then transform source tiles or thumbnails. See `references/filters_preprocessing.md` for filter-based alternatives.

### 6. Visualization

Visualize slides, masks, tile locations, and extraction quality.

**Common visualization tasks:**
- Displaying slide thumbnails
- Visualizing tissue masks
- Previewing tile locations
- Assessing tile quality
- Creating reports and figures

**Reference:** `references/visualization.md` contains comprehensive documentation on:
- Slide thumbnail display and saving
- Mask visualization with `locate_mask()`
- Tile location preview with `locate_tiles()`
- Displaying extracted tiles and mosaics
- Quality assessment (score distributions, top vs bottom tiles)
- Multi-slide visualization
- Filter effect visualization
- Exporting high-resolution figures and PDF reports
- Interactive visualization in Jupyter notebooks

**Example workflows:**

```python
import matplotlib.pyplot as plt
from histolab.masks import TissueMask

# Display slide thumbnail
plt.figure(figsize=(10, 10))
plt.imshow(slide.thumbnail)
plt.title(f"Slide: {slide.name}")
plt.axis('off')
plt.show()

# Visualize tissue mask
tissue_mask = TissueMask()
slide.locate_mask(tissue_mask)

# Preview tile locations
tiler = RandomTiler(tile_size=(512, 512), n_tiles=50)
tiler.locate_tiles(slide, n_tiles=20)

# Display extracted tiles in grid
from pathlib import Path
from PIL import Image

tile_paths = list(Path("output/tiles/").glob("*.png"))[:16]
fig, axes = plt.subplots(4, 4, figsize=(12, 12))
axes = axes.ravel()

for idx, tile_path in enumerate(tile_paths):
    tile_img = Image.open(tile_path)
    axes[idx].imshow(tile_img)
    axes[idx].set_title(tile_path.stem, fontsize=8)
    axes[idx].axis('off')

plt.tight_layout()
plt.show()
```

### `references/filters_preprocessing.md`

# Filters and Preprocessing

## Overview

Histolab provides a comprehensive set of filters for preprocessing whole slide images and tiles. Filters can be applied to images for visualization, quality control, tissue detection, and artifact removal. They are composable and can be chained together to create sophisticated preprocessing pipelines.

## Filter Categories

### Image Filters
Color space conversions, thresholding, and intensity adjustments

### Morphological Filters
Structural operations like dilation, erosion, opening, and closing

### Composition Filters
Utilities for combining multiple filters

## Image Filters

### RgbToGrayscale

Convert RGB images to grayscale.

```python
from histolab.filters.image_filters import RgbToGrayscale

gray_filter = RgbToGrayscale()
gray_image = gray_filter(rgb_image)
```

**Use cases:**
- Preprocessing for intensity-based operations
- Simplifying color complexity
- Input for morphological operations

### RgbToHsv

Convert RGB to HSV (Hue, Saturation, Value) color space.

```python
from histolab.filters.image_filters import RgbToHsv

hsv_filter = RgbToHsv()
hsv_image = hsv_filter(rgb_image)
```

**Use cases:**
- Color-based tissue segmentation
- Detecting pen markings by hue
- Separating chromatic from achromatic content

### RgbToHed

Convert RGB to HED (Hematoxylin-Eosin-DAB) color space for stain deconvolution.

```python
from histolab.filters.image_filters import RgbToHed

hed_filter = RgbToHed()
hed_image = hed_filter(rgb_image)
```

**Use cases:**
- Separating H&E stain components
- Analyzing nuclear (hematoxylin) vs. cytoplasmic (eosin) staining
- Quantifying stain intensity

### OtsuThreshold

Apply Otsu's automatic thresholding method to create binary images.

```python
from histolab.filters.image_filters import OtsuThreshold

otsu_filter = OtsuThreshold()
binary_image = otsu_filter(grayscale_image)
```

**How it works:**
- Automatically determines optimal threshold
- Separates foreground from background
- Minimizes intra-class variance

**Use cases:**
- Tissue detection
- Nuclei segmentation
- Binary mask creation

### AdaptiveThreshold

Apply adaptive thresholding for local intensity variations.

```python
from histolab.filters.image_filters import AdaptiveThreshold

adaptive_filter = AdaptiveThreshold(
    block_size=11,      # Size of local neighborhood
    offset=2            # Constant subtracted from mean
)
binary_image = adaptive_filter(grayscale_image)
```

**Use cases:**
- Non-uniform illumination
- Local contrast enhancement
- Handling variable staining intensity

### Invert

Invert image intensity values.

```python
from histolab.filters.image_filters import Invert

invert_filter = Invert()
inverted_image = invert_filter(image)
```

**Use cases:**
- Preprocessing for certain segmentation algorithms
- Visualization adjustments

### StretchContrast

Enhance image contrast by stretching intensity range.

```python
from histolab.filters.image_filters import StretchContrast

contrast_filter = StretchContrast()
enhanced_image = contrast_filter(image)
```

**Use cases:**
- Improving visibility of low-contrast features
- Preprocessing for visualization
- Enhancing faint structures

### HistogramEqualization

Equalize image histogram for contrast enhancement.

```python
from histolab.filters.image_filters import HistogramEqualization

hist_eq_filter = HistogramEqualization()
equalized_image = hist_eq_filter(grayscale_image)
```

**Use cases:**
- Standardizing image contrast
- Revealing hidden details
- Preprocessing for feature extraction

## Morphological Filters

### BinaryDilation

Expand white regions in binary images.

```python
from histolab.filters.morphological_filters import BinaryDilation

dilation_filter = BinaryDilation(disk_size=5)
dilated_image = dilation_filter(binary_image)
```

**Parameters:**
- `disk_size`: Size of structuring element (default: 5)

**Use cases:**
- Connecting nearby tissue regions
- Filling small gaps
- Expanding tissue masks

### BinaryErosion

Shrink white regions in binary images.

```python
from histolab.filters.morphological_filters import BinaryErosion

erosion_filter = BinaryErosion(disk_size=5)
eroded_image = erosion_filter(binary_image)
```

**Use cases:**
- Removing small protrusions
- Separating connected objects
- Shrinking tissue boundaries

### BinaryOpening

Erosion followed by dilation (removes small objects).

```python
from histolab.filters.morphological_filters import BinaryOpening

opening_filter = BinaryOpening(disk_size=3)
opened_image = opening_filter(binary_image)
```

**Use cases:**
- Removing small artifacts
- Smoothing object boundaries
- Noise reduction

### BinaryClosing

Dilation followed by erosion (fills small holes).

```python
from histolab.filters.morphological_filters import BinaryClosing

closing_filter = BinaryClosing(disk_size=5)
closed_image = closing_filter(binary_image)
```

**Use cases:**
- Filling small holes in tissue regions
- Connecting nearby objects
- Smoothing internal boundaries

### RemoveSmallObjects

Remove connected components smaller than a threshold.

```python
from histolab.filters.morphological_filters import RemoveSmallObjects

remove_small_filter = RemoveSmallObjects(
    area_threshold=500  # Minimum area in pixels
)
cleaned_image = remove_small_filter(binary_image)
```

**Use cases:**
- Removing dust and artifacts
- Filtering noise
- Cleaning tissue masks

### RemoveSmallHoles

Fill holes smaller than a threshold.

```python
from histolab.filters.morphological_filters import RemoveSmallHoles

fill_holes_filter = RemoveSmallHoles(
    area_threshold=1000  # Maximum hole size to fill
)
filled_image = fill_holes_filter(binary_image)
```

**Use cases:**
- Filling small gaps in tissue
- Creating continuous tissue regions
- Removing internal artifacts

## Filter Composition

### Chaining Filters

Combine multiple filters in sequence:

```python
from histolab.filters.image_filters import RgbToGrayscale, OtsuThreshold
from histolab.filters.morphological_filters import BinaryDilation, RemoveSmallObjects
from histolab.filters.compositions import Compose

# Create filter pipeline
tissue_detection_pipeline = Compose([
    RgbToGrayscale(),
    OtsuThreshold(),
    BinaryDilation(disk_size=5),
    RemoveSmallHoles(area_threshold=1000),
    RemoveSmallObjects(area_threshold=500)
])

# Apply pipeline
result = tissue_detection_pipeline(rgb_image)
```

### Lambda Filters

Create custom filters inline:

```python
from histolab.filters.image_filters import Lambda
import numpy as np

# Custom brightness adjustment
brightness_filter = Lambda(lambda img: np.clip(img * 1.2, 0, 255).astype(np.uint8))

# Custom color channel extraction
red_channel_filter = Lambda(lambda img: img[:, :, 0])
```

## Common Preprocessing Pipelines

### Standard Tissue Detection

```python
from histolab.filters.compositions import Compose
from histolab.filters.image_filters import RgbToGrayscale, OtsuThreshold
from histolab.filters.morphological_filters import (
    BinaryDilation, RemoveSmallHoles, RemoveSmallObjects
)

tissue_detection = Compose([
    RgbToGrayscale(),
    OtsuThreshold(),
    BinaryDilation(disk_size=5),
    RemoveSmallHoles(area_threshold=1000),
    RemoveSmallObjects(area_threshold=500)
])
```

### Pen Mark Removal

```python
from histolab.filters.image_filters import RgbToHsv, Lambda
import numpy as np

def remove_pen_marks(hsv_image):
    """Remove blue/green pen markings."""
    h, s, v = hsv_image[:, :, 0], hsv_image[:, :, 1], hsv_image[:, :, 2]
    # Mask for blue/green hues (common pen colors)
    pen_mask = ((h > 0.45) & (h < 0.7) & (s > 0.3))
    # Set pen regions to white
    hsv_image[pen_mask] = [0, 0, 1]
    return hsv_image

pen_removal = Compose([
    RgbToHsv(),
    Lambda(remove_pen_marks)
])
```

### Nuclei Enhancement

```python
from histolab.filters.image_filters import RgbToHed, HistogramEqualization
from histolab.filters.compositions import Compose

nuclei_enhancement = Compose([
    RgbToHed(),
    Lambda(lambda hed: hed[:, :, 0]),  # Extract hematoxylin channel
    HistogramEqualization()
])
```

### Contrast Normalization

```python
from histolab.filters.image_filters import StretchContrast, HistogramEqualization

contrast_normalization = Compose([
    RgbToGrayscale(),
    StretchContrast(),
    HistogramEqualization()
])
```

## Applying Filters to Tiles

Filters can be applied to individual tiles:

```python
from histolab.tile import Tile
from histolab.filters.image_filters import RgbToGrayscale

# Load or extract tile
tile = Tile(image=pil_image, coords=(x, y))

# Apply filter
gray_filter = RgbToGrayscale()
filtered_tile = tile.apply_filters(gray_filter)

# Chain multiple filters
from histolab.filters.compositions import Compose
from histolab.filters.image_filters import StretchContrast

filter_chain = Compose([
    RgbToGrayscale(),
    StretchContrast()
])
processed_tile = tile.apply_filters(filter_chain)
```

## Custom Mask Filters

Integrate custom filters with tissue masks:

```python
from histolab.masks import TissueMask
from histolab.filters.compositions import Compose
from histolab.filters.image_filters import RgbToGrayscale, OtsuThreshold
from histolab.filters.morphological_filters import BinaryDilation

# Custom aggressive tissue detection
aggressive_filters = Compose([
    RgbToGrayscale(),
    OtsuThreshold(),
    BinaryDilation(disk_size=10),  # Larger dilation
    RemoveSmallObjects(area_threshold=5000)  # Remove only large artifacts
])

# Create mask with custom filters
custom_mask = TissueMask(filters=aggressive_filters)
```

## Stain Normalization

Histolab 0.6.0+ includes built-in stain normalization via `histolab.stain_normalizer`. Both methods follow the standard fit-on-target, transform-source pattern:

```python
from histolab.stain_normalizer import MacenkoStainNormalizer, ReinhardStainNormalizer
from PIL import Image

target_image = Image.open("reference_stain.png")
source_image = Image.open("source_stain.png")

# Macenko (H&E stain matrix decomposition)
macenko = MacenkoStainNormalizer()
macenko.fit(target_image)
normalized = macenko.transform(source_image)

# Reinhard (color transfer in LAB space)
reinhard = ReinhardStainNormalizer()
reinhard.fit(target_image)
normalized = reinhard.transform(source_image)
```

See the [stain normalizer docs](https://histolab.readthedocs.io/en/latest/api/stain_normalizer.html) for examples and comparison images.

### Filter-based alternatives

For lightweight preprocessing without full stain normalization, combine HED decomposition with custom filters:

```python
from histolab.filters.image_filters import RgbToHed, Lambda
import numpy as np

def normalize_hed(hed_image, target_means=[0.65, 0.70], target_stds=[0.15, 0.13]):
    """Simple H&E channel normalization in HED space."""
    h_channel = hed_image[:, :, 0]
    e_channel = hed_image[:, :, 1]

    h_normalized = (h_channel - h_channel.mean()) / h_channel.std()
    h_normalized = h_normalized * target_stds[0] + target_means[0]

    e_normalized = (e_channel - e_channel.mean()) / e_channel.std()
    e_normalized = e_normalized * target_stds[1] + target_means[1]

    hed_image[:, :, 0] = h_normalized
    hed_image[:, :, 1] = e_normalized

    return hed_image

normalization_pipeline = Compose([
    RgbToHed(),
    Lambda(normalize_hed)
])
```

## Best Practices

1. **Preview filters**: Visualize filter outputs on thumbnails before applying to tiles
2. **Chain efficiently**: Order filters logically (e.g., color conversion before thresholding)
3. **Tune parameters**: Adjust thresholds and structuring element sizes for specific tissues
4. **Use composition**: Build reusable filter pipelines with `Compose`
5. **Consider performance**: Complex filter chains increase processing time
6. **Validate on diverse slides**: Test filters across different scanners, stains, and tissue types
7. **Document custom filters**: Clearly describe purpose and parameters of custom pipelines

## Quality Control Filters

### Blur Detection

```python
from histolab.filters.image_filters import Lambda
import cv2
import numpy as np

def laplacian_blur_score(gray_image):
    """Calculate Laplacian variance (blur metric)."""
    # cv2.CV_64F is an OpenCV constant, not Python eval()
    return cv2.Laplacian(np.array(gray_image), cv2.CV_64F).var()

blur_detector = Lambda(lambda img: laplacian_blur_score(
    RgbToGrayscale()(img)
))
```

### Tissue Coverage

```python
from histolab.filters.image_filters import RgbToGrayscale, OtsuThreshold
from histolab.filters.compositions import Compose

def tissue_coverage(image):
    """Calculate percentage of tissue in image."""
    tissue_mask = Compose([
        RgbToGrayscale(),
        OtsuThreshold()
    ])(image)
    return tissue_mask.sum() / tissue_mask.size * 100

coverage_filter = Lambda(tissue_coverage)
```

## Troubleshooting

### Issue: Tissue detection misses valid tissue
**Solutions:**
- Reduce `area_threshold` in `RemoveSmallObjects`
- Decrease erosion/opening disk size
- Try adaptive thresholding instead of Otsu

### Issue: Too many artifacts included
**Solutions:**
- Increase `area_threshold` in `RemoveSmallObjects`
- Add opening/closing operations
- Use custom color-based filtering for specific artifacts

### Issue: Tissue boundaries too rough
**Solutions:**
- Add `BinaryClosing` or `BinaryOpening` for smoothing
- Adjust disk_size for morphological operations

### Issue: Variable staining quality
**Solutions:**
- Apply `MacenkoStainNormalizer` or `ReinhardStainNormalizer` (histolab 0.6.0+)
- Apply histogram equalization
- Use adaptive thresholding
- Implement filter-based normalization pipeline

### `references/slide_management.md`

# Slide Management

## Overview

The `Slide` class is the primary interface for working with whole slide images (WSI) in histolab. It provides methods to load, inspect, and process large histopathology images stored in various formats.

## Initialization

```python
from histolab.slide import Slide

# Initialize a slide with a WSI file and output directory
slide = Slide("path/to/slide.svs", processed_path="path/to/processed/output")
```

**Parameters:**
- `path`: Path to the whole slide image file (supports multiple formats: SVS, TIFF, NDPI, etc.)
- `processed_path`: Directory where processed outputs (tiles, thumbnails, etc.) will be saved
- `use_largeimage` (optional): Use `large_image` for multi-format backends and mpp-based extraction

## Loading Sample Data

Histolab provides built-in sample datasets from TCGA for testing and demonstration. Install `pooch` to download them:

```bash
uv pip install pooch
```

```python
from histolab.data import prostate_tissue, ovarian_tissue, breast_tissue, heart_tissue, kidney_tissue

# Load prostate tissue sample
prostate_svs, prostate_path = prostate_tissue()
slide = Slide(prostate_path, processed_path="output/")
```

Available sample datasets:
- `prostate_tissue()`: Prostate tissue sample
- `ovarian_tissue()`: Ovarian tissue sample
- `breast_tissue()`: Breast tissue sample
- `heart_tissue()`: Heart tissue sample
- `kidney_tissue()`: Kidney tissue sample

## Key Properties

### Slide Dimensions
```python
# Get slide dimensions at level 0 (highest resolution)
width, height = slide.dimensions

# Get dimensions at specific pyramid level
level_dimensions = slide.level_dimensions
# Returns tuple of (width, height) for each level
```

### Magnification Information
```python
# Get base magnification (e.g., 40x, 20x)
base_mag = slide.base_mpp  # Microns per pixel at level 0

# Get all available levels
num_levels = slide.levels  # Number of pyramid levels
```

### Slide Properties
```python
# Access OpenSlide properties dictionary
properties = slide.properties

# Common properties include:
# - slide.properties['openslide.objective-power']: Objective power
# - slide.properties['openslide.mpp-x']: Microns per pixel in X
# - slide.properties['openslide.mpp-y']: Microns per pixel in Y
# - slide.properties['openslide.vendor']: Scanner vendor
```

## Thumbnail Generation

```python
from pathlib import Path

# Get thumbnail at default size
thumbnail = slide.thumbnail

# Save thumbnail to processed_path
Path(slide.processed_path).mkdir(parents=True, exist_ok=True)
slide.thumbnail.save(Path(slide.processed_path) / f"{slide.name}_thumbnail.png")

# Get scaled thumbnail
scaled_thumbnail = slide.scaled_image(scale_factor=32)
```

## Slide Visualization

```python
# Display slide thumbnail with matplotlib
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 10))
plt.imshow(slide.thumbnail)
plt.title(f"Slide: {slide.name}")
plt.axis('off')
plt.show()
```

## Extracting Regions

```python
from histolab.types import CoordinatePair

# Extract a tile at specific coordinates and level
tile = slide.extract_tile(
    coords=CoordinatePair(x_ul=x, y_ul=y, x_br=x + width, y_br=y + height),
    tile_size=(width, height),
    level=0,
)
region = tile.image
```

## Working with Pyramid Levels

WSI files use a pyramidal structure with multiple resolution levels:
- Level 0: Highest resolution (native scan resolution)
- Level 1+: Progressively lower resolutions for faster access

```python
# Check available levels
for level in range(slide.levels):
    dims = slide.level_dimensions[level]
    downsample = slide.level_downsamples[level]
    print(f"Level {level}: {dims}, downsample: {downsample}x")
```

## Slide Name and Path

```python
# Get slide filename without extension
slide_name = slide.name

# Get output directory for processed artifacts
output_dir = slide.processed_path
```

## Best Practices

1. **Always specify processed_path**: Organize outputs in dedicated directories
2. **Check dimensions before processing**: Large slides can exceed memory limits
3. **Use appropriate pyramid levels**: Extract tiles at levels matching your analysis resolution
4. **Preview with thumbnails**: Use thumbnails for quick visualization before heavy processing
5. **Monitor memory usage**: Level 0 operations on large slides require significant RAM

## Common Workflows

### Slide Inspection Workflow
```python
from histolab.slide import Slide

# Load slide
slide = Slide("slide.svs", processed_path="output/")

# Inspect properties
print(f"Dimensions: {slide.dimensions}")
print(f"Levels: {slide.levels}")
print(f"Magnification: {slide.properties.get('openslide.objective-power', 'N/A')}")

# Save thumbnail for review
from pathlib import Path
Path(slide.processed_path).mkdir(parents=True, exist_ok=True)
slide.thumbnail.save(Path(slide.processed_path) / f"{slide.name}_thumbnail.png")
```

### Multi-Slide Processing
```python
import os
from pathlib import Path

slide_dir = Path("slides/")
output_dir = Path("processed/")

for slide_path in slide_dir.glob("*.svs"):
    slide = Slide(slide_path, processed_path=output_dir / slide_path.stem)
    # Process each slide
    print(f"Processing: {slide.name}")
```

### `references/tile_extraction.md`

# Tile Extraction

## Overview

Tile extraction is the process of cropping smaller, manageable regions from large whole slide images. Histolab provides three main extraction strategies, each suited for different analysis needs. All tilers share common parameters and provide methods for previewing and extracting tiles.

## Common Parameters

All tiler classes accept these parameters:

```python
tile_size: tuple = (512, 512)           # Tile dimensions in pixels (width, height)
level: int = 0                          # Pyramid level for extraction (0=highest resolution)
check_tissue: bool = True               # Filter tiles by tissue content
tissue_percent: float = 80.0            # Minimum tissue coverage (0-100)
pixel_overlap: int = 0                  # Overlap between adjacent tiles (GridTiler only)
prefix: str = ""                        # Prefix for saved tile filenames
suffix: str = ".png"                    # File extension for saved tiles
extraction_mask: BinaryMask = BiggestTissueBoxMask()  # Mask defining extraction region
```

## RandomTiler

**Purpose:** Extract a fixed number of randomly positioned tiles from tissue regions.

```python
from histolab.tiler import RandomTiler

random_tiler = RandomTiler(
    tile_size=(512, 512),
    n_tiles=100,                # Number of random tiles to extract
    level=0,
    seed=42,                    # Random seed for reproducibility
    check_tissue=True,
    tissue_percent=80.0
)

# Extract tiles
random_tiler.extract(slide, extraction_mask=TissueMask())
```

**Key Parameters:**
- `n_tiles`: Number of random tiles to extract
- `seed`: Random seed for reproducible tile selection
- `max_iter`: Maximum attempts to find valid tiles (default 1000)

**Use cases:**
- Exploratory analysis of slide content
- Sampling diverse regions for training data
- Quick assessment of tissue characteristics
- Balanced dataset creation from multiple slides

**Advantages:**
- Computationally efficient
- Good for sampling diverse tissue morphologies
- Reproducible with seed parameter
- Fast execution

**Limitations:**
- May miss rare tissue patterns
- No guarantee of coverage
- Random distribution may not capture structured features

## GridTiler

**Purpose:** Extract tiles systematically across tissue regions following a grid pattern.

```python
from histolab.tiler import GridTiler

grid_tiler = GridTiler(
    tile_size=(512, 512),
    level=0,
    check_tissue=True,
    tissue_percent=80.0,
    pixel_overlap=0             # Overlap in pixels between adjacent tiles
)

# Extract tiles
grid_tiler.extract(slide)
```

**Key Parameters:**
- `pixel_overlap`: Number of overlapping pixels between adjacent tiles
  - `pixel_overlap=0`: Non-overlapping tiles
  - `pixel_overlap=128`: 128-pixel overlap on each side
  - Can be used for sliding window approaches

**Use cases:**
- Comprehensive slide coverage
- Spatial analysis requiring positional information
- Image reconstruction from tiles
- Semantic segmentation tasks
- Region-based analysis

**Advantages:**
- Complete tissue coverage
- Preserves spatial relationships
- Predictable tile positions
- Suitable for whole-slide analysis

**Limitations:**
- Computationally intensive for large slides
- May generate many background-heavy tiles (mitigated by `check_tissue`)
- Larger output datasets

**Grid Pattern:**
```
[Tile 1][Tile 2][Tile 3]
[Tile 4][Tile 5][Tile 6]
[Tile 7][Tile 8][Tile 9]
```

With `pixel_overlap=64`:
```
[Tile 1-overlap-Tile 2-overlap-Tile 3]
[    overlap       overlap       overlap]
[Tile 4-overlap-Tile 5-overlap-Tile 6]
```

## ScoreTiler

**Purpose:** Extract top-ranked tiles based on custom scoring functions.

```python
from histolab.tiler import ScoreTiler
from histolab.scorer import NucleiScorer

score_tiler = ScoreTiler(
    tile_size=(512, 512),
    n_tiles=50,                 # Number of top-scoring tiles to extract
    level=0,
    scorer=NucleiScorer(),      # Scoring function
    check_tissue=True
)

# Extract top-scoring tiles
score_tiler.extract(slide)
```

**Key Parameters:**
- `n_tiles`: Number of top-scoring tiles to extract
- `scorer`: Scoring function (e.g., `NucleiScorer`, `CellularityScorer`, custom scorer)

**Use cases:**
- Extracting most informative regions
- Prioritizing tiles with specific features (nuclei, cells, etc.)
- Quality-based tile selection
- Focusing on diagnostically relevant areas
- Training data curation

**Advantages:**
- Focuses on most informative tiles
- Reduces dataset size while maintaining quality
- Customizable with different scorers
- Efficient for targeted analysis

**Limitations:**
- Slower than RandomTiler (must score all candidate tiles)
- Requires appropriate scorer for task
- May miss low-scoring but relevant regions

## Available Scorers

### NucleiScorer

Scores tiles based on nuclei detection and density.

```python
from histolab.scorer import NucleiScorer

nuclei_scorer = NucleiScorer()
```

**How it works:**
1. Converts tile to grayscale
2. Applies thresholding to detect nuclei
3. Counts nuclei-like structures
4. Assigns score based on nuclei density

**Best for:**
- Cell-rich tissue regions
- Tumor detection
- Mitosis analysis
- Areas with high cellular content

### CellularityScorer

Scores tiles based on overall cellular content.

```python
from histolab.scorer import CellularityScorer

cellularity_scorer = CellularityScorer()
```

**Best for:**
- Identifying cellular vs. stromal regions
- Tumor cellularity assessment
- Separating dense from sparse tissue areas

### Custom Scorers

Create custom scoring functions for specific needs:

```python
from histolab.scorer import Scorer
import numpy as np

class ColorVarianceScorer(Scorer):
    def __call__(self, tile):
        """Score tiles based on color variance."""
        tile_array = np.array(tile.image)
        # Calculate color variance
        variance = np.var(tile_array, axis=(0, 1)).sum()
        return variance

# Use custom scorer
variance_scorer = ColorVarianceScorer()
score_tiler = ScoreTiler(
    tile_size=(512, 512),
    n_tiles=30,
    scorer=variance_scorer
)
```

## Tile Preview with locate_tiles()

Preview tile locations before extraction to validate tiler configuration:

```python
# Preview random tile locations
random_tiler.locate_tiles(
    slide=slide,
    extraction_mask=TissueMask(),
    n_tiles=20  # Number of tiles to preview (for RandomTiler)
)
```

This displays the slide thumbnail with colored rectangles indicating tile positions.

## Extraction Workflow

### Basic Extraction

```python
from histolab.slide import Slide
from histolab.tiler import RandomTiler

# Load slide
slide = Slide("slide.svs", processed_path="output/tiles/")

# Configure tiler
tiler = RandomTiler(
    tile_size=(512, 512),
    n_tiles=100,
    level=0,
    seed=42
)

# Extract tiles (saved to processed_path)
tiler.extract(slide)
```

### Extraction with Logging

```python
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)

# Extract tiles with progress information
tiler.extract(slide)
# Output: INFO: Tile 1/100 saved...
# Output: INFO: Tile 2/100 saved...
```

### Extraction with Report

```python
# Generate CSV report with tile information
score_tiler = ScoreTiler(
    tile_size=(512, 512),
    n_tiles=50,
    scorer=NucleiScorer()
)

# Extract and save report
score_tiler.extract(slide, report_path="tiles_report.csv")

# Report contains: tile name, coordinates, score, tissue percentage
```

Report format:
```csv
tile_name,x_coord,y_coord,level,score,tissue_percent
tile_001.png,10240,5120,0,0.89,95.2
tile_002.png,15360,7680,0,0.85,91.7
...
```

## Advanced Extraction Patterns

### Multi-Level Extraction

Extract tiles at different magnification levels:

```python
# High resolution tiles (level 0)
high_res_tiler = RandomTiler(tile_size=(512, 512), n_tiles=50, level=0)
high_res_tiler.extract(slide)

# Medium resolution tiles (level 1)
med_res_tiler = RandomTiler(tile_size=(512, 512), n_tiles=50, level=1)
med_res_tiler.extract(slide)

# Low resolution tiles (level 2)
low_res_tiler = RandomTiler(tile_size=(512, 512), n_tiles=50, level=2)
low_res_tiler.extract(slide)
```

### Hierarchical Extraction

Extract at multiple scales from same locations:

```python
# Extract random locations at level 0
random_tiler_l0 = RandomTiler(
    tile_size=(512, 512),
    n_tiles=30,
    level=0,
    seed=42,
    prefix="level0_"
)
random_tiler_l0.extract(slide)

# Extract same locations at level 1 (use same seed)
random_tiler_l1 = RandomTiler(
    tile_size=(512, 512),
    n_tiles=30,
    level=1,
    seed=42,
    prefix="level1_"
)
random_tiler_l1.extract(slide)
```

### Custom Tile Filtering

Apply additional filtering after extraction:

```python
from PIL import Image
import numpy as np
from pathlib import Path

def filter_blurry_tiles(tile_dir, threshold=100):
    """Remove blurry tiles using Laplacian variance."""
    for tile_path in Path(tile_dir).glob("*.png"):
        img = Image.open(tile_path)
        gray = np.array(img.convert('L'))
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        if laplacian_var < threshold:
            tile_path.unlink()  # Remove blurry tile
            print(f"Removed blurry tile: {tile_path.name}")

# Use after extraction
tiler.extract(slide)
filter_blurry_tiles("output/tiles/")
```

## Best Practices

1. **Preview before extraction**: Always use `locate_tiles()` to verify tile placement
2. **Use appropriate level**: Match extraction level to analysis resolution requirements
3. **Set tissue_percent threshold**: Adjust based on staining and tissue type (70-90% typical)
4. **Choose right tiler**:
   - RandomTiler for sampling and exploration
   - GridTiler for comprehensive coverage
   - ScoreTiler for targeted, quality-driven extraction
5. **Enable logging**: Monitor extraction progress for large datasets
6. **Use seeds for reproducibility**: Set random seeds in RandomTiler
7. **Consider storage**: GridTiler can generate thousands of tiles per slide
8. **Validate tile quality**: Check extracted tiles for artifacts, blur, or focus issues

## Performance Optimization

1. **Extract at appropriate level**: Lower levels (1, 2) extract faster
2. **Adjust tissue_percent**: Higher thresholds reduce invalid tile attempts
3. **Use BiggestTissueBoxMask**: Faster than TissueMask for single tissue sections
4. **Limit n_tiles**: For RandomTiler and ScoreTiler
5. **Use pixel_overlap=0**: For non-overlapping GridTiler extraction

## Troubleshooting

### Issue: No tiles extracted
**Solutions:**
- Lower `tissue_percent` threshold
- Verify slide contains tissue (check thumbnail)
- Ensure extraction_mask captures tissue regions
- Check that tile_size is appropriate for slide resolution

### Issue: Many background tiles extracted
**Solutions:**
- Enable `check_tissue=True`
- Increase `tissue_percent` threshold
- Use appropriate mask (TissueMask vs. BiggestTissueBoxMask)

### Issue: Extraction is very slow
**Solutions:**
- Extract at lower pyramid level (level=1 or 2)
- Reduce `n_tiles` for RandomTiler/ScoreTiler
- Use RandomTiler instead of GridTiler for sampling
- Use BiggestTissueBoxMask instead of TissueMask

### Issue: Tiles have too much overlap (GridTiler)
**Solutions:**
- Set `pixel_overlap=0` for non-overlapping tiles
- Reduce `pixel_overlap` value

### `references/tissue_masks.md`

# Tissue Masks

## Overview

Tissue masks are binary representations that identify tissue regions within whole slide images. They are essential for filtering out background, artifacts, and non-tissue areas during tile extraction. Histolab provides several mask classes to accommodate different tissue segmentation needs.

## Mask Classes

### BinaryMask

**Purpose:** Generic base class for creating custom binary masks.

```python
from histolab.masks import BinaryMask

class CustomMask(BinaryMask):
    def _mask(self, obj):
        # Implement custom masking logic
        # Return binary numpy array
        pass
```

**Use cases:**
- Custom tissue segmentation algorithms
- Region-specific analysis (e.g., excluding annotations)
- Integration with external segmentation models

### TissueMask

**Purpose:** Segments all tissue regions in the slide using automated filters.

```python
from histolab.masks import TissueMask

# Create tissue mask
tissue_mask = TissueMask()

# Apply to slide
mask_array = tissue_mask(slide)
```

**How it works:**
1. Converts image to grayscale
2. Applies Otsu thresholding to separate tissue from background
3. Performs binary dilation to connect nearby tissue regions
4. Removes small holes within tissue regions
5. Filters out small objects (artifacts)

**Returns:** Binary NumPy array where:
- `True` (or 1): Tissue pixels
- `False` (or 0): Background pixels

**Best for:**
- Slides with multiple separate tissue sections
- Comprehensive tissue analysis
- When all tissue regions are important

### BiggestTissueBoxMask (Default)

**Purpose:** Identifies and returns the bounding box of the largest connected tissue region.

```python
from histolab.masks import BiggestTissueBoxMask

# Create mask for largest tissue region
biggest_mask = BiggestTissueBoxMask()

# Apply to slide
mask_array = biggest_mask(slide)
```

**How it works:**
1. Applies same filtering pipeline as TissueMask
2. Identifies all connected tissue components
3. Selects the largest connected component
4. Returns bounding box encompassing that region

**Best for:**
- Slides with a single primary tissue section
- Excluding small artifacts or tissue fragments
- Focusing on main tissue area (default for most tilers)

## Customizing Masks with Filters

Masks accept custom filter chains for specialized tissue detection:

```python
from histolab.masks import TissueMask
from histolab.filters.image_filters import RgbToGrayscale, OtsuThreshold
from histolab.filters.morphological_filters import BinaryDilation, RemoveSmallHoles

# Define custom filter composition
custom_mask = TissueMask(
    filters=[
        RgbToGrayscale(),
        OtsuThreshold(),
        BinaryDilation(disk_size=5),
        RemoveSmallHoles(area_threshold=500)
    ]
)
```

## Visualizing Masks

### Using locate_mask()

```python
from histolab.slide import Slide
from histolab.masks import TissueMask

slide = Slide("slide.svs", processed_path="output/")
mask = TissueMask()

# Visualize mask boundaries on thumbnail
slide.locate_mask(mask)
```

This displays the slide thumbnail with mask boundaries overlaid in a contrasting color.

### Manual Visualization

```python
import matplotlib.pyplot as plt
from histolab.masks import TissueMask

slide = Slide("slide.svs", processed_path="output/")
tissue_mask = TissueMask()

# Generate mask
mask_array = tissue_mask(slide)

# Plot side by side
fig, axes = plt.subplots(1, 2, figsize=(15, 7))

axes[0].imshow(slide.thumbnail)
axes[0].set_title("Original Slide")
axes[0].axis('off')

axes[1].imshow(mask_array, cmap='gray')
axes[1].set_title("Tissue Mask")
axes[1].axis('off')

plt.show()
```

## Creating Custom Rectangular Masks

Define specific regions of interest:

```python
from histolab.masks import BinaryMask
import numpy as np

class RectangularMask(BinaryMask):
    def __init__(self, x_start, y_start, width, height):
        self.x_start = x_start
        self.y_start = y_start
        self.width = width
        self.height = height

    def _mask(self, obj):
        # Create mask with specified rectangular region
        thumb = obj.thumbnail
        mask = np.zeros(thumb.shape[:2], dtype=bool)
        mask[self.y_start:self.y_start+self.height,
             self.x_start:self.x_start+self.width] = True
        return mask

# Use custom mask
roi_mask = RectangularMask(x_start=1000, y_start=500, width=2000, height=1500)
```

## Excluding Annotations

Pathology slides often contain pen markings or digital annotations. Exclude them using custom masks:

```python
from histolab.masks import TissueMask
from histolab.filters.image_filters import RgbToGrayscale, OtsuThreshold
from histolab.filters.morphological_filters import BinaryDilation

class AnnotationExclusionMask(BinaryMask):
    def _mask(self, obj):
        thumb = obj.thumbnail

        # Convert to HSV to detect pen marks (often blue/green)
        hsv = cv2.cvtColor(np.array(thumb), cv2.COLOR_RGB2HSV)

        # Define color ranges for pen marks
        lower_blue = np.array([100, 50, 50])
        upper_blue = np.array([130, 255, 255])

        # Create mask excluding pen marks
        pen_mask = cv2.inRange(hsv, lower_blue, upper_blue)

        # Apply standard tissue detection
        tissue_mask = TissueMask()(obj)

        # Combine: keep tissue, exclude pen marks
        final_mask = tissue_mask & ~pen_mask.astype(bool)

        return final_mask
```

## Integration with Tile Extraction

Masks integrate seamlessly with tilers through the `extraction_mask` parameter:

```python
from histolab.tiler import RandomTiler
from histolab.masks import TissueMask, BiggestTissueBoxMask

# Use TissueMask to extract from all tissue
random_tiler = RandomTiler(
    tile_size=(512, 512),
    n_tiles=100,
    level=0,
    extraction_mask=TissueMask()  # Extract from all tissue regions
)

# Or use default BiggestTissueBoxMask
random_tiler = RandomTiler(
    tile_size=(512, 512),
    n_tiles=100,
    level=0,
    extraction_mask=BiggestTissueBoxMask()  # Default behavior
)
```

## Best Practices

1. **Preview masks before extraction**: Use `locate_mask()` or manual visualization to verify mask quality
2. **Choose appropriate mask type**: Use `TissueMask` for multiple tissue sections, `BiggestTissueBoxMask` for single main sections
3. **Customize for specific stains**: Different stains (H&E, IHC) may require adjusted threshold parameters
4. **Handle artifacts**: Use custom filters or masks to exclude pen marks, bubbles, or folds
5. **Test on diverse slides**: Validate mask performance across slides with varying quality and artifacts
6. **Consider computational cost**: `TissueMask` is more comprehensive but computationally intensive than `BiggestTissueBoxMask`

## Common Issues and Solutions

### Issue: Mask includes too much background
**Solution:** Adjust Otsu threshold or increase small object removal threshold

### Issue: Mask excludes valid tissue
**Solution:** Reduce small object removal threshold or modify dilation parameters

### Issue: Multiple tissue sections, but only largest is captured
**Solution:** Switch from `BiggestTissueBoxMask` to `TissueMask`

### Issue: Pen annotations included in mask
**Solution:** Implement custom annotation exclusion mask (see example above)

### `references/typical_workflows.md`

# Typical Workflows

Five end-to-end workflows: exploratory tile extraction, comprehensive grid extraction,
quality-driven tile selection, multi-slide processing pipelines, and custom tissue
detection and filtering.

## Typical Workflows

### Workflow 1: Exploratory Tile Extraction

Quick sampling of diverse tissue regions for initial analysis.

```python
from histolab.slide import Slide
from histolab.tiler import RandomTiler
from pathlib import Path
import logging

# Enable logging for progress tracking
logging.basicConfig(level=logging.INFO)

# Load slide
slide = Slide("slide.svs", processed_path="output/random_tiles/")

# Inspect slide
print(f"Dimensions: {slide.dimensions}")
print(f"Levels: {slide.levels}")
Path(slide.processed_path).mkdir(parents=True, exist_ok=True)
slide.thumbnail.save(Path(slide.processed_path) / f"{slide.name}_thumbnail.png")

# Configure random tiler
random_tiler = RandomTiler(
    tile_size=(512, 512),
    n_tiles=100,
    level=0,
    seed=42,
    check_tissue=True,
    tissue_percent=80.0
)

# Preview locations
random_tiler.locate_tiles(slide, n_tiles=20)

# Extract tiles
random_tiler.extract(slide)
```

### Workflow 2: Comprehensive Grid Extraction

Complete tissue coverage for whole-slide analysis.

```python
from histolab.slide import Slide
from histolab.tiler import GridTiler
from histolab.masks import TissueMask

# Load slide
slide = Slide("slide.svs", processed_path="output/grid_tiles/")

# Use TissueMask for all tissue sections
tissue_mask = TissueMask()
slide.locate_mask(tissue_mask)

# Configure grid tiler
grid_tiler = GridTiler(
    tile_size=(512, 512),
    level=1,  # Use level 1 for faster extraction
    pixel_overlap=0,
    check_tissue=True,
    tissue_percent=70.0
)

# Preview grid
grid_tiler.locate_tiles(slide)

# Extract all tiles
grid_tiler.extract(slide, extraction_mask=tissue_mask)
```

### Workflow 3: Quality-Driven Tile Selection

Extract most informative tiles based on nuclei density.

```python
from histolab.slide import Slide
from histolab.tiler import ScoreTiler
from histolab.scorer import NucleiScorer
import pandas as pd
import matplotlib.pyplot as plt

# Load slide
slide = Slide("slide.svs", processed_path="output/scored_tiles/")

# Configure score tiler
score_tiler = ScoreTiler(
    tile_size=(512, 512),
    n_tiles=50,
    level=0,
    scorer=NucleiScorer(),
    check_tissue=True
)

# Preview top tiles
score_tiler.locate_tiles(slide, n_tiles=15)

# Extract with report
score_tiler.extract(slide, report_path="tiles_report.csv")

# Analyze scores
report_df = pd.read_csv("tiles_report.csv")
plt.hist(report_df['score'], bins=20, edgecolor='black')
plt.xlabel('Tile Score')
plt.ylabel('Frequency')
plt.title('Distribution of Tile Scores')
plt.show()
```

### Workflow 4: Multi-Slide Processing Pipeline

Process entire slide collection with consistent parameters.

```python
from pathlib import Path
from histolab.slide import Slide
from histolab.tiler import RandomTiler
import logging

logging.basicConfig(level=logging.INFO)

# Configure tiler once
tiler = RandomTiler(
    tile_size=(512, 512),
    n_tiles=50,
    level=0,
    seed=42,
    check_tissue=True
)

# Process all slides
slide_dir = Path("slides/")
output_base = Path("output/")

for slide_path in slide_dir.glob("*.svs"):
    print(f"\nProcessing: {slide_path.name}")

    # Create slide-specific output directory
    output_dir = output_base / slide_path.stem
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load and process slide
    slide = Slide(slide_path, processed_path=output_dir)

    # Save thumbnail for review
    Path(slide.processed_path).mkdir(parents=True, exist_ok=True)
    slide.thumbnail.save(Path(slide.processed_path) / f"{slide.name}_thumbnail.png")

    # Extract tiles
    tiler.extract(slide)

    print(f"Completed: {slide_path.name}")
```

### Workflow 5: Custom Tissue Detection and Filtering

Handle slides with artifacts, annotations, or unusual staining.

```python
from histolab.slide import Slide
from histolab.masks import TissueMask
from histolab.tiler import RandomTiler
from histolab.filters.compositions import Compose
from histolab.filters.image_filters import RgbToGrayscale, OtsuThreshold
from histolab.filters.morphological_filters import (
    BinaryDilation, RemoveSmallObjects, RemoveSmallHoles
)

# Define custom filter pipeline for aggressive artifact removal
aggressive_filters = Compose([
    RgbToGrayscale(),
    OtsuThreshold(),
    BinaryDilation(disk_size=10),
    RemoveSmallHoles(area_threshold=5000),
    RemoveSmallObjects(area_threshold=3000)  # Remove larger artifacts
])

# Create custom mask
custom_mask = TissueMask(filters=aggressive_filters)

# Load slide and visualize mask
slide = Slide("slide.svs", processed_path="output/")
slide.locate_mask(custom_mask)

# Extract with custom mask
tiler = RandomTiler(tile_size=(512, 512), n_tiles=100)
tiler.extract(slide, extraction_mask=custom_mask)
```

### `references/visualization.md`

# Visualization

## Overview

Histolab provides several built-in visualization methods to help inspect slides, preview tile locations, visualize masks, and assess extraction quality. Proper visualization is essential for validating preprocessing pipelines, debugging extraction issues, and presenting results.

## Slide Visualization

### Thumbnail Display

```python
from histolab.slide import Slide
import matplotlib.pyplot as plt

slide = Slide("slide.svs", processed_path="output/")

# Display thumbnail
plt.figure(figsize=(10, 10))
plt.imshow(slide.thumbnail)
plt.title(f"Slide: {slide.name}")
plt.axis('off')
plt.show()
```

### Save Thumbnail to Disk

```python
from pathlib import Path

Path(slide.processed_path).mkdir(parents=True, exist_ok=True)
slide.thumbnail.save(Path(slide.processed_path) / f"{slide.name}_thumbnail.png")
```

### Scaled Images

```python
# Get scaled version of slide at specific downsample factor
scaled_img = slide.scaled_image(scale_factor=32)

plt.imshow(scaled_img)
plt.title(f"Slide at 32x downsample")
plt.show()
```

## Mask Visualization

### Using locate_mask()

```python
from histolab.masks import TissueMask, BiggestTissueBoxMask

# Visualize TissueMask
tissue_mask = TissueMask()
slide.locate_mask(tissue_mask)

# Visualize BiggestTissueBoxMask
biggest_mask = BiggestTissueBoxMask()
slide.locate_mask(biggest_mask)
```

This displays the slide thumbnail with mask boundaries overlaid in red.

### Manual Mask Visualization

```python
import matplotlib.pyplot as plt
from histolab.masks import TissueMask

slide = Slide("slide.svs", processed_path="output/")
mask = TissueMask()

# Generate mask
mask_array = mask(slide)

# Create side-by-side comparison
fig, axes = plt.subplots(1, 3, figsize=(20, 7))

# Original thumbnail
axes[0].imshow(slide.thumbnail)
axes[0].set_title("Original Slide")
axes[0].axis('off')

# Binary mask
axes[1].imshow(mask_array, cmap='gray')
axes[1].set_title("Tissue Mask")
axes[1].axis('off')

# Overlay mask on thumbnail
from matplotlib.colors import ListedColormap
overlay = slide.thumbnail.copy()
axes[2].imshow(overlay)
axes[2].imshow(mask_array, cmap=ListedColormap(['none', 'red']), alpha=0.3)
axes[2].set_title("Mask Overlay")
axes[2].axis('off')

plt.tight_layout()
plt.show()
```

### Comparing Multiple Masks

```python
from histolab.masks import TissueMask, BiggestTissueBoxMask

masks = {
    'TissueMask': TissueMask(),
    'BiggestTissueBoxMask': BiggestTissueBoxMask()
}

fig, axes = plt.subplots(1, len(masks) + 1, figsize=(20, 6))

# Original
axes[0].imshow(slide.thumbnail)
axes[0].set_title("Original")
axes[0].axis('off')

# Each mask
for idx, (name, mask) in enumerate(masks.items(), 1):
    mask_array = mask(slide)
    axes[idx].imshow(mask_array, cmap='gray')
    axes[idx].set_title(name)
    axes[idx].axis('off')

plt.tight_layout()
plt.show()
```

## Tile Location Preview

### Using locate_tiles()

Preview tile locations before extraction:

```python
from histolab.tiler import RandomTiler, GridTiler, ScoreTiler
from histolab.scorer import NucleiScorer

# RandomTiler preview
random_tiler = RandomTiler(
    tile_size=(512, 512),
    n_tiles=50,
    level=0,
    seed=42
)
random_tiler.locate_tiles(slide, n_tiles=20)

# GridTiler preview
grid_tiler = GridTiler(
    tile_size=(512, 512),
    level=0
)
grid_tiler.locate_tiles(slide)

# ScoreTiler preview
score_tiler = ScoreTiler(
    tile_size=(512, 512),
    n_tiles=30,
    scorer=NucleiScorer()
)
score_tiler.locate_tiles(slide, n_tiles=15)
```

This displays colored rectangles on the slide thumbnail indicating where tiles will be extracted.

### Custom Tile Location Visualization

```python
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from histolab.tiler import RandomTiler

slide = Slide("slide.svs", processed_path="output/")
tiler = RandomTiler(tile_size=(512, 512), n_tiles=30, seed=42)

# Get thumbnail and scale factor
thumbnail = slide.thumbnail
scale_factor = slide.dimensions[0] / thumbnail.size[0]

# Generate tile coordinates (without extracting)
fig, ax = plt.subplots(figsize=(12, 12))
ax.imshow(thumbnail)
ax.set_title("Tile Locations Preview")
ax.axis('off')

# Manually add rectangles for each tile location
# Note: This is conceptual - actual implementation would retrieve coordinates from tiler
tile_coords = []  # Would be populated by tiler logic
for coord in tile_coords:
    x, y = coord[0] / scale_factor, coord[1] / scale_factor
    w, h = 512 / scale_factor, 512 / scale_factor
    rect = patches.Rectangle((x, y), w, h,
                             linewidth=2, edgecolor='red',
                             facecolor='none')
    ax.add_patch(rect)

plt.show()
```

## Tile Visualization

### Display Extracted Tiles

```python
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt

tile_dir = Path("output/tiles/")
tile_paths = list(tile_dir.glob("*.png"))[:16]  # First 16 tiles

fig, axes = plt.subplots(4, 4, figsize=(12, 12))
axes = axes.ravel()

for idx, tile_path in enumerate(tile_paths):
    tile_img = Image.open(tile_path)
    axes[idx].imshow(tile_img)
    axes[idx].set_title(tile_path.stem, fontsize=8)
    axes[idx].axis('off')

plt.tight_layout()
plt.show()
```

### Tile Grid Mosaic

```python
def create_tile_mosaic(tile_dir, grid_size=(4, 4)):
    """Create mosaic of tiles."""
    tile_paths = list(Path(tile_dir).glob("*.png"))[:grid_size[0] * grid_size[1]]

    fig, axes = plt.subplots(grid_size[0], grid_size[1], figsize=(16, 16))

    for idx, tile_path in enumerate(tile_paths):
        row = idx // grid_size[1]
        col = idx % grid_size[1]
        tile_img = Image.open(tile_path)
        axes[row, col].imshow(tile_img)
        axes[row, col].axis('off')

    plt.tight_layout()
    plt.savefig("tile_mosaic.png", dpi=150, bbox_inches='tight')
    plt.show()

create_tile_mosaic("output/tiles/", grid_size=(5, 5))
```

### Tile with Tissue Mask Overlay

```python
from histolab.tile import Tile
import matplotlib.pyplot as plt

# Assume we have a tile object
tile = Tile(image=pil_image, coords=(x, y))

# Calculate tissue mask
tile.calculate_tissue_mask()

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Original tile
axes[0].imshow(tile.image)
axes[0].set_title("Original Tile")
axes[0].axis('off')

# Tissue mask
axes[1].imshow(tile.tissue_mask, cmap='gray')
axes[1].set_title(f"Tissue Mask ({tile.tissue_ratio:.1%} tissue)")
axes[1].axis('off')

# Overlay
axes[2].imshow(tile.image)
axes[2].imshow(tile.tissue_mask, cmap='Reds', alpha=0.3)
axes[2].set_title("Overlay")
axes[2].axis('off')

plt.tight_layout()
plt.show()
```

## Quality Assessment Visualization

### Tile Score Distribution

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load tile report from ScoreTiler
report_df = pd.read_csv("tiles_report.csv")

# Score distribution histogram
plt.figure(figsize=(10, 6))
plt.hist(report_df['score'], bins=30, edgecolor='black', alpha=0.7)
plt.xlabel('Tile Score')
plt.ylabel('Frequency')
plt.title('Distribution of Tile Scores')
plt.grid(axis='y', alpha=0.3)
plt.show()

# Score vs tissue percentage scatter
plt.figure(figsize=(10, 6))
plt.scatter(report_df['tissue_percent'], report_df['score'], alpha=0.5)
plt.xlabel('Tissue Percentage')
plt.ylabel('Tile Score')
plt.title('Tile Score vs Tissue Coverage')
plt.grid(alpha=0.3)
plt.show()
```

### Top vs Bottom Scoring Tiles

```python
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt

# Load tile report
report_df = pd.read_csv("tiles_report.csv")
report_df = report_df.sort_values('score', ascending=False)

# Top 8 tiles
top_tiles = report_df.head(8)
# Bottom 8 tiles
bottom_tiles = report_df.tail(8)

fig, axes = plt.subplots(2, 8, figsize=(20, 6))

# Display top tiles
for idx, (_, row) in enumerate(top_tiles.iterrows()):
    tile_img = Image.open(f"output/tiles/{row['tile_name']}")
    axes[0, idx].imshow(tile_img)
    axes[0, idx].set_title(f"Score: {row['score']:.3f}", fontsize=8)
    axes[0, idx].axis('off')

# Display bottom tiles
for idx, (_, row) in enumerate(bottom_tiles.iterrows()):
    tile_img = Image.open(f"output/tiles/{row['tile_name']}")
    axes[1, idx].imshow(tile_img)
    axes[1, idx].set_title(f"Score: {row['score']:.3f}", fontsize=8)
    axes[1, idx].axis('off')

axes[0, 0].set_ylabel('Top Scoring', fontsize=12)
axes[1, 0].set_ylabel('Bottom Scoring', fontsize=12)

plt.tight_layout()
plt.savefig("score_comparison.png", dpi=150, bbox_inches='tight')
plt.show()
```

## Multi-Slide Visualization

### Slide Collection Thumbnails

```python
from pathlib import Path
from histolab.slide import Slide
import matplotlib.pyplot as plt

slide_dir = Path("slides/")
slide_paths = list(slide_dir.glob("*.svs"))[:9]

fig, axes = plt.subplots(3, 3, figsize=(15, 15))
axes = axes.ravel()

for idx, slide_path in enumerate(slide_paths):
    slide = Slide(slide_path, processed_path="output/")
    axes[idx].imshow(slide.thumbnail)
    axes[idx].set_title(slide.name, fontsize=10)
    axes[idx].axis('off')

plt.tight_layout()
plt.savefig("slide_collection.png", dpi=150, bbox_inches='tight')
plt.show()
```

### Tissue Coverage Comparison

```python
from pathlib import Path
from histolab.slide import Slide
from histolab.masks import TissueMask
import matplotlib.pyplot as plt
import numpy as np

slide_paths = list(Path("slides/").glob("*.svs"))
tissue_percentages = []
slide_names = []

for slide_path in slide_paths:
    slide = Slide(slide_path, processed_path="output/")
    mask = TissueMask()(slide)
    tissue_pct = mask.sum() / mask.size * 100
    tissue_percentages.append(tissue_pct)
    slide_names.append(slide.name)

# Bar plot
plt.figure(figsize=(12, 6))
plt.bar(range(len(slide_names)), tissue_percentages)
plt.xticks(range(len(slide_names)), slide_names, rotation=45, ha='right')
plt.ylabel('Tissue Coverage (%)')
plt.title('Tissue Coverage Across Slides')
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.show()
```

## Filter Effect Visualization

### Before and After Filtering

```python
from histolab.filters.image_filters import RgbToGrayscale, HistogramEqualization
from histolab.filters.compositions import Compose

# Define filter pipeline
filter_pipeline = Compose([
    RgbToGrayscale(),
    HistogramEqualization()
])

# Original vs filtered
fig, axes = plt.subplots(1, 2, figsize=(12, 6))

axes[0].imshow(slide.thumbnail)
axes[0].set_title("Original")
axes[0].axis('off')

filtered = filter_pipeline(slide.thumbnail)
axes[1].imshow(filtered, cmap='gray')
axes[1].set_title("After Filtering")
axes[1].axis('off')

plt.tight_layout()
plt.show()
```

### Multi-Step Filter Visualization

```python
from histolab.filters.image_filters import RgbToGrayscale, OtsuThreshold
from histolab.filters.morphological_filters import BinaryDilation, RemoveSmallObjects

# Individual filter steps
steps = [
    ("Original", None),
    ("Grayscale", RgbToGrayscale()),
    ("Otsu Threshold", Compose([RgbToGrayscale(), OtsuThreshold()])),
    ("After Dilation", Compose([RgbToGrayscale(), OtsuThreshold(), BinaryDilation(disk_size=5)])),
    ("Remove Small Objects", Compose([RgbToGrayscale(), OtsuThreshold(), BinaryDilation(disk_size=5), RemoveSmallObjects(area_threshold=500)]))
]

fig, axes = plt.subplots(1, len(steps), figsize=(20, 4))

for idx, (title, filter_fn) in enumerate(steps):
    if filter_fn is None:
        axes[idx].imshow(slide.thumbnail)
    else:
        result = filter_fn(slide.thumbnail)
        axes[idx].imshow(result, cmap='gray')
    axes[idx].set_title(title, fontsize=10)
    axes[idx].axis('off')

plt.tight_layout()
plt.show()
```

## Exporting Visualizations

### High-Resolution Exports

```python
# Export high-resolution figure
fig, ax = plt.subplots(figsize=(20, 20))
ax.imshow(slide.thumbnail)
ax.axis('off')
plt.savefig("slide_high_res.png", dpi=300, bbox_inches='tight', pad_inches=0)
plt.close()
```

### PDF Reports

```python
from matplotlib.backends.backend_pdf import PdfPages

# Create multi-page PDF report
with PdfPages('slide_report.pdf') as pdf:
    # Page 1: Slide thumbnail
    fig1, ax1 = plt.subplots(figsize=(10, 10))
    ax1.imshow(slide.thumbnail)
    ax1.set_title(f"Slide: {slide.name}")
    ax1.axis('off')
    pdf.savefig(fig1, bbox_inches='tight')
    plt.close()

    # Page 2: Tissue mask
    fig2, ax2 = plt.subplots(figsize=(10, 10))
    mask = TissueMask()(slide)
    ax2.imshow(mask, cmap='gray')
    ax2.set_title("Tissue Mask")
    ax2.axis('off')
    pdf.savefig(fig2, bbox_inches='tight')
    plt.close()

    # Page 3: Tile locations
    fig3, ax3 = plt.subplots(figsize=(10, 10))
    tiler = RandomTiler(tile_size=(512, 512), n_tiles=30)
    tiler.locate_tiles(slide)
    pdf.savefig(fig3, bbox_inches='tight')
    plt.close()
```

## Interactive Visualization (Jupyter)

### IPython Widgets for Exploration

```python
from ipywidgets import interact, IntSlider
import matplotlib.pyplot as plt
from histolab.filters.morphological_filters import BinaryDilation

@interact(disk_size=IntSlider(min=1, max=20, value=5))
def explore_dilation(disk_size):
    """Interactive dilation exploration."""
    filter_pipeline = Compose([
        RgbToGrayscale(),
        OtsuThreshold(),
        BinaryDilation(disk_size=disk_size)
    ])
    result = filter_pipeline(slide.thumbnail)

    plt.figure(figsize=(10, 10))
    plt.imshow(result, cmap='gray')
    plt.title(f"Binary Dilation (disk_size={disk_size})")
    plt.axis('off')
    plt.show()
```

## Best Practices

1. **Always preview before processing**: Use thumbnails and `locate_tiles()` to validate settings
2. **Use side-by-side comparisons**: Show before/after for filter effects
3. **Label clearly**: Include titles, axes labels, and legends
4. **Export high-resolution**: Use 300 DPI for publication-quality figures
5. **Save intermediate visualizations**: Document processing steps
6. **Use colormaps appropriately**: 'gray' for binary masks, 'viridis' for heatmaps
7. **Create reusable visualization functions**: Standardize reporting across projects
