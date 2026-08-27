---
name: deepspot-m
description: Generate transcriptome-wide virtual spatial transcriptomics from H&E histology with DeepSpot-M. Use when you need spatial gene expression in log1p-CPM for 224x224 tiles at about 20x, want to query protein-coding genes by symbol instead of a fixed panel, or want to run prediction across a whole slide after tiling with histolab.
---

# DeepSpot-M

## Overview

DeepSpot-M is a multimodal foundation model that maps a 224x224 H&E histology tile to
spatial gene expression in log1p-CPM. The output is virtual spatial transcriptomics: one
value per queried gene per tile, laid out on the grid the tiles came from.

A LoRA-adapted pathology foundation backbone (Midnight) tokenises the tile. A
cross-attention gene decoder lets each gene query attend to the patch tokens, and a gene
router hypernetwork builds gene-specific projections from frozen biological embeddings
(Evo 2, Orthrus, ProtT5, scGPT, Apertus). Genes enter the model as queryable embeddings
rather than fixed output slots, so the released model covers a ~19k protein-coding gene
panel including genes unseen in training. The panel ships with the weights as
`tokens.csv` and is exposed as `model.gene_names`; genes outside it cannot be queried in
this release.

Applied to TCGA, the model produced a virtual spatial transcriptomics atlas of 28,664
slides across 32 cancer types.

## Licensing

The code is PolyForm Noncommercial 1.0.0 and the weights are CC-BY-NC-SA-4.0. Use it for
noncommercial research and check both licences before redistributing outputs.

## Installation

```bash
uv pip install deepspotm==1.0.0
```

Version 1.0.0 targets Python 3.10 to 3.13 and pulls in PyTorch. Install the PyTorch build
that matches your CUDA version first if you want GPU inference.

## Model access

The weights are gated:

1. Open <https://huggingface.co/ratschlab/DeepSpotM> and request access.
2. Once access is granted, authenticate the machine that will download them:

```bash
huggingface-cli login
```

`from_pretrained` reads that cached token, so a login is needed once per machine.

## Quick start

```python
from deepspotm import DeepSpotM

model, image_processor = DeepSpotM.from_pretrained("ratschlab/DeepSpotM", source="scgpt")

vals = model.predict_genes(image_processor(pil_tile).unsqueeze(0), ["EPCAM", "CD3D"])
```

`pil_tile` is a PIL image of exactly 224x224 pixels. `image_processor` turns it into a
tensor, `unsqueeze(0)` adds the batch dimension, and `predict_genes` takes the batch plus a
list of HGNC gene symbols. Values come back in log1p-CPM, aligned with the gene list you
passed, so keep that list beside the output to keep the columns labelled. Symbols must be
in the released ~19k-gene panel (`model.gene_names`); an unknown symbol raises `KeyError`
naming the offending genes.

## Tile requirements

Tiles must be 224x224 RGB at roughly 20x magnification (about 0.5 microns per pixel). Check
the size at the boundary of your pipeline rather than passing an unchecked crop through:

```python
TILE_PX = 224

def require_tile(tile):
    """Return an RGB 224x224 tile, or raise if the crop is the wrong size."""
    if tile.size != (TILE_PX, TILE_PX):
        raise ValueError(
            f"DeepSpot-M expects a {TILE_PX}x{TILE_PX} tile at about 20x "
            f"(~0.5 microns per pixel); got {tile.size[0]}x{tile.size[1]}. "
            "Re-tile at the matching level or resample the crop."
        )
    return tile.convert("RGB")
```

Extract tiles at the slide level whose resolution is nearest 0.5 microns per pixel, then
crop to 224x224 there. Resampling from a coarser level changes the texture the backbone
reads.

## Keep the dependency optional

`deepspotm` and its weights are a heavy, gated dependency. Import it inside the function
that needs it so the surrounding project installs, imports and tests without it, and turn
an `ImportError` into a message that names every step:

```python
DEEPSPOTM_HELP = (
    "DeepSpot-M is unavailable. Install it with `uv pip install deepspotm==1.0.0`, request "
    "access to the gated weights at https://huggingface.co/ratschlab/DeepSpotM, then "
    "authenticate with `huggingface-cli login`."
)

def load_deepspotm(source="scgpt"):
    try:
        from deepspotm import DeepSpotM
    except ImportError as exc:
        raise RuntimeError(DEEPSPOTM_HELP) from exc
    return DeepSpotM.from_pretrained("ratschlab/DeepSpotM", source=source)
```

## Embedding sources

`source` selects which frozen gene embedding the router builds projections from. It is one
of five values:

| `source`  | Gene embedding                    |
| --------- | --------------------------------- |
| `evo2`    | genomic sequence                  |
| `orthrus` | RNA                               |
| `prott5`  | protein sequence                  |
| `scgpt`   | single-cell expression            |
| `apertus` | language model                    |

Each gives a different view of gene identity. Pick one per run, and run the same tiles
through more than one source when the choice matters to your analysis. See
`references/api.md` for the full call surface, batching and device placement, gene symbol
handling and output units.

## Whole slide workflow

Prediction is per tile, so a slide-scale run is a tiling step followed by batched
inference:

1. Extract 224x224 tiles on a grid with the `histolab` skill, keeping each tile's
   coordinates.
2. Process and stack tiles into batches with `torch.stack`.
3. Call `predict_genes` once per batch with the same gene list.
4. Concatenate the batches into a tiles-by-genes matrix and attach the coordinates.

That matrix is the virtual spatial transcriptomics map for the slide, and it drops
straight into `AnnData` for downstream spatial analysis. `references/whole_slide.md` has a
worked loop, batch sizing and an `AnnData` assembly step.

## Common use cases

- Spatial expression maps for marker genes across a tumour section.
- Transcriptome-wide prediction over a slide cohort with no matching assay run.
- Querying any of the ~19k panel genes by symbol, including genes unseen in training —
  far beyond the few hundred genes of a typical spatial assay panel.
- Adding an expression channel to a morphology-only histology pipeline.
- Building a slide-level cohort atlas, as done for TCGA.

## Detailed references

- `references/api.md`: `from_pretrained` and `predict_genes` in full, the five embedding
  sources and how to choose, batching, device placement, gene symbol handling, and
  converting log1p-CPM output.
- `references/whole_slide.md`: tiling with histolab, a slide-scale prediction loop,
  assembling and storing a tiles-by-genes matrix, and cohort-scale runs.

## Primary sources

- Paper: <https://doi.org/10.64898/2026.06.19.26356060> (medRxiv, posted 22 June 2026)
- Code: <https://github.com/ratschlab/DeepSpotM>
- Weights: <https://huggingface.co/ratschlab/DeepSpotM>
- PyPI: <https://pypi.org/project/deepspotm/>

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/deepspot-m/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/api.md`

# DeepSpot-M API reference

Everything here builds on the two calls in `SKILL.md`: `DeepSpotM.from_pretrained` and
`model.predict_genes`.

## Loading a model

```python
from deepspotm import DeepSpotM

model, image_processor = DeepSpotM.from_pretrained("ratschlab/DeepSpotM", source="scgpt")
```

`from_pretrained` returns two objects:

- `model`: the PyTorch model that answers gene queries.
- `image_processor`: the transform that turns one 224x224 PIL tile into the tensor the
  model reads. Always use the processor that came back with the model rather than a
  hand-written transform, so normalisation matches the weights.

Arguments:

- The repository id, `"ratschlab/DeepSpotM"`. It is gated, so request access on the model
  page and run `huggingface-cli login` before the first call.
- `source`: which frozen gene embedding the router builds gene-specific projections from.
  One of `evo2`, `orthrus`, `prott5`, `scgpt`, `apertus`.

The first call downloads weights into the Hugging Face cache. Set `HF_HOME` to place that
cache on a volume with room for it, which matters on a shared cluster where the default
home directory is small.

## Choosing an embedding source

| `source`  | Gene embedding         |
| --------- | ---------------------- |
| `evo2`    | genomic sequence       |
| `orthrus` | RNA                    |
| `prott5`  | protein sequence       |
| `scgpt`   | single-cell expression |
| `apertus` | language model         |

The gene router turns whichever embedding you pick into per-gene projections, which is
what makes genes queryable rather than fixed outputs. Each source describes gene identity
from a different modality, so the same gene is represented differently under each one.

Pick one source per run and keep it fixed across every tile in a slide or cohort, so the
values stay comparable. When the choice matters to a conclusion, run the same tiles
through several sources and report the values side by side:

```python
genes = ["EPCAM", "CD3D", "PTPRC"]

per_source = {}
for source in ("scgpt", "prott5", "evo2"):
    model, image_processor = DeepSpotM.from_pretrained("ratschlab/DeepSpotM", source=source)
    tiles = torch.stack([image_processor(require_tile(t)) for t in pil_tiles])
    per_source[source] = model.predict_genes(tiles, genes)
```

Reload the model when you change `source`, and rebuild the tile batch with the processor
returned alongside it.

## Predicting genes

```python
vals = model.predict_genes(image_processor(pil_tile).unsqueeze(0), ["EPCAM", "CD3D"])
```

The first argument is a batch tensor of processed tiles. The second is a list of gene
symbols. A single tile still needs the batch dimension, which is what `unsqueeze(0)` adds.

### Gene symbols

Pass HGNC gene symbols as uppercase strings, for example `EPCAM`, `CD3D`, `PTPRC`,
`MKI67`. The queryable genes are the ~19k-symbol panel shipped with the weights as
`tokens.csv`, exposed on the loaded model as `model.gene_names`. A symbol outside that
panel raises `KeyError` naming the offending genes, and predicting genes outside the
panel is not part of this release. Check membership up front when a gene list comes from
elsewhere:

```python
panel = set(model.gene_names)
missing = [g for g in genes if g not in panel]
if missing:
    raise ValueError(f"Not in the DeepSpot-M panel: {missing}")
```

Two habits keep a run reproducible:

- Map aliases to current HGNC symbols before querying, so `CD45` becomes `PTPRC`. Reading
  the list from a file keeps the mapping visible in the run.
- Keep the gene list beside the output. Values come back in the order requested, and the
  list is the only label the array carries.

```python
genes = [line.strip() for line in open("genes.txt") if line.strip()]
vals = model.predict_genes(tiles, genes)
```

Ask for every gene you need in one call rather than looping one gene at a time. The tile
tokens are computed once per batch and reused across the gene queries.

## Batching

`image_processor` handles one tile, so build a batch by stacking:

```python
import torch

batch = torch.stack([image_processor(require_tile(t)) for t in pil_tiles])
vals = model.predict_genes(batch, genes)
```

Batch size trades throughput against memory. Start at 32 tiles on a GPU and 8 on CPU, then
raise it while memory allows. Memory grows with both the batch and the number of genes in
one call, so lower one when the other is large.

## Device placement

`from_pretrained` accepts a `device` argument and returns the model already in eval mode
on that device, and `predict_genes` runs under `no_grad` on its own. So device handling
is one argument plus putting each batch on the same device:

```python
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
model, image_processor = DeepSpotM.from_pretrained(
    "ratschlab/DeepSpotM", source="scgpt", device=device
)

vals = model.predict_genes(batch.to(device), genes)
```

Keeping the model on the device across batches is what makes a slide-scale run practical.
Move results back with `.cpu()` before converting to NumPy.

## Output units

Values are log1p-CPM, the same scale as `log1p` normalised counts per million in a
single-cell or spatial expression matrix. It is the scale most downstream tools expect, so
feed it straight into clustering, correlation or spatial statistics.

To read values as CPM instead, invert the transform:

```python
import numpy as np

cpm = np.expm1(vals.cpu().numpy())
```

Compare values across tiles and slides on the log1p-CPM scale, since that is the scale the
model produces.

## Handling the gated download

`from_pretrained` fails when the machine has no access token or the access request is
still pending. Report the whole path back to a working call rather than the raw error:

```python
DEEPSPOTM_HELP = (
    "DeepSpot-M is unavailable. Install it with `uv pip install deepspotm==1.0.0`, request "
    "access to the gated weights at https://huggingface.co/ratschlab/DeepSpotM, then "
    "authenticate with `huggingface-cli login`."
)

def load_deepspotm(source="scgpt"):
    try:
        from deepspotm import DeepSpotM
    except ImportError as exc:
        raise RuntimeError(DEEPSPOTM_HELP) from exc
    try:
        return DeepSpotM.from_pretrained("ratschlab/DeepSpotM", source=source)
    except Exception as exc:
        raise RuntimeError(DEEPSPOTM_HELP) from exc
```

On a cluster node with no outbound network, download the weights once on a login node and
point `HF_HOME` at the shared cache.

## Primary sources

- Paper: <https://doi.org/10.64898/2026.06.19.26356060> (medRxiv, posted 22 June 2026)
- Code: <https://github.com/ratschlab/DeepSpotM>
- Weights: <https://huggingface.co/ratschlab/DeepSpotM>
- PyPI: <https://pypi.org/project/deepspotm/>

### `references/whole_slide.md`

# Whole slide and cohort runs

DeepSpot-M predicts per tile. A slide-scale virtual spatial transcriptomics map is a
tiling step, a batched prediction loop, and an assembly step that puts the values back on
the slide grid.

## 1. Pick the level that gives about 20x

Tiles must be 224x224 at roughly 20x, near 0.5 microns per pixel. Read the resolution off
the slide rather than assuming level 0 is 20x, since many scanners write level 0 at 40x:

```python
import openslide

slide = openslide.open_slide("slide.svs")
mpp_x = float(slide.properties.get(openslide.PROPERTY_NAME_MPP_X))
downsamples = slide.level_downsamples

level = min(
    range(slide.level_count),
    key=lambda i: abs(mpp_x * downsamples[i] - 0.5),
)
```

Tile at that level. A slide already scanned at 20x gives level 0; a 40x slide usually
gives level 1.

## 2. Extract a tile grid

Use the `histolab` skill for tiling. A grid tiler at 224x224 with a tissue check covers
the section and skips background:

```python
from histolab.slide import Slide
from histolab.tiler import GridTiler

slide = Slide("slide.svs", processed_path="tiles/")

tiler = GridTiler(
    tile_size=(224, 224),
    level=level,
    check_tissue=True,
    tissue_percent=80.0,
    pixel_overlap=0,
)
tiler.extract(slide)
```

Keep each tile's coordinates. `ScoreTiler.extract(slide, report_path="tiles_report.csv")`
writes a CSV with `tile_name,x_coord,y_coord,level,...`, which is the least fragile way to
carry them. See the `histolab` skill for tissue masks, filters and the other tilers.

## 3. Predict in batches

Load the model once, then stream tiles through it. Reloading per batch redownloads nothing
but rebuilds the model each time, which dominates the runtime of a slide:

```python
from pathlib import Path

import torch
from PIL import Image
from deepspotm import DeepSpotM

TILE_PX = 224

def require_tile(tile):
    if tile.size != (TILE_PX, TILE_PX):
        raise ValueError(
            f"DeepSpot-M expects a {TILE_PX}x{TILE_PX} tile at about 20x "
            f"(~0.5 microns per pixel); got {tile.size[0]}x{tile.size[1]}."
        )
    return tile.convert("RGB")

def batched(items, size):
    for start in range(0, len(items), size):
        yield items[start : start + size]

device = "cuda" if torch.cuda.is_available() else "cpu"
model, image_processor = DeepSpotM.from_pretrained(
    "ratschlab/DeepSpotM", source="scgpt", device=device
)

genes = ["EPCAM", "CD3D", "PTPRC", "MKI67"]
tile_paths = sorted(Path("tiles/").glob("*.png"))

chunks = []
for paths in batched(tile_paths, 32):
    tiles = [require_tile(Image.open(p)) for p in paths]
    batch = torch.stack([image_processor(t) for t in tiles]).to(device)
    chunks.append(model.predict_genes(batch, genes).cpu())

expression = torch.cat(chunks).numpy()  # tiles by genes, log1p-CPM
```

Batch sizing: start at 32 tiles on a GPU and 8 on CPU. Memory grows with both the batch
size and the number of genes requested in one call, so lower one when the other is large.
Ask for the full gene list in each call rather than looping gene by gene, since the tile
tokens are computed once per batch and reused across gene queries.

## 4. Assemble the slide map

Pair the matrix with the tile coordinates and the gene list. `AnnData` is the natural
container, and it is what spatial analysis tools read:

```python
import anndata as ad
import numpy as np
import pandas as pd

report = pd.read_csv("tiles_report.csv")
coords = report[["x_coord", "y_coord"]].to_numpy(dtype=float)

adata = ad.AnnData(
    X=expression,
    obs=pd.DataFrame({"tile_name": report["tile_name"]}).set_index("tile_name"),
    var=pd.DataFrame(index=pd.Index(genes, name="gene")),
)
adata.obsm["spatial"] = coords
adata.uns["deepspotm"] = {
    "source": "scgpt",
    "units": "log1p-CPM",
    "tile_px": 224,
    "level": int(level),
}
adata.write_h5ad("slide.h5ad")
```

Recording `source`, `units` and `level` in `uns` keeps the run readable later, and makes it
obvious when two slides were produced under different settings.

## 5. Plot a gene

```python
import matplotlib.pyplot as plt

values = adata[:, "EPCAM"].X.ravel()
plt.scatter(coords[:, 0], -coords[:, 1], c=values, s=6, cmap="viridis")
plt.gca().set_aspect("equal")
plt.colorbar(label="EPCAM (log1p-CPM)")
```

Negating the y coordinate puts the map in slide orientation, since slide coordinates grow
downward.

## 6. Cohort scale

For many slides, run one slide per process and write one `.h5ad` per slide rather than
holding a cohort in memory:

```python
for svs in sorted(Path("cohort/").glob("*.svs")):
    out = Path("out") / f"{svs.stem}.h5ad"
    if out.exists():
        continue          # resume without recomputing finished slides
    run_slide(svs, out)   # steps 1 to 4 above
```

Points worth fixing across a cohort:

- One `source` for every slide, so values stay comparable.
- One gene list, stored in a file and read by every run.
- The same target resolution, chosen per slide from its own metadata.
- A skip-if-exists guard, so an interrupted cohort resumes where it stopped.

Concatenate afterwards with `ad.concat(slides, label="slide_id")` when a cohort-level
matrix is needed. This is the shape of the run that produced the TCGA atlas of 28,664
slides across 32 cancer types.

## Primary sources

- Paper: <https://doi.org/10.64898/2026.06.19.26356060> (medRxiv, posted 22 June 2026)
- Code: <https://github.com/ratschlab/DeepSpotM>
- Weights: <https://huggingface.co/ratschlab/DeepSpotM>
