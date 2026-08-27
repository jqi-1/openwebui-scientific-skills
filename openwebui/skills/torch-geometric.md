---
name: torch-geometric
description: PyTorch Geometric (PyG) for graph neural networks — node/link/graph classification, message passing (GCN, GAT, GraphSAGE, GIN), heterogeneous graphs, neighbor sampling, and custom datasets. Use when working with torch_geometric, not for general NetworkX analytics or non-graph PyTorch models.
---

# PyTorch Geometric (PyG)

PyG is the standard library for Graph Neural Networks built on PyTorch. It provides data structures for graphs, 60+ GNN layer implementations, scalable mini-batch training, and support for heterogeneous graphs.

## Installation

Tested against **torch-geometric 2.7.x** (Oct 2025). Requires **Python 3.10+** and **PyTorch 2.6+**.

```bash
# 1. Install PyTorch first (match your CUDA/CPU setup — see https://pytorch.org/get-started/locally/)
uv pip install torch

# 2. Core PyG (no extension wheels required for basic usage)
uv pip install torch_geometric
```

Optional accelerated ops (`pyg-lib`, `torch-scatter`, `torch-sparse`, `torch-cluster`) are **not required** for basic PyG usage (since PyG 2.3). Install version-matched wheels from the [PyG wheel index](https://data.pyg.org/whl) after checking your PyTorch and CUDA versions:

```bash
python -c "import torch; print(torch.__version__, torch.version.cuda)"
# Then install wheels for your torch+CUDA combo, e.g.:
uv pip install pyg-lib torch-scatter torch-sparse torch-cluster \
  -f https://data.pyg.org/whl/torch-2.8.0+cu128.html
```

Check your version:

```python
import torch_geometric
print(torch_geometric.__version__)
```

**Conda:** the `pyg` conda channel is no longer maintained for PyTorch >2.5 — use `uv pip install` and the wheel index above instead.

### PyG 2.7 notes

PyG 2.7 dropped Python 3.9 and PyTorch ≤2.5. See the [2.7.0 release notes](https://github.com/pyg-team/pytorch_geometric/releases/tag/2.7.0) for PyTorch 2.6–2.8 compatibility tables. `torch_geometric.distributed` is deprecated — use standard `torch.distributed` DDP (see `references/scaling.md`).

## Core Concepts

### Graph Data: `Data` and `HeteroData`

A graph lives in a `Data` object. The key attributes:

```python
from torch_geometric.data import Data

data = Data(
    x=node_features,          # [num_nodes, num_node_features]
    edge_index=edge_index,     # [2, num_edges] — COO format, dtype=torch.long
    edge_attr=edge_features,   # [num_edges, num_edge_features]
    y=labels,                  # node-level [num_nodes, *] or graph-level [1, *]
    pos=positions,             # [num_nodes, num_dimensions] (for point clouds/spatial)
)
```

**`edge_index` format is critical**: it's a `[2, num_edges]` tensor where `edge_index[0]` = source nodes, `edge_index[1]` = target nodes. It is NOT a list of tuples. If you have edge pairs as rows, transpose and call `.contiguous()`:

```python
# If edges are [[src1, dst1], [src2, dst2], ...] — transpose first:
edge_index = edge_pairs.t().contiguous()
```

For undirected graphs, include both directions: edge (0,1) needs both `[0,1]` and `[1,0]` in edge_index.

For heterogeneous graphs, use `HeteroData` — see the Heterogeneous Graphs section below.

### Datasets

PyG bundles many standard datasets that auto-download and preprocess:

```python
from torch_geometric.datasets import Planetoid, TUDataset

# Single-graph node classification (Cora, Citeseer, Pubmed)
dataset = Planetoid(root='./data', name='Cora')
data = dataset[0]  # single graph with train/val/test masks

# Multi-graph classification (ENZYMES, MUTAG, IMDB-BINARY, etc.)
dataset = TUDataset(root='./data', name='ENZYMES')
# dataset[0], dataset[1], ... are individual graphs
```

Common datasets by task:
- **Node classification**: Planetoid (Cora/Citeseer/Pubmed), OGB (ogbn-arxiv, ogbn-products, ogbn-mag)
- **Graph classification**: TUDataset (MUTAG, ENZYMES, PROTEINS, IMDB-BINARY), OGB (ogbg-molhiv)
- **Link prediction**: OGB (ogbl-collab, ogbl-citation2)
- **Molecular**: QM7, QM9, MoleculeNet
- **Point cloud/mesh**: ShapeNet, ModelNet10/40, FAUST

### Transforms

Transforms preprocess or augment graph data, analogous to torchvision transforms:

```python
import torch_geometric.transforms as T

# Common transforms
T.NormalizeFeatures()    # Row-normalize node features to sum to 1
T.ToUndirected()         # Add reverse edges to make graph undirected
T.AddSelfLoops()         # Add self-loop edges
T.KNNGraph(k=6)          # Build k-NN graph from point cloud positions
T.RandomJitter(0.01)     # Random noise augmentation on positions
T.Compose([...])         # Chain multiple transforms

# Apply as pre_transform (once, saved to disk) or transform (every access)
dataset = ShapeNet(root='./data', pre_transform=T.KNNGraph(k=6),
                   transform=T.RandomJitter(0.01))
```

## Building GNN Models

### Quick Start: Using Built-in Layers

The fastest way to build a GNN — stack conv layers from `torch_geometric.nn`:

```python
import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv

class GCN(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels):
        super().__init__()
        self.conv1 = GCNConv(in_channels, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, out_channels)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index).relu()
        x = F.dropout(x, p=0.5, training=self.training)
        x = self.conv2(x, edge_index)
        return x
```

**Important**: PyG conv layers do NOT include activation functions — apply them yourself after each layer. This is by design for flexibility.

### Choosing a Conv Layer

Pick based on your task and graph structure:

| Layer | Best for | Key idea |
|-------|----------|----------|
| `GCNConv` | Homogeneous, semi-supervised node classification | Spectral-inspired, degree-normalized aggregation |
| `GATConv` / `GATv2Conv` | When neighbor importance varies | Attention-weighted messages |
| `SAGEConv` | Large graphs, inductive settings | Sampling-friendly, learnable aggregation |
| `GINConv` | Graph classification, maximizing expressiveness | As powerful as WL test |
| `TransformerConv` | Rich edge features, complex interactions | Multi-head attention with edge features |
| `EdgeConv` | Point clouds, dynamic graphs | MLP on edge features (x_i, x_j - x_i) |
| `RGCNConv` | Heterogeneous with many relation types | Relation-specific weight matrices |
| `HGTConv` | Heterogeneous graphs | Type-specific attention |

All conv layers accept `(x, edge_index)` at minimum. Many also accept `edge_attr` for edge features.

### Lazy Initialization

Use `-1` for input channels to let PyG infer dimensions automatically — especially useful for heterogeneous models:

```python
conv = SAGEConv((-1, -1), 64)  # Input dims inferred on first forward pass
# Initialize lazy modules:
with torch.no_grad():
    out = model(data.x, data.edge_index)
```

### High-Level Model APIs

For common architectures, PyG provides ready-made model classes:

```python
from torch_geometric.nn import GraphSAGE, GCN, GAT, GIN

model = GraphSAGE(
    in_channels=dataset.num_features,
    hidden_channels=64,
    out_channels=dataset.num_classes,
    num_layers=2,
)
```

### Custom Layers via MessagePassing

To implement a novel GNN layer, subclass `MessagePassing`. The framework is:

1. `propagate()` orchestrates the message passing
2. `message()` defines what info flows along each edge (the phi function)
3. `aggregate()` combines messages at each node (sum/mean/max)
4. `update()` transforms the aggregated result (the gamma function)

```python
from torch_geometric.nn import MessagePassing
from torch_geometric.utils import add_self_loops, degree

class MyConv(MessagePassing):
    def __init__(self, in_channels, out_channels):
        super().__init__(aggr='add')  # "add", "mean", or "max"
        self.lin = torch.nn.Linear(in_channels, out_channels)

    def forward(self, x, edge_index):
        # Pre-processing before message passing
        x = self.lin(x)
        # Start message passing
        return self.propagate(edge_index, x=x)

    def message(self, x_j):
        # x_j: features of source nodes for each edge [num_edges, features]
        # The _j suffix auto-indexes source nodes, _i indexes target nodes
        return x_j
```

**The `_i` / `_j` convention**: any tensor passed to `propagate()` can be auto-indexed by appending `_i` (target/central node) or `_j` (source/neighbor node) in the `message()` signature. So if you pass `x=...` to propagate, you can access `x_i` and `x_j` in message().

Read `references/message_passing.md` for the full GCN and EdgeConv implementation examples.

## Task-Specific Patterns

### Node Classification

```python
# Full-batch training on a single graph (e.g., Cora)
model.train()
for epoch in range(200):
    optimizer.zero_grad()
    out = model(data.x, data.edge_index)
    loss = F.cross_entropy(out[data.train_mask], data.y[data.train_mask])
    loss.backward()
    optimizer.step()

# Evaluation — train(False) puts the model in inference mode (disables dropout/BN)
model.train(False)
pred = model(data.x, data.edge_index).argmax(dim=1)
acc = (pred[data.test_mask] == data.y[data.test_mask]).float().mean()
```

### Graph Classification

Multiple graphs — use `DataLoader` for mini-batching and global pooling to get graph-level representations:

```python
from torch_geometric.loader import DataLoader
from torch_geometric.nn import GCNConv, global_mean_pool

loader = DataLoader(dataset, batch_size=32, shuffle=True)

class GraphClassifier(torch.nn.Module):
    def __init__(self, in_ch, hidden_ch, out_ch):
        super().__init__()
        self.conv1 = GCNConv(in_ch, hidden_ch)
        self.conv2 = GCNConv(hidden_ch, hidden_ch)
        self.lin = torch.nn.Linear(hidden_ch, out_ch)

    def forward(self, x, edge_index, batch):
        x = self.conv1(x, edge_index).relu()
        x = self.conv2(x, edge_index).relu()
        x = global_mean_pool(x, batch)  # [num_graphs_in_batch, hidden_ch]
        return self.lin(x)

# Training loop
for data in loader:
    out = model(data.x, data.edge_index, data.batch)
    loss = F.cross_entropy(out, data.y)
```

PyG's `DataLoader` batches multiple graphs by creating block-diagonal adjacency matrices. The `batch` tensor maps each node to its graph index. Pooling ops (`global_mean_pool`, `global_max_pool`, `global_add_pool`) use this to aggregate per-graph.

### Link Prediction

Split edges into train/val/test, use negative sampling:

```python
from torch_geometric.transforms import RandomLinkSplit

transform = RandomLinkSplit(
    num_val=0.1,
    num_test=0.1,
    is_undirected=True,
    add_negative_train_samples=False,
)
train_data, val_data, test_data = transform(data)

# Encode nodes, then score edges
z = model.encode(train_data.x, train_data.edge_index)
# Positive edges
pos_score = (z[train_data.edge_label_index[0]] * z[train_data.edge_label_index[1]]).sum(dim=1)
```

Read `references/link_prediction.md` for the complete link prediction guide: GAE/VGAE autoencoders, full training loops, LinkNeighborLoader for large graphs, heterogeneous link prediction, and evaluation metrics.

## Scaling to Large Graphs

For graphs that don't fit in GPU memory, use neighbor sampling via `NeighborLoader`:

```python
from torch_geometric.loader import NeighborLoader

train_loader = NeighborLoader(
    data,
    num_neighbors=[15, 10],     # Sample 15 neighbors in hop 1, 10 in hop 2
    batch_size=128,              # Number of seed nodes per batch
    input_nodes=data.train_mask, # Which nodes to sample from
    shuffle=True,
)

for batch in train_loader:
    batch = batch.to(device)
    out = model(batch.x, batch.edge_index)
    # Only use first batch_size nodes for loss (these are the seed nodes)
    loss = F.cross_entropy(out[:batch.batch_size], batch.y[:batch.batch_size])
```

**Key points about NeighborLoader**:
- `num_neighbors` list length should match GNN depth (number of message passing layers)
- Seed nodes are always the first `batch.batch_size` nodes in the output
- `batch.n_id` maps relabeled indices back to original node IDs
- Works for both `Data` and `HeteroData`
- For link prediction, use `LinkNeighborLoader` instead
- Sampling more than 2-3 hops is generally infeasible (exponential blowup)

Other scalability options: `ClusterLoader` (ClusterGCN), `GraphSAINTSampler`, `ShaDowKHopSampler`. For multi-GPU training, DDP, PyTorch Lightning integration, and `torch.compile` support, read `references/scaling.md`.

## Heterogeneous Graphs

For graphs with multiple node and edge types (social networks, knowledge graphs, recommendation):

```python
from torch_geometric.data import HeteroData

data = HeteroData()

# Node features — indexed by node type string
data['user'].x = torch.randn(1000, 64)
data['movie'].x = torch.randn(500, 128)

# Edge indices — indexed by (src_type, edge_type, dst_type) triplet
data['user', 'rates', 'movie'].edge_index = torch.randint(0, 500, (2, 3000))
data['user', 'follows', 'user'].edge_index = torch.randint(0, 1000, (2, 5000))

# Access convenience dicts
data.x_dict        # {'user': tensor, 'movie': tensor}
data.edge_index_dict  # {('user','rates','movie'): tensor, ...}
data.metadata()    # ([node_types], [edge_types])
```

### Three ways to build heterogeneous GNNs

**1. Auto-convert with `to_hetero()`** — write a homogeneous model, convert automatically:

```python
from torch_geometric.nn import SAGEConv, to_hetero

class GNN(torch.nn.Module):
    def __init__(self, hidden_channels, out_channels):
        super().__init__()
        self.conv1 = SAGEConv((-1, -1), hidden_channels)
        self.conv2 = SAGEConv((-1, -1), out_channels)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index).relu()
        x = self.conv2(x, edge_index)
        return x

model = GNN(64, dataset.num_classes)
model = to_hetero(model, data.metadata(), aggr='sum')

# Now accepts dicts:
out = model(data.x_dict, data.edge_index_dict)
```

Use `(-1, -1)` for bipartite input channels (source, target may differ). Lazy init handles the rest.

**2. `HeteroConv` wrapper** — different conv per edge type:

```python
from torch_geometric.nn import HeteroConv, GCNConv, SAGEConv, GATConv

conv = HeteroConv({
    ('paper', 'cites', 'paper'): GCNConv(-1, 64),
    ('author', 'writes', 'paper'): SAGEConv((-1, -1), 64),
    ('paper', 'rev_writes', 'author'): GATConv((-1, -1), 64, add_self_loops=False),
}, aggr='sum')
```

**3. Native heterogeneous operators** like `HGTConv`:

```python
from torch_geometric.nn import HGTConv
conv = HGTConv(hidden_channels, hidden_channels, data.metadata(), num_heads=4)
```

**Important for heterogeneous graphs**:
- Use `T.ToUndirected()` to add reverse edge types for bidirectional message flow
- Disable `add_self_loops` in bipartite conv layers (different source/dest types) — use skip connections instead: `conv(x, edge_index) + lin(x)`
- For NeighborLoader on HeteroData, specify `input_nodes` as `('node_type', mask)` tuple
- `num_neighbors` can be a dict keyed by edge type for fine-grained control

Read `references/heterogeneous.md` for complete examples including training loops and NeighborLoader usage with heterogeneous graphs.

## Custom Datasets

For loading your own data into PyG:

- **Quick (no class needed)**: Create `Data` objects directly and pass a list to `DataLoader`
- **Reusable (fits in RAM)**: Subclass `InMemoryDataset` — override `raw_file_names`, `processed_file_names`, `download()`, `process()`
- **Large (disk-backed)**: Subclass `Dataset` — also override `len()` and `get()`
- **From CSV**: Load node/edge tables with pandas, build mappings to consecutive indices, assemble into `Data` or `HeteroData`
- **From NetworkX**: `from_networkx(G)` converts a NetworkX graph directly
- **From scipy sparse**: `from_scipy_sparse_matrix(adj)` extracts edge_index

Read `references/custom_datasets.md` for complete examples with all patterns, CSV loading with encoders, and the MovieLens walkthrough.

## Explainability

PyG provides `torch_geometric.explain` for interpreting GNN predictions:

```python
from torch_geometric.explain import Explainer, GNNExplainer

explainer = Explainer(
    model=model,
    algorithm=GNNExplainer(epochs=200),
    explanation_type='model',
    node_mask_type='attributes',
    edge_mask_type='object',
    model_config=dict(
        mode='multiclass_classification',
        task_level='node',
        return_type='log_probs',
    ),
)

explanation = explainer(data.x, data.edge_index, index=10)
explanation.visualize_graph()           # Important subgraph
explanation.visualize_feature_importance(top_k=10)  # Feature importance
```

Available algorithms: `GNNExplainer` (optimization-based), `PGExplainer` (parametric, trained), `CaptumExplainer` (gradient-based via Captum), `AttentionExplainer` (attention weights). Works for both homogeneous and heterogeneous graphs.

Read `references/explainability.md` for all algorithms, heterogeneous explanations, evaluation metrics, and PGExplainer training.

## Common Pitfalls

1. **edge_index shape**: Must be `[2, num_edges]`, not `[num_edges, 2]`. Transpose if needed.
2. **Forgetting activations**: Conv layers don't include ReLU/etc — add them manually.
3. **Self-loops in hetero bipartite**: Don't use `add_self_loops=True` when source and dest node types differ. Use skip connections instead.
4. **NeighborLoader slicing**: Only the first `batch.batch_size` nodes are your seed nodes. Slice predictions and labels accordingly.
5. **Undirected graphs**: If your graph is undirected, include edges in both directions in `edge_index`, or use `T.ToUndirected()`.
6. **Lazy init**: Models with `-1` input channels need one forward pass with `torch.no_grad()` before training to initialize parameters.
7. **Global pooling for graph tasks**: Use `global_mean_pool(x, batch)` (not manual reshape) to aggregate node features to graph-level.
8. **num_neighbors alignment**: Keep `len(num_neighbors)` equal to the number of GNN layers. More hops than layers wastes compute; fewer means wasted model capacity.

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/torch-geometric/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/custom_datasets.md`

# Custom Datasets — Full Reference

How to create your own graph datasets and load graph data from raw sources (CSV, pandas, numpy, etc.).

## Quick: No Dataset Class Needed

For synthetic data or one-off graphs, skip the dataset machinery — just create `Data` objects and pass them to `DataLoader`:

```python
from torch_geometric.data import Data
from torch_geometric.loader import DataLoader

data_list = [Data(x=..., edge_index=..., y=...) for _ in range(100)]
loader = DataLoader(data_list, batch_size=32)
```

## InMemoryDataset (fits in RAM)

For reusable datasets that fit in CPU memory. Override 4 methods:

```python
from torch_geometric.data import InMemoryDataset, download_url

class MyDataset(InMemoryDataset):
    def __init__(self, root, transform=None, pre_transform=None, pre_filter=None):
        super().__init__(root, transform, pre_transform, pre_filter)
        self.load(self.processed_paths[0])

    @property
    def raw_file_names(self):
        # Files in raw_dir that must exist to skip download()
        return ['data.csv']

    @property
    def processed_file_names(self):
        # Files in processed_dir that must exist to skip process()
        return ['data.pt']

    def download(self):
        # Download raw files to self.raw_dir
        # Use trusted sources only; verify checksums or signatures before loading.
        download_url('https://example.com/data.csv', self.raw_dir)

    def process(self):
        # Read raw data and create a list of Data objects
        data_list = [...]

        if self.pre_filter is not None:
            data_list = [d for d in data_list if self.pre_filter(d)]
        if self.pre_transform is not None:
            data_list = [self.pre_transform(d) for d in data_list]

        # save() collates list into one big Data + slices dict, then saves
        self.save(data_list, self.processed_paths[0])
```

**Directory structure created automatically:**
```
root/
├── raw/          # raw_dir — downloaded files go here
│   └── data.csv
└── processed/    # processed_dir — processed .pt files go here
    └── data.pt
```

**Key behaviors:**
- `download()` runs only if files in `raw_file_names` are missing from `raw_dir`
- `process()` runs only if files in `processed_file_names` are missing from `processed_dir`
- If you change `pre_transform`, delete the `processed/` directory to reprocess

## Dataset (doesn't fit in RAM)

For very large datasets, save each graph individually:

```python
import os.path as osp
import torch
from torch_geometric.data import Dataset, download_url

class LargeDataset(Dataset):
    def __init__(self, root, transform=None, pre_transform=None):
        super().__init__(root, transform, pre_transform)

    @property
    def raw_file_names(self):
        return ['graph_data.csv']

    @property
    def processed_file_names(self):
        return [f'data_{i}.pt' for i in range(1000)]

    def download(self):
        download_url('...', self.raw_dir)

    def process(self):
        for idx in range(1000):
            data = Data(...)  # Build graph from raw data
            if self.pre_filter is not None and not self.pre_filter(data):
                continue
            if self.pre_transform is not None:
                data = self.pre_transform(data)
            torch.save(data, osp.join(self.processed_dir, f'data_{idx}.pt'))

    def len(self):
        return 1000

    def get(self, idx):
        return torch.load(osp.join(self.processed_dir, f'data_{idx}.pt'))
```

## Loading Graphs from CSV

A common pattern: load node/edge data from CSV files into a HeteroData object.

### Step 1: Load node features

```python
import pandas as pd
import torch

def load_node_csv(path, index_col, encoders=None):
    df = pd.read_csv(path, index_col=index_col)
    # Map original IDs to consecutive 0..N-1 indices
    mapping = {idx: i for i, idx in enumerate(df.index.unique())}

    x = None
    if encoders is not None:
        xs = [encoder(df[col]) for col, encoder in encoders.items()]
        x = torch.cat(xs, dim=-1)

    return x, mapping
```

### Step 2: Load edges

```python
def load_edge_csv(path, src_index_col, src_mapping, dst_index_col, dst_mapping,
                  encoders=None):
    df = pd.read_csv(path)
    src = [src_mapping[idx] for idx in df[src_index_col]]
    dst = [dst_mapping[idx] for idx in df[dst_index_col]]
    edge_index = torch.tensor([src, dst])

    edge_attr = None
    if encoders is not None:
        edge_attrs = [encoder(df[col]) for col, encoder in encoders.items()]
        edge_attr = torch.cat(edge_attrs, dim=-1)

    return edge_index, edge_attr
```

### Step 3: Assemble HeteroData

```python
from torch_geometric.data import HeteroData

# Load nodes
movie_x, movie_mapping = load_node_csv('movies.csv', 'movieId',
    encoders={'genres': GenresEncoder()})
_, user_mapping = load_node_csv('ratings.csv', 'userId')

# Load edges
edge_index, edge_label = load_edge_csv('ratings.csv',
    src_index_col='userId', src_mapping=user_mapping,
    dst_index_col='movieId', dst_mapping=movie_mapping,
    encoders={'rating': IdentityEncoder(dtype=torch.long)})

# Build HeteroData
data = HeteroData()
data['user'].num_nodes = len(user_mapping)
data['movie'].x = movie_x
data['user', 'rates', 'movie'].edge_index = edge_index
data['user', 'rates', 'movie'].edge_label = edge_label
```

### Common Encoders

```python
class IdentityEncoder:
    """Encode a numeric column as-is."""
    def __init__(self, dtype=None):
        self.dtype = dtype
    def __call__(self, df):
        return torch.from_numpy(df.values).view(-1, 1).to(self.dtype)

class GenresEncoder:
    """Multi-hot encode a pipe-separated categorical column."""
    def __init__(self, sep='|'):
        self.sep = sep
    def __call__(self, df):
        genres = set(g for col in df.values for g in col.split(self.sep))
        mapping = {genre: i for i, genre in enumerate(genres)}
        x = torch.zeros(len(df), len(mapping))
        for i, col in enumerate(df.values):
            for genre in col.split(self.sep):
                x[i, mapping[genre]] = 1
        return x
```

For text features, use sentence-transformers:

```python
from sentence_transformers import SentenceTransformer

class SequenceEncoder:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
    @torch.no_grad()
    def __call__(self, df):
        return self.model.encode(df.values, convert_to_tensor=True).cpu()
```

## From NetworkX

```python
from torch_geometric.utils import from_networkx
import networkx as nx

G = nx.karate_club_graph()
data = from_networkx(G)
# Node attributes become data.x, edge attributes become data.edge_attr
```

## From scipy sparse adjacency matrix

```python
from torch_geometric.utils import from_scipy_sparse_matrix

edge_index, edge_attr = from_scipy_sparse_matrix(adj_matrix)
data = Data(x=features, edge_index=edge_index)
```

## Featureless Nodes

If nodes have no features, common options:
- Use `torch.nn.Embedding` to learn features during training
- Set `data['node_type'].num_nodes = N` (for HeteroData)
- Use structural features: degree, clustering coefficient, etc.
- Use `data.x = torch.eye(num_nodes)` (one-hot, only for small graphs)

### `references/explainability.md`

# GNN Explainability — Full Reference

PyG provides `torch_geometric.explain` for interpreting GNN predictions. The module includes a unified `Explainer` interface, several explanation algorithms, visualization, and evaluation metrics.

## The Explainer Interface

The `Explainer` class is the central entry point. Configure it with:
1. An explanation **algorithm** (GNNExplainer, PGExplainer, CaptumExplainer, etc.)
2. An **explanation type** (`"model"` — explain model predictions, or `"phenomenon"` — explain dataset patterns)
3. **Mask types** — which parts of the input to explain (nodes, edges, features)
4. **Post-processing** — how to threshold masks (top-k, hard, etc.)

```python
from torch_geometric.explain import Explainer, GNNExplainer

explainer = Explainer(
    model=model,
    algorithm=GNNExplainer(epochs=200),
    explanation_type='model',          # 'model' or 'phenomenon'
    node_mask_type='attributes',       # 'object', 'common_attributes', 'attributes', or None
    edge_mask_type='object',           # 'object' or None
    model_config=dict(
        mode='multiclass_classification',  # 'binary_classification', 'multiclass_classification', 'regression'
        task_level='node',                  # 'node', 'edge', 'graph'
        return_type='log_probs',            # 'log_probs', 'probs', 'raw'
    ),
)
```

**Mask types explained:**
- `'object'`: One mask value per node/edge (which nodes/edges matter?)
- `'attributes'`: One mask value per node feature dimension (which features matter?)
- `'common_attributes'`: Same feature mask shared across all nodes
- `None`: Don't generate this mask type

## Generating Explanations

### Node classification

```python
# Explain prediction for node at index 10
explanation = explainer(data.x, data.edge_index, index=10)

print(explanation.node_mask)   # [num_nodes, num_features] — importance per feature per node
print(explanation.edge_mask)   # [num_edges] — importance per edge
```

### Graph classification

```python
explainer = Explainer(
    model=model,
    algorithm=GNNExplainer(epochs=200),
    explanation_type='model',
    edge_mask_type='object',
    model_config=dict(
        mode='multiclass_classification',
        task_level='graph',
        return_type='raw',
    ),
)

explanation = explainer(data.x, data.edge_index)
```

## Visualization

```python
# Visualize which features are most important (bar chart)
explanation.visualize_feature_importance(top_k=10)
# Saves to 'feature_importance.png' by default, or pass path=

# Visualize the important subgraph
explanation.visualize_graph()
# Saves to 'graph.png' by default, or pass path=
```

## Available Algorithms

### GNNExplainer

Learns soft masks via optimization. Works for node and graph-level tasks. The most widely used algorithm.

```python
from torch_geometric.explain import GNNExplainer

algorithm = GNNExplainer(epochs=200, lr=0.01)
```

### PGExplainer

A parametric (trained) explainer — learns a neural network that generates edge masks. Must be trained before use, but then generalizes to new graphs. Only supports edge masks (no node masks).

```python
from torch_geometric.explain import PGExplainer

explainer = Explainer(
    model=model,
    algorithm=PGExplainer(epochs=30, lr=0.003),
    explanation_type='phenomenon',     # PGExplainer explains phenomena
    edge_mask_type='object',
    model_config=dict(
        mode='regression',
        task_level='graph',
        return_type='raw',
    ),
    threshold_config=dict(threshold_type='topk', value=10),
)

# Train the explainer first
for epoch in range(30):
    for batch in loader:
        loss = explainer.algorithm.train(
            epoch, model, batch.x, batch.edge_index, target=batch.target
        )

# Then explain
explanation = explainer(data.x, data.edge_index)
```

### CaptumExplainer

Wraps the [Captum](https://captum.ai/) library, giving access to gradient-based attribution methods. Works with both homogeneous and heterogeneous graphs.

```python
from torch_geometric.explain import CaptumExplainer

# Supports: 'IntegratedGradients', 'Saliency', 'Deconvolution',
#           'ShapleyValueSampling', 'GuidedBackprop', etc.
algorithm = CaptumExplainer('IntegratedGradients')
```

Requires `uv pip install captum` (or `uv add captum`).

### AttentionExplainer

Uses attention weights from attention-based GNNs (GATConv, TransformerConv) as edge explanations. No training needed — just reads existing attention scores.

```python
from torch_geometric.explain import AttentionExplainer

algorithm = AttentionExplainer()
```

## Heterogeneous Graph Explanations

For heterogeneous models, the explainer returns `HeteroExplanation` with per-type masks:

```python
from torch_geometric.explain import Explainer, CaptumExplainer

explainer = Explainer(
    model=hetero_model,
    algorithm=CaptumExplainer('IntegratedGradients'),
    explanation_type='model',
    node_mask_type='attributes',
    edge_mask_type='object',
    model_config=dict(
        mode='multiclass_classification',
        task_level='node',
        return_type='probs',
    ),
)

hetero_explanation = explainer(
    data.x_dict,
    data.edge_index_dict,
    index=torch.tensor([1, 3]),
)

# Access per-type masks
hetero_explanation.node_mask_dict    # {'paper': tensor, 'author': tensor, ...}
hetero_explanation.edge_mask_dict    # {('paper','cites','paper'): tensor, ...}
```

## Evaluation Metrics

```python
from torch_geometric.explain import unfaithfulness, fidelity, characterization_score

# Unfaithfulness: how much does the explanation change the prediction?
# Lower is better (0 = perfectly faithful)
score = unfaithfulness(explainer, explanation)

# Fidelity: measures explanation quality via positive/negative fidelity
pos_fidelity, neg_fidelity = fidelity(explainer, explanation)

# Characterization score: combined metric
char_score = characterization_score(pos_fidelity, neg_fidelity)
```

## Post-Processing Masks

Control how raw mask values are converted to final explanations:

```python
explainer = Explainer(
    ...,
    threshold_config=dict(
        threshold_type='topk',    # 'topk', 'hard', or None
        value=10,                  # Top-10 edges for 'topk', threshold value for 'hard'
    ),
)
```

- `'topk'`: Keep only top-k highest-scored elements
- `'hard'`: Binary threshold — elements above `value` are kept
- `None`: Return raw continuous mask values

### `references/heterogeneous.md`

# Heterogeneous Graph Learning — Full Reference

## Creating HeteroData

```python
from torch_geometric.data import HeteroData

data = HeteroData()

# Node features — keyed by node type string
data['paper'].x = ...       # [num_papers, num_features_paper]
data['author'].x = ...      # [num_authors, num_features_author]
data['institution'].x = ... # [num_institutions, num_features_institution]

# Edge indices — keyed by (source_type, edge_type, dest_type) triplet
data['paper', 'cites', 'paper'].edge_index = ...              # [2, num_edges]
data['author', 'writes', 'paper'].edge_index = ...            # [2, num_edges]
data['author', 'affiliated_with', 'institution'].edge_index = ... # [2, num_edges]

# Edge features (optional)
data['paper', 'cites', 'paper'].edge_attr = ...  # [num_edges, num_edge_features]

# Additional node attributes
data['paper'].y = ...           # labels
data['paper'].train_mask = ...  # boolean mask
```

### Accessing data

```python
# Single store access
data['paper']                          # NodeStore for papers
data['paper', 'cites', 'paper']       # EdgeStore for cites edges
data['paper', 'paper']                 # Shorthand if edge type is unambiguous
data['cites']                          # Shorthand if edge type name is unique

# Dict access for model input
data.x_dict                            # {'paper': tensor, 'author': tensor, ...}
data.edge_index_dict                   # {('paper','cites','paper'): tensor, ...}
data.edge_attr_dict

# Metadata
node_types, edge_types = data.metadata()

# Modify
data['paper'].year = ...               # Add new attribute
del data['field_of_study']             # Delete node type
del data['has_topic']                  # Delete edge type

# Convert
data.to('cuda:0')                      # Transfer to GPU
data.to_homogeneous()                  # Convert to typed homogeneous graph
```

### Transforms on HeteroData

```python
import torch_geometric.transforms as T

data = T.ToUndirected()(data)       # Add reverse edge types
data = T.AddSelfLoops()(data)       # Add self-loops for same-type edges
data = T.NormalizeFeatures()(data)  # Normalize features across all types
```

`ToUndirected()` is important — it creates reverse edge types (e.g., `('paper', 'rev_writes', 'author')`) so messages flow in both directions.

## Building Heterogeneous GNN Models

### Option 1: Auto-convert with `to_hetero()`

Write a standard homogeneous GNN, then convert:

```python
from torch_geometric.nn import SAGEConv, to_hetero
import torch_geometric.transforms as T
from torch_geometric.datasets import OGB_MAG

dataset = OGB_MAG(root='./data', preprocess='metapath2vec', transform=T.ToUndirected())
data = dataset[0]

class GNN(torch.nn.Module):
    def __init__(self, hidden_channels, out_channels):
        super().__init__()
        # Use (-1, -1) for lazy init with bipartite support
        self.conv1 = SAGEConv((-1, -1), hidden_channels)
        self.conv2 = SAGEConv((-1, -1), out_channels)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index).relu()
        x = self.conv2(x, edge_index)
        return x

model = GNN(64, dataset.num_classes)
model = to_hetero(model, data.metadata(), aggr='sum')

# Initialize lazy modules
with torch.no_grad():
    out = model(data.x_dict, data.edge_index_dict)
```

With skip-connections (important for attention-based models):

```python
from torch_geometric.nn import GATConv, Linear, to_hetero

class GAT(torch.nn.Module):
    def __init__(self, hidden_channels, out_channels):
        super().__init__()
        self.conv1 = GATConv((-1, -1), hidden_channels, add_self_loops=False)
        self.lin1 = Linear(-1, hidden_channels)
        self.conv2 = GATConv((-1, -1), out_channels, add_self_loops=False)
        self.lin2 = Linear(-1, out_channels)

    def forward(self, x, edge_index):
        # Skip connection replaces self-loops for bipartite message passing
        x = self.conv1(x, edge_index) + self.lin1(x)
        x = x.relu()
        x = self.conv2(x, edge_index) + self.lin2(x)
        return x

model = GAT(64, dataset.num_classes)
model = to_hetero(model, data.metadata(), aggr='sum')
```

### Option 2: HeteroConv wrapper (different conv per edge type)

```python
from torch_geometric.nn import HeteroConv, GCNConv, SAGEConv, GATConv, Linear

class HeteroGNN(torch.nn.Module):
    def __init__(self, hidden_channels, out_channels, num_layers):
        super().__init__()

        self.convs = torch.nn.ModuleList()
        for _ in range(num_layers):
            conv = HeteroConv({
                ('paper', 'cites', 'paper'): GCNConv(-1, hidden_channels),
                ('author', 'writes', 'paper'): SAGEConv((-1, -1), hidden_channels),
                ('paper', 'rev_writes', 'author'): GATConv((-1, -1), hidden_channels,
                                                            add_self_loops=False),
            }, aggr='sum')
            self.convs.append(conv)

        self.lin = Linear(hidden_channels, out_channels)

    def forward(self, x_dict, edge_index_dict):
        for conv in self.convs:
            x_dict = conv(x_dict, edge_index_dict)
            x_dict = {key: x.relu() for key, x in x_dict.items()}
        return self.lin(x_dict['paper'])

model = HeteroGNN(64, dataset.num_classes, num_layers=2)
with torch.no_grad():
    out = model(data.x_dict, data.edge_index_dict)
```

### Option 3: HGTConv (native heterogeneous operator)

```python
from torch_geometric.nn import HGTConv, Linear

class HGT(torch.nn.Module):
    def __init__(self, hidden_channels, out_channels, num_heads, num_layers):
        super().__init__()

        self.lin_dict = torch.nn.ModuleDict()
        for node_type in data.node_types:
            self.lin_dict[node_type] = Linear(-1, hidden_channels)

        self.convs = torch.nn.ModuleList()
        for _ in range(num_layers):
            conv = HGTConv(hidden_channels, hidden_channels, data.metadata(),
                           num_heads, group='sum')
            self.convs.append(conv)

        self.lin = Linear(hidden_channels, out_channels)

    def forward(self, x_dict, edge_index_dict):
        for node_type, x in x_dict.items():
            x_dict[node_type] = self.lin_dict[node_type](x).relu_()
        for conv in self.convs:
            x_dict = conv(x_dict, edge_index_dict)
        return self.lin(x_dict['paper'])
```

## Training with HeteroData

### Full-batch

```python
def train():
    model.train()
    optimizer.zero_grad()
    out = model(data.x_dict, data.edge_index_dict)
    mask = data['paper'].train_mask
    loss = F.cross_entropy(out['paper'][mask], data['paper'].y[mask])
    loss.backward()
    optimizer.step()
    return float(loss)
```

### Mini-batch with NeighborLoader

```python
from torch_geometric.loader import NeighborLoader

train_loader = NeighborLoader(
    data,
    num_neighbors=[15] * 2,              # per hop (applies to all edge types)
    batch_size=128,
    input_nodes=('paper', data['paper'].train_mask),
)

# Fine-grained neighbor control per edge type:
# num_neighbors = {key: [15] * 2 for key in data.edge_types}

def train():
    model.train()
    total_examples = total_loss = 0
    for batch in train_loader:
        optimizer.zero_grad()
        batch = batch.to(device)
        batch_size = batch['paper'].batch_size
        out = model(batch.x_dict, batch.edge_index_dict)
        loss = F.cross_entropy(out['paper'][:batch_size],
                               batch['paper'].y[:batch_size])
        loss.backward()
        optimizer.step()
        total_examples += batch_size
        total_loss += float(loss) * batch_size
    return total_loss / total_examples
```

HGTLoader is also available for type-aware sampling:

```python
from torch_geometric.loader import HGTLoader

loader = HGTLoader(data, num_samples=[512] * 2, batch_size=128,
                   input_nodes=('paper', data['paper'].train_mask))
```

### `references/link_prediction.md`

# Link Prediction — Full Reference

Link prediction is the task of predicting missing or future edges in a graph. Common applications: social network friend suggestion, knowledge graph completion, drug-target interaction.

## Edge Splitting

Use `RandomLinkSplit` to split edges into train/val/test while maintaining graph structure:

```python
import torch_geometric.transforms as T

transform = T.RandomLinkSplit(
    num_val=0.1,              # 10% of edges for validation
    num_test=0.1,             # 10% of edges for test
    is_undirected=True,       # Set True for undirected graphs
    add_negative_train_samples=False,  # Generate negatives on-the-fly during training
    neg_sampling_ratio=1.0,   # 1 negative per positive edge
)
train_data, val_data, test_data = transform(data)
```

After splitting, each split contains:
- `edge_index`: message-passing edges (train edges only — no data leakage)
- `edge_label_index`: supervision edges `[2, num_supervision_edges]` — the edges to predict
- `edge_label`: binary labels — 1 for positive (real) edges, 0 for negative (fake) edges

For the training split with `add_negative_train_samples=False`, only positive edges are in `edge_label_index` and negatives are sampled during training. Val/test splits always include both positive and negative edges.

## Encoder-Decoder Pattern

The standard approach:
1. **Encode** — use a GNN to produce node embeddings from the message-passing edges
2. **Decode** — score candidate edges using the node embeddings

```python
import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv

class LinkEncoder(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels):
        super().__init__()
        self.conv1 = GCNConv(in_channels, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, out_channels)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index).relu()
        x = self.conv2(x, edge_index)
        return x

def decode(z, edge_label_index):
    """Dot-product decoder: score = z_src . z_dst for each edge."""
    src, dst = edge_label_index
    return (z[src] * z[dst]).sum(dim=1)
```

## Full-Batch Training Loop

```python
from torch_geometric.utils import negative_sampling

model = LinkEncoder(data.num_features, 128, 64)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

def train(train_data):
    model.train()
    optimizer.zero_grad()

    # Encode using message-passing edges only
    z = model(train_data.x, train_data.edge_index)

    # Sample negative edges for this batch
    neg_edge_index = negative_sampling(
        edge_index=train_data.edge_index,
        num_nodes=train_data.num_nodes,
        num_neg_samples=train_data.edge_label_index.size(1),
    )

    # Combine positive and negative supervision edges
    edge_label_index = torch.cat([train_data.edge_label_index, neg_edge_index], dim=1)
    edge_label = torch.cat([
        torch.ones(train_data.edge_label_index.size(1)),
        torch.zeros(neg_edge_index.size(1)),
    ])

    # Decode and compute loss
    pred = decode(z, edge_label_index)
    loss = F.binary_cross_entropy_with_logits(pred, edge_label)
    loss.backward()
    optimizer.step()
    return loss.item()

@torch.no_grad()
def test(data_split):
    model.train(False)  # Inference mode (disables dropout; not Python eval)
    z = model(data_split.x, data_split.edge_index)
    pred = decode(z, data_split.edge_label_index).sigmoid()
    # AUC is the standard metric for link prediction
    from sklearn.metrics import roc_auc_score
    return roc_auc_score(data_split.edge_label.cpu(), pred.cpu())
```

## Graph Autoencoders (GAE / VGAE)

PyG provides `GAE` and `VGAE` for unsupervised link prediction:

```python
from torch_geometric.nn import GAE, VGAE, GCNConv

class Encoder(torch.nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.conv1 = GCNConv(in_channels, 2 * out_channels)
        self.conv2 = GCNConv(2 * out_channels, out_channels)
        # For VGAE, also define conv_mu and conv_logstd

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index).relu()
        return self.conv2(x, edge_index)

# GAE wraps your encoder and provides train/test methods
model = GAE(Encoder(data.num_features, 64))
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

def train():
    model.train()
    optimizer.zero_grad()
    z = model.encode(train_data.x, train_data.edge_index)
    loss = model.recon_loss(z, train_data.edge_label_index)
    # For VGAE, add KL divergence:
    # loss = loss + (1 / data.num_nodes) * model.kl_loss()
    loss.backward()
    optimizer.step()
    return loss.item()

@torch.no_grad()
def test(data_split):
    model.train(False)  # Inference mode (disables dropout; not Python eval)
    z = model.encode(data_split.x, data_split.edge_index)
    return model.test(z, data_split.edge_label_index[0],  # positive edges
                         data_split.edge_label_index[1])   # negative edges
```

For VGAE, the encoder must return `mu` and `logstd` instead of a single embedding. Use the VGAE-specific encoder pattern:

```python
class VariationalEncoder(torch.nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.conv1 = GCNConv(in_channels, 2 * out_channels)
        self.conv_mu = GCNConv(2 * out_channels, out_channels)
        self.conv_logstd = GCNConv(2 * out_channels, out_channels)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index).relu()
        return self.conv_mu(x, edge_index), self.conv_logstd(x, edge_index)

model = VGAE(VariationalEncoder(data.num_features, 64))
```

## Mini-Batch Link Prediction with LinkNeighborLoader

For large graphs, use `LinkNeighborLoader` — it samples subgraphs around supervision edges:

```python
from torch_geometric.loader import LinkNeighborLoader

train_loader = LinkNeighborLoader(
    data=train_data,
    num_neighbors=[20, 10],         # Sample neighbors per hop
    edge_label_index=train_data.edge_label_index,
    edge_label=train_data.edge_label,
    batch_size=128,                  # Number of supervision edges per batch
    neg_sampling_ratio=1.0,          # 1 negative per positive
    shuffle=True,
)

for batch in train_loader:
    # batch.edge_label_index: supervision edges (pos + neg)
    # batch.edge_label: 1 for positive, 0 for negative
    # batch.edge_index: message-passing edges (from neighbor sampling)
    z = model(batch.x, batch.edge_index)
    pred = decode(z, batch.edge_label_index)
    loss = F.binary_cross_entropy_with_logits(pred, batch.edge_label)
```

## Heterogeneous Link Prediction

For heterogeneous graphs (e.g., user-item recommendation):

```python
transform = T.RandomLinkSplit(
    num_val=0.1,
    num_test=0.1,
    neg_sampling_ratio=1.0,
    add_negative_train_samples=False,
    edge_types=('user', 'rates', 'movie'),              # Which edge type to predict
    rev_edge_types=('movie', 'rev_rates', 'user'),       # Its reverse
)
train_data, val_data, test_data = transform(data)

# Supervision edges are in:
# train_data['user', 'rates', 'movie'].edge_label_index
# train_data['user', 'rates', 'movie'].edge_label
```

## Evaluation Metrics

- **AUC-ROC**: Standard metric — area under the ROC curve
- **Average Precision (AP)**: Area under the precision-recall curve
- **Hits@K**: Fraction of positive edges ranked in top K (used in knowledge graphs)
- **MRR**: Mean reciprocal rank of positive edges

```python
from sklearn.metrics import roc_auc_score, average_precision_score

auc = roc_auc_score(edge_label.cpu(), pred.cpu())
ap = average_precision_score(edge_label.cpu(), pred.cpu())
```

## Common Pitfalls

1. **Data leakage**: Never include val/test edges in the message-passing graph during training. `RandomLinkSplit` handles this correctly — `edge_index` in train_data only contains training edges.
2. **Negative sampling quality**: Using random negatives is standard but can be too easy. For harder negatives, sample from 2-hop neighbors.
3. **Undirected graphs**: Set `is_undirected=True` in `RandomLinkSplit` — otherwise it will treat each direction independently and leak information.
4. **Decoding**: Dot-product is simplest but not always best. Consider MLP decoders or DistMult for heterogeneous/knowledge graphs.

### `references/message_passing.md`

# Custom Message Passing Layers

Full reference for implementing custom GNN layers via the `MessagePassing` base class.

## MessagePassing API

```python
MessagePassing(aggr="add", flow="source_to_target", node_dim=-2)
```

- `aggr`: Aggregation scheme — `"add"`, `"mean"`, or `"max"`
- `flow`: Message direction — `"source_to_target"` (default) or `"target_to_source"`
- `node_dim`: Axis along which to propagate

### Methods to override

- `message(...)`: Constructs messages for each edge. Access source/target node features via `_j`/`_i` suffixes.
- `aggregate(inputs, index)`: Aggregates messages (usually handled by `aggr` parameter).
- `update(aggr_out, ...)`: Post-aggregation transform on each node.
- `propagate(edge_index, size=None, **kwargs)`: Orchestrates the full pipeline. Call this from `forward()`.

Any tensor passed to `propagate()` can be auto-indexed in `message()` by appending `_i` (target) or `_j` (source). E.g., passing `x=features` lets you use `x_i` and `x_j` in the message function.

For bipartite graphs, pass `size=(N, M)` to `propagate()` and provide features as tuples: `x=(x_src, x_dst)`.

## Example: GCN Layer from Scratch

```python
import torch
from torch.nn import Linear, Parameter
from torch_geometric.nn import MessagePassing
from torch_geometric.utils import add_self_loops, degree

class GCNConv(MessagePassing):
    def __init__(self, in_channels, out_channels):
        super().__init__(aggr='add')
        self.lin = Linear(in_channels, out_channels, bias=False)
        self.bias = Parameter(torch.empty(out_channels))
        self.reset_parameters()

    def reset_parameters(self):
        self.lin.reset_parameters()
        self.bias.data.zero_()

    def forward(self, x, edge_index):
        # 1. Add self-loops
        edge_index, _ = add_self_loops(edge_index, num_nodes=x.size(0))
        # 2. Linear transform
        x = self.lin(x)
        # 3. Compute normalization coefficients
        row, col = edge_index
        deg = degree(col, x.size(0), dtype=x.dtype)
        deg_inv_sqrt = deg.pow(-0.5)
        deg_inv_sqrt[deg_inv_sqrt == float('inf')] = 0
        norm = deg_inv_sqrt[row] * deg_inv_sqrt[col]
        # 4-5. Message passing
        out = self.propagate(edge_index, x=x, norm=norm)
        # 6. Add bias
        return out + self.bias

    def message(self, x_j, norm):
        # x_j: source node features for each edge [num_edges, out_channels]
        # norm: normalization coefficients [num_edges]
        return norm.view(-1, 1) * x_j
```

## Example: EdgeConv Layer

```python
import torch
from torch.nn import Sequential as Seq, Linear, ReLU
from torch_geometric.nn import MessagePassing

class EdgeConv(MessagePassing):
    def __init__(self, in_channels, out_channels):
        super().__init__(aggr='max')
        self.mlp = Seq(
            Linear(2 * in_channels, out_channels),
            ReLU(),
            Linear(out_channels, out_channels),
        )

    def forward(self, x, edge_index):
        return self.propagate(edge_index, x=x)

    def message(self, x_i, x_j):
        # x_i: target node features [num_edges, in_channels]
        # x_j: source node features [num_edges, in_channels]
        return self.mlp(torch.cat([x_i, x_j - x_i], dim=1))
```

## Example: Dynamic EdgeConv (recomputes graph each layer)

```python
from torch_geometric.nn import knn_graph

class DynamicEdgeConv(EdgeConv):
    def __init__(self, in_channels, out_channels, k=6):
        super().__init__(in_channels, out_channels)
        self.k = k

    def forward(self, x, batch=None):
        edge_index = knn_graph(x, self.k, batch, loop=False, flow=self.flow)
        return super().forward(x, edge_index)
```

## Utility Functions

```python
from torch_geometric.utils import (
    add_self_loops,      # Add self-loop edges
    remove_self_loops,   # Remove self-loop edges
    degree,              # Compute node degrees
    softmax,             # Sparse softmax over neighborhoods
    to_dense_adj,        # Convert edge_index to dense adjacency matrix
    to_undirected,       # Make edge_index undirected
    contains_self_loops, # Check for self-loops
    is_undirected,       # Check if graph is undirected
    scatter,             # Scatter operations (sum, mean, max)
)
```

### `references/scaling.md`

# Scaling GNNs — Full Reference

Techniques for training GNNs on large graphs that don't fit in GPU memory, multi-GPU training, and performance optimization.

## Table of Contents
1. Neighbor Sampling (NeighborLoader)
2. Other Sampling Strategies
3. Multi-GPU / Distributed Training
4. torch.compile Support
5. Performance Tips

---

## 1. Neighbor Sampling (NeighborLoader)

The primary approach for large single-graph training. Recursively samples a fixed number of neighbors per hop, bounding the computation graph.

```python
from torch_geometric.loader import NeighborLoader

loader = NeighborLoader(
    data,
    num_neighbors=[15, 10],       # Max neighbors per hop (hop 1: 15, hop 2: 10)
    batch_size=1024,               # Number of seed nodes per batch
    input_nodes=data.train_mask,   # Which nodes to sample from
    shuffle=True,
    num_workers=4,                 # Parallel data loading
    replace=False,                 # Sample without replacement
)
```

**Key parameters:**
- `num_neighbors`: List of max neighbors per hop. Length should match GNN depth. Use `-1` to sample all neighbors for a hop.
- `input_nodes`: Seed nodes — can be a mask, tensor of indices, or `('node_type', mask)` tuple for hetero graphs.
- `subgraph_type`: `"directional"` (default), `"bidirectional"` (add reverse edges), or `"induced"` (full induced subgraph).
- `disjoint`: If `True`, don't fuse neighborhoods across seed nodes (uses more memory but can be needed).

**Training pattern:**
```python
model = GraphSAGE(in_channels, hidden_channels, out_channels, num_layers=2)

for batch in loader:
    batch = batch.to(device)
    out = model(batch.x, batch.edge_index)
    # CRITICAL: only first batch_size nodes are seed nodes
    loss = F.cross_entropy(out[:batch.batch_size], batch.y[:batch.batch_size])
```

**Important details:**
- Nodes are sorted: first `batch.batch_size` nodes are the seed nodes
- `batch.n_id` maps local indices back to original node IDs
- Sampling >2-3 hops is generally infeasible (exponential neighborhood growth)
- Keep `len(num_neighbors) == num_gnn_layers` for efficiency
- PyG 2.7 adds `BidirectionalSampler` and forward+reverse edge sampling on `NeighborSampler` for undirected graphs

### LinkNeighborLoader (for link prediction)

Samples subgraphs around supervision edges:

```python
from torch_geometric.loader import LinkNeighborLoader

loader = LinkNeighborLoader(
    data,
    num_neighbors=[20, 10],
    edge_label_index=train_data.edge_label_index,
    edge_label=train_data.edge_label,
    batch_size=256,
    neg_sampling_ratio=1.0,
    shuffle=True,
)
```

### HGTLoader (type-aware heterogeneous sampling)

Samples a fixed number of nodes per type per hop, following HGT paper:

```python
from torch_geometric.loader import HGTLoader

loader = HGTLoader(
    data,
    num_samples=[512] * 2,        # Nodes per type per hop
    batch_size=128,
    input_nodes=('paper', data['paper'].train_mask),
)
```

## 2. Other Sampling Strategies

### ClusterLoader (ClusterGCN)

Partitions the graph into clusters, trains on full subgraphs. Better for deeper GNNs since messages flow freely within clusters:

```python
from torch_geometric.loader import ClusterData, ClusterLoader

cluster_data = ClusterData(data, num_parts=1500)
loader = ClusterLoader(cluster_data, batch_size=20, shuffle=True)

for batch in loader:
    # batch is a full subgraph — no slicing needed
    out = model(batch.x, batch.edge_index)
    loss = F.cross_entropy(out[batch.train_mask], batch.y[batch.train_mask])
```

### GraphSAINTSampler

Samples subgraphs via random walks, nodes, or edges with importance-based normalization:

```python
from torch_geometric.loader import GraphSAINTRandomWalkSampler

loader = GraphSAINTRandomWalkSampler(
    data, batch_size=6000, walk_length=2, num_steps=5,
)
```

### ShaDowKHopSampler

Extracts K-hop induced subgraphs around seed nodes — decouples depth from scope:

```python
from torch_geometric.loader import ShaDowKHopSampler

loader = ShaDowKHopSampler(
    data, depth=2, num_neighbors=5, batch_size=64,
    input_nodes=data.train_mask,
)
```

## 3. Multi-GPU / Distributed Training

`torch_geometric.distributed` is deprecated as of PyG 2.7 — use standard PyTorch DDP below.

### DistributedDataParallel (DDP)

Standard PyTorch DDP works with PyG. Each GPU gets a partition of the seed nodes:

```python
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel
import torch.multiprocessing as mp

def run(rank, world_size, dataset):
    # Initialize process group
    os.environ['MASTER_ADDR'] = 'localhost'
    os.environ['MASTER_PORT'] = '12345'
    dist.init_process_group('nccl', rank=rank, world_size=world_size)

    data = dataset[0]

    # Split training nodes across GPUs
    train_idx = data.train_mask.nonzero().view(-1)
    train_idx = train_idx.split(train_idx.size(0) // world_size)[rank]

    loader = NeighborLoader(
        data,
        input_nodes=train_idx,
        num_neighbors=[25, 10],
        batch_size=1024,
        num_workers=4,
        shuffle=True,
    )

    # Wrap model in DDP
    model = GraphSAGE(...).to(rank)
    model = DistributedDataParallel(model, device_ids=[rank])
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    for epoch in range(10):
        model.train()
        for batch in loader:
            batch = batch.to(rank)
            optimizer.zero_grad()
            out = model(batch.x, batch.edge_index)[:batch.batch_size]
            loss = F.cross_entropy(out, batch.y[:batch.batch_size])
            loss.backward()
            optimizer.step()

        # Synchronize before evaluation
        dist.barrier()

        if rank == 0:
            # Evaluate on rank 0 only
            ...

    dist.destroy_process_group()

# Launch
if __name__ == '__main__':
    dataset = Reddit('./data/Reddit')
    world_size = torch.cuda.device_count()
    mp.spawn(run, args=(world_size, dataset), nprocs=world_size, join=True)
```

**Key points:**
- Initialize dataset before `mp.spawn()` — data auto-moves to shared memory
- Each rank creates its own NeighborLoader with a subset of seed nodes
- Call `dist.barrier()` to synchronize before evaluation
- Evaluate on rank 0 only for simplicity
- Clean up with `dist.destroy_process_group()`

### PyTorch Lightning Integration

PyG provides Lightning wrappers for minimal boilerplate. PyG 2.7 supports the `lightning` package (not only legacy `pytorch-lightning`):

```python
import lightning as L
from torch_geometric.data import LightningNodeData

datamodule = LightningNodeData(
    data,
    input_train_nodes=data.train_mask,
    input_val_nodes=data.val_mask,
    input_test_nodes=data.test_mask,
    loader='neighbor',
    num_neighbors=[25, 10],
    batch_size=1024,
)

# Use with any Lightning Trainer
trainer = L.Trainer(devices=4, accelerator='gpu', strategy='ddp')
trainer.fit(model, datamodule)
```

Also available: `LightningLinkData` for link prediction, `LightningDataset` for graph-level tasks.

## 4. torch.compile Support

PyG supports `torch.compile` for faster execution:

```python
model = GCN(...)
model = torch.compile(model)

# Works with standard training loops
out = model(data.x, data.edge_index)
```

**What works:**
- Most GNN layers (GCNConv, SAGEConv, GATConv, etc.)
- Standard training/inference pipelines
- Both CPU and CUDA backends

**Limitations:**
- Dynamic shapes (varying graph sizes per batch) may trigger recompilation
- Some specialized layers or custom MessagePassing subclasses may not compile
- Use `torch.compile(model, dynamic=True)` if batch graph sizes vary significantly

## 5. Performance Tips

- **num_workers**: Set `num_workers=4` (or more) in data loaders for CPU-side parallelism
- **pin_memory**: Use `pin_memory=True` in loaders for faster CPU-to-GPU transfer
- **Sparse tensors**: Use `SparseTensor` from `torch_sparse` instead of `edge_index` for faster message passing on some layers
- **Profiling**: Use `torch_geometric.profile` to measure time and memory of individual layers
- **Mixed precision**: Standard PyTorch AMP works with PyG:
  ```python
  from torch.amp import autocast, GradScaler
  scaler = GradScaler()
  with autocast('cuda'):
      out = model(batch.x, batch.edge_index)
      loss = F.cross_entropy(out[:batch.batch_size], batch.y[:batch.batch_size])
  scaler.scale(loss).backward()
  scaler.step(optimizer)
  scaler.update()
  ```
- **Reduce sampling**: Fewer neighbors per hop = faster but noisier. Start with `[15, 10]` for 2-layer GNNs.
- **Avoid unnecessary computation**: With NeighborLoader, only the first `batch_size` outputs matter — don't compute metrics on sampled-only nodes.
