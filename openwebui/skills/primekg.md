---
name: primekg
description: Query the Precision Medicine Knowledge Graph (PrimeKG) for multiscale biological data including genes, drugs, diseases, phenotypes, and more.
---

# PrimeKG Knowledge Graph Skill

## Overview

PrimeKG is a precision medicine knowledge graph that integrates over 20 primary databases and high-quality scientific literature into a single resource. It contains over 100,000 nodes and 4 million edges across 29 relationship types, including drug-target, disease-gene, and phenotype-disease associations.

**Key capabilities:**
- Search for nodes (genes, proteins, drugs, diseases, phenotypes)
- Retrieve direct neighbors (associated entities and clinical evidence)
- Analyze local disease context (related genes, drugs, phenotypes)
- Identify drug-disease paths (potential repurposing opportunities)

**Data access:** Programmatic access via `query_primekg.py`. Data is stored at `C:\Users\eamon\Documents\Data\PrimeKG\kg.csv`.

## When to Use This Skill

This skill should be used when:

- **Knowledge-based drug discovery:** Identifying targets and mechanisms for diseases.
- **Drug repurposing:** Finding existing drugs that might have evidence for new indications.
- **Phenotype analysis:** Understanding how symptoms/phenotypes relate to diseases and genes.
- **Multiscale biology:** Bridging the gap between molecular targets (genes) and clinical outcomes (diseases).
- **Network pharmacology:** Investigating the broader network effects of drug-target interactions.

## Core Workflow

### 1. Search for Entities

Find identifiers for genes, drugs, or diseases.

```python
from scripts.query_primekg import search_nodes

# Search for Alzheimer's disease nodes
results = search_nodes("Alzheimer", node_type="disease")
# Returns: [{"id": "EFO_0000249", "type": "disease", "name": "Alzheimer's disease", ...}]
```

### 2. Get Neighbors (Direct Associations)

Retrieve all connected nodes and relationship types.

```python
from scripts.query_primekg import get_neighbors

# Get all neighbors of a specific disease ID
neighbors = get_neighbors("EFO_0000249")
# Returns: List of neighbors like {"neighbor_name": "APOE", "relation": "disease_gene", ...}
```

### 3. Analyze Disease Context

A high-level function to summarize associations for a disease.

```python
from scripts.query_primekg import get_disease_context

# Comprehensive summary for a disease
context = get_disease_context("Alzheimer's disease")
# Access: context['associated_genes'], context['associated_drugs'], context['phenotypes']
```

## Relationship Types in PrimeKG

The graph contains several key relationship types including:
- `protein_protein`: Physical PPIs
- `drug_protein`: Drug target/mechanism associations
- `disease_gene`: Genetic associations
- `drug_disease`: Indications and contraindications
- `disease_phenotype`: Clinical signs and symptoms
- `gwas`: Genome-wide association studies evidence

## Best Practices

1. **Use specific IDs:** When using `get_neighbors`, ensure you have the correct ID from `search_nodes`.
2. **Context first:** Use `get_disease_context` for a broad overview before diving into specific genes or drugs.
3. **Filter relationships:** Use the `relation_type` filter in `get_neighbors` to focus on specific evidence (e.g., only `drug_protein`).
4. **Multiscale integration:** Combine with `OpenTargets` for deeper genetic evidence or `Semantic Scholar` for the latest literature context.

## Resources

### Scripts
- `scripts/query_primekg.py`: Core functions for searching and querying the knowledge graph.

### Data Path
- Data: `kg.csv`, downloaded from the [PrimeKG Harvard Dataverse](https://dataverse.harvard.edu/dataverse/primekg).
- Point the scripts at it with `export PRIMEKG_DATA=/path/to/kg.csv` (default: `data/PrimeKG/kg.csv`).
- Total nodes: ~129,000
- Total edges: ~4,000,000
- Database: CSV-based, optimized for pandas querying.

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/primekg/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `scripts/query_primekg.py`

```python
import pandas as pd
import os
import json
from typing import List, Dict, Optional, Union

# Where kg.csv lives. Override with the PRIMEKG_DATA environment variable, or
# by assigning to DATA_PATH before calling any query function.
DATA_PATH = os.environ.get("PRIMEKG_DATA", "data/PrimeKG/kg.csv")

def _load_kg():
    """Internal helper to load the KG efficiently."""
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"PrimeKG data not found at {DATA_PATH}. Download kg.csv from "
            "https://dataverse.harvard.edu/dataverse/primekg and set "
            "PRIMEKG_DATA to its path."
        )
    # For very large files, we might want to use a database or specialized graph library.
    # For now, we'll use pandas for simplicity but with low_memory=True.
    return pd.read_csv(DATA_PATH, low_memory=True)

def search_nodes(name_query: str, node_type: Optional[str] = None) -> List[Dict]:
    """
    Search for nodes in PrimeKG by name and optionally type.
    
    Args:
        name_query: String to search for in node names.
        node_type: Optional type of node (e.g., 'gene/protein', 'drug', 'disease').
        
    Returns:
        List of matching nodes with their metadata.
    """
    kg = _load_kg()
    
    # Check both x and y columns for unique nodes
    x_nodes = kg[['x_id', 'x_type', 'x_name', 'x_source']].drop_duplicates()
    x_nodes.columns = ['id', 'type', 'name', 'source']
    
    y_nodes = kg[['y_id', 'y_type', 'y_name', 'y_source']].drop_duplicates()
    y_nodes.columns = ['id', 'type', 'name', 'source']
    
    nodes = pd.concat([x_nodes, y_nodes]).drop_duplicates()
    
    mask = nodes['name'].str.contains(name_query, case=False, na=False)
    if node_type:
        mask &= (nodes['type'] == node_type)
        
    results = nodes[mask].head(20).to_dict(orient='records')
    return results

def get_neighbors(node_id: Union[str, int], relation_type: Optional[str] = None) -> List[Dict]:
    """
    Get all direct neighbors of a specific node.
    
    Args:
        node_id: The ID of the node (e.g., NCBI Gene ID or ChEMBL ID).
        relation_type: Optional filter for specific relationship types.
        
    Returns:
        List of neighbors and the relationship metadata.
    """
    kg = _load_kg()
    node_id = str(node_id)
    
    mask_x = (kg['x_id'].astype(str) == node_id)
    mask_y = (kg['y_id'].astype(str) == node_id)
    
    if relation_type:
        mask_x &= (kg['relation'] == relation_type)
        mask_y &= (kg['relation'] == relation_type)
        
    neighbors_x = kg[mask_x][['relation', 'display_relation', 'y_id', 'y_type', 'y_name', 'y_source']]
    neighbors_x.columns = ['relation', 'display_relation', 'neighbor_id', 'neighbor_type', 'neighbor_name', 'neighbor_source']
    
    neighbors_y = kg[mask_y][['relation', 'display_relation', 'x_id', 'x_type', 'x_name', 'x_source']]
    neighbors_y.columns = ['relation', 'display_relation', 'neighbor_id', 'neighbor_type', 'neighbor_name', 'neighbor_source']
    
    results = pd.concat([neighbors_x, neighbors_y]).to_dict(orient='records')
    return results

def find_paths(start_node_id: str, end_node_id: str, max_depth: int = 2) -> List[List[Dict]]:
    """
    Find paths between two nodes (e.g., Drug to Disease) up to a certain depth.
    Note: Simple BFS implementation.
    """
    kg = _load_kg()
    start_node_id = str(start_node_id)
    end_node_id = str(end_node_id)
    
    # Simplified path finding for depth 1 and 2
    # Depth 1
    direct = kg[((kg['x_id'].astype(str) == start_node_id) & (kg['y_id'].astype(str) == end_node_id)) |
                ((kg['y_id'].astype(str) == start_node_id) & (kg['x_id'].astype(str) == end_node_id))]
    
    paths = []
    for _, row in direct.iterrows():
        paths.append([row.to_dict()])
        
    if max_depth >= 2:
        # Find neighbors of start
        n1_x = kg[kg['x_id'].astype(str) == start_node_id]
        n1_y = kg[kg['y_id'].astype(str) == start_node_id]
        
        # This is computationally expensive in pure pandas for a large KG.
        # Implementation skipped for brevity in this MVP, but suggested for full version.
        pass
        
    return paths

def get_disease_context(disease_name: str) -> Dict:
    """
    Analyze the local graph around a disease: associated genes, drugs, and phenotypes.
    """
    results = search_nodes(disease_name, node_type='disease')
    if not results:
        return {"error": "Disease not found"}
    
    disease_id = results[0]['id']
    neighbors = get_neighbors(disease_id)
    
    summary = {
        "disease_info": results[0],
        "associated_genes": [n for n in neighbors if n['neighbor_type'] == 'gene/protein'],
        "associated_drugs": [n for n in neighbors if n['neighbor_type'] == 'drug'],
        "phenotypes": [n for n in neighbors if n['neighbor_type'] == 'phenotype'],
        "related_diseases": [n for n in neighbors if n['neighbor_type'] == 'disease']
    }
    return summary
```
