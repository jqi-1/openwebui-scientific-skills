---
name: pyzotero
description: Zotero library type: ''user'' or ''group'' (default ''user'').
---

# Pyzotero

Pyzotero is a Python wrapper for the [Zotero API v3](https://www.zotero.org/support/dev/web_api/v3/start). Use it to programmatically manage Zotero libraries: read items and collections, create and update references, upload attachments, manage tags, and export citations.

**Current upstream:** pyzotero 1.13.0 (PyPI, May 2026). Docs: [pyzotero.readthedocs.io](https://pyzotero.readthedocs.io/en/latest/).

## Authentication Setup

**Required credentials** — get from https://www.zotero.org/settings/keys:
- **User ID**: shown as "Your userID for use in API calls"
- **API Key**: create at https://www.zotero.org/settings/keys/new
- **Library ID**: for group libraries, the integer after `/groups/` in the group URL

Store credentials in environment variables or a `.env` file:
```
ZOTERO_LIBRARY_ID=your_user_id
ZOTERO_API_KEY=your_api_key
ZOTERO_LIBRARY_TYPE=user  # or "group"
```

See [references/authentication.md](references/authentication.md) for full setup details.

## Installation

```bash
uv add pyzotero              # Web API client
uv add "pyzotero[cli]"       # + local CLI (Zotero 7)
uv add "pyzotero[mcp]"       # + MCP server for LLM clients (Zotero 7)
```

## Quick Start

```python
import os
from pyzotero import Zotero

zot = Zotero(
    library_id=os.environ['ZOTERO_LIBRARY_ID'],
    library_type=os.environ.get('ZOTERO_LIBRARY_TYPE', 'user'),
    api_key=os.environ['ZOTERO_API_KEY'],
)

# Retrieve top-level items (returns 100 by default)
items = zot.top(limit=10)
for item in items:
    print(item['data']['title'], item['data']['itemType'])

# Search by keyword
results = zot.items(q='machine learning', limit=20)

# Retrieve all items (use everything() for complete results)
all_items = zot.everything(zot.items())
```

## Core Concepts

- A `Zotero` instance is bound to a single library (user or group). All methods operate on that library.
- Item data lives in `item['data']`. Access fields like `item['data']['title']`, `item['data']['creators']`.
- Pyzotero returns 100 items by default (API default is 25). Use `zot.everything(zot.items())` to get all items.
- Write methods return `True` on success or raise a `ZoteroError`.

## Reference Files

| File | Contents |
|------|----------|
| [references/authentication.md](references/authentication.md) | Credentials, library types, local mode |
| [references/read-api.md](references/read-api.md) | Retrieving items, collections, tags, groups |
| [references/search-params.md](references/search-params.md) | Filtering, sorting, search parameters |
| [references/write-api.md](references/write-api.md) | Creating, updating, deleting items |
| [references/collections.md](references/collections.md) | Collection CRUD operations |
| [references/tags.md](references/tags.md) | Tag access and management |
| [references/files-attachments.md](references/files-attachments.md) | File download and attachment uploads |
| [references/exports.md](references/exports.md) | BibTeX, CSL-JSON, bibliography export |
| [references/pagination.md](references/pagination.md) | follow(), everything(), generators |
| [references/full-text.md](references/full-text.md) | Full-text content indexing and access |
| [references/saved-searches.md](references/saved-searches.md) | Saved search management |
| [references/cli.md](references/cli.md) | Command-line interface (local Zotero 7) |
| [references/mcp.md](references/mcp.md) | MCP server for LLM clients (local Zotero 7) |
| [references/error-handling.md](references/error-handling.md) | Errors and exception handling |

## Common Patterns

### Fetch and modify an item
```python
item = zot.item('ITEMKEY')
item['data']['title'] = 'New Title'
zot.update_item(item)
```

### Create an item from a template
```python
template = zot.item_template('journalArticle')
template['title'] = 'My Paper'
template['creators'][0] = {'creatorType': 'author', 'firstName': 'Jane', 'lastName': 'Doe'}
zot.create_items([template])
```

### Export as BibTeX
```python
zot.add_parameters(format='bibtex')
bibtex = zot.top(limit=50)
# bibtex is a bibtexparser BibDatabase object
print(bibtex.entries)
```

### Local mode (read-only, no API key needed)
```python
zot = Zotero(library_id='123456', library_type='user', local=True)
items = zot.items()
```

### Local Zotero 7 (CLI or MCP, no API key)

For searching a locally running Zotero desktop app (including full-text PDF search), use the CLI or MCP server instead of the Web API. Both require Zotero 7 with local API access enabled. See [references/cli.md](references/cli.md) and [references/mcp.md](references/mcp.md).

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/pyzotero/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/authentication.md`

# Authentication & Setup

> **Security:** Never hardcode API keys in source code or commit them to version control. Use environment variables or a `.env` file scoped to `ZOTERO_*` keys only. Placeholder values like `ABC1234XYZ` below are illustrative — substitute your real credentials from env vars.

## Credentials

Obtain from https://www.zotero.org/settings/keys (or create a key at https://www.zotero.org/settings/keys/new):

| Credential | Where to Find |
|-----------|---------------|
| **User ID** | "Your userID for use in API calls" section |
| **API Key** | Create new key at /settings/keys/new, or via Settings → Security → Applications → "Create new key" at https://www.zotero.org/settings/security |
| **Group Library ID** | Integer after `/groups/` in group URL (e.g. `https://www.zotero.org/groups/169947`) |

## Environment Variables (recommended)

Store in `.env` or export in shell:

```
ZOTERO_LIBRARY_ID=436
ZOTERO_API_KEY=your_api_key_here
ZOTERO_LIBRARY_TYPE=user
```

Load in Python:

```python
import os
from dotenv import load_dotenv
from pyzotero import Zotero

load_dotenv()

zot = Zotero(
    library_id=os.environ['ZOTERO_LIBRARY_ID'],
    library_type=os.environ.get('ZOTERO_LIBRARY_TYPE', 'user'),
    api_key=os.environ['ZOTERO_API_KEY'],
)
```

## Library Types

```python
import os

# Personal library
zot = Zotero(
    os.environ['ZOTERO_LIBRARY_ID'],
    'user',
    os.environ['ZOTERO_API_KEY'],
)

# Group library — use the group ID as library_id
zot = Zotero('169947', 'group', os.environ['ZOTERO_API_KEY'])
```

**Important**: A `Zotero` instance is bound to a single library. To access multiple libraries, create multiple instances.

## Local Mode (Read-Only)

Connect to your local Zotero installation without an API key. Only supports read requests.

```python
zot = Zotero(library_id='436', library_type='user', local=True)
items = zot.items(limit=10)  # reads from local Zotero
```

For Zotero 7, enable local API access: Settings → Advanced → "Allow other applications on this computer to communicate with Zotero". See [cli.md](cli.md) and [mcp.md](mcp.md) for richer local access.

## Optional Parameters

```python
zot = Zotero(
    library_id=os.environ['ZOTERO_LIBRARY_ID'],
    library_type='user',
    api_key=os.environ['ZOTERO_API_KEY'],
    preserve_json_order=True,   # use OrderedDict for JSON responses
    locale='en-US',             # localise field names (e.g. 'fr-FR' for French)
)
```

## Key Permissions

Check what the current API key can access:

```python
info = zot.key_info()
# Returns dict with user info and group access permissions
```

Check accessible groups:

```python
groups = zot.groups()
# Returns list of group libraries accessible to the current key
```

## API Key Scopes

When creating an API key at https://www.zotero.org/settings/keys/new, choose appropriate permissions:

- **Read Only**: For retrieving items and collections
- **Write Access**: For creating, updating, and deleting items
- **Notes Access**: To include notes in read/write operations
- **Files Access**: Required for uploading attachments

### `references/cli.md`

# Command-Line Interface

The pyzotero CLI connects to your **local Zotero 7 installation** (not the remote Web API). It requires a running Zotero desktop app with local API access enabled:

**Zotero → Settings → Advanced → Allow other applications on this computer to communicate with Zotero**

## Installation

```bash
uv add "pyzotero[cli]"
# or run without installing:
uvx --from "pyzotero[cli]" pyzotero search -q "your query"
```

## Searching

```bash
# Search titles and metadata
pyzotero search -q "machine learning"

# Full-text search (includes PDF content)
pyzotero search -q "climate change" --fulltext

# Filter by item type
pyzotero search -q "methodology" --itemtype journalArticle --itemtype book

# Filter by tags (AND logic)
pyzotero search -q "evolution" --tag "reviewed" --tag "high-priority"

# Search within a collection
pyzotero search --collection ABC123 -q "test"

# Paginate results
pyzotero search -q "deep learning" --limit 20 --offset 40

# Output as JSON (for machine processing)
pyzotero search -q "protein" --json
```

## Getting Individual Items

```bash
# Get a single item by key
pyzotero item ABC123

# Get as JSON
pyzotero item ABC123 --json

# Get child items (attachments, notes)
pyzotero children ABC123 --json

# Get multiple items at once (up to 50)
pyzotero subset ABC123 DEF456 GHI789 --json
```

## Collections & Tags

```bash
# List all collections
pyzotero listcollections

# List all tags
pyzotero tags

# Tags in a specific collection
pyzotero tags --collection ABC123
```

## Full-Text Content

```bash
# Get full-text content of an attachment
pyzotero fulltext ABC123
```

## Item Types

```bash
# List all available item types
pyzotero itemtypes
```

## DOI Index

```bash
# Get complete DOI-to-key mapping (useful for caching)
pyzotero doiindex > doi_cache.json
# Returns JSON: {"10.1038/s41592-024-02233-6": {"key": "ABC123", "doi": "..."}}
```

## Output Format

By default the CLI outputs human-readable text including title, authors, date, publication, volume, issue, DOI, URL, and PDF attachment paths.

Use `--json` for structured JSON output suitable for piping to other tools.

## Search Behaviour Notes

- Default search covers top-level item titles and metadata fields only
- `--fulltext` expands search to PDF content; results show parent bibliographic items (not raw attachments)
- Multiple `--tag` flags use AND logic
- Multiple `--itemtype` flags use OR logic

### `references/collections.md`

# Collection Management

## Reading Collections

```python
# All collections (flat list including nested)
all_cols = zot.collections()

# Only top-level collections
top_cols = zot.collections_top()

# Specific collection
col = zot.collection('COLKEY')

# Sub-collections of a collection
sub_cols = zot.collections_sub('COLKEY')

# All collections under a given collection (recursive)
tree = zot.all_collections('COLKEY')
# Or all collections in the library:
tree = zot.all_collections()
```

## Collection Data Structure

```python
col = zot.collection('5TSDXJG6')
name = col['data']['name']
key = col['data']['key']
parent = col['data']['parentCollection']  # False if top-level, else parent key
version = col['data']['version']
n_items = col['meta']['numItems']
n_sub_collections = col['meta']['numCollections']
```

## Creating Collections

```python
# Create a top-level collection
zot.create_collections([{'name': 'My New Collection'}])

# Create a nested collection
zot.create_collections([{
    'name': 'Sub-Collection',
    'parentCollection': 'PARENTCOLKEY'
}])

# Create multiple at once
zot.create_collections([
    {'name': 'Collection A'},
    {'name': 'Collection B'},
    {'name': 'Sub-B', 'parentCollection': 'BKEY'},
])
```

## Updating Collections

```python
cols = zot.collections()
# Rename the first collection
cols[0]['data']['name'] = 'Renamed Collection'
zot.update_collection(cols[0])

# Update multiple collections (auto-chunked at 50)
zot.update_collections(cols)
```

## Deleting Collections

```python
# Delete a single collection
col = zot.collection('COLKEY')
zot.delete_collection(col)

# Delete multiple collections
cols = zot.collections()
zot.delete_collection(cols)  # pass a list of dicts
```

## Managing Items in Collections

```python
# Add an item to a collection
item = zot.item('ITEMKEY')
zot.addto_collection('COLKEY', item)

# Remove an item from a collection
zot.deletefrom_collection('COLKEY', item)

# Get all items in a collection
items = zot.collection_items('COLKEY')

# Get only top-level items in a collection
top_items = zot.collection_items_top('COLKEY')

# Count items in a collection
n = zot.num_collectionitems('COLKEY')

# Get tags in a collection
tags = zot.collection_tags('COLKEY')
```

## Find Collection Key by Name

```python
def find_collection(zot, name):
    for col in zot.everything(zot.collections()):
        if col['data']['name'] == name:
            return col['data']['key']
    return None

key = find_collection(zot, 'Machine Learning Papers')
```

### `references/error-handling.md`

# Error Handling

## Exception Types

Pyzotero raises `ZoteroError` subclasses for API errors. Import from `pyzotero.zotero_errors`:

```python
from pyzotero import zotero_errors
```

Common exceptions:

| Exception | Cause |
|-----------|-------|
| `UserNotAuthorised` | Invalid or missing API key |
| `HTTPError` | Generic HTTP error |
| `ParamNotPassed` | Required parameter missing |
| `CallDoesNotExist` | Invalid API method for library type |
| `ResourceNotFound` | Item/collection key not found |
| `Conflict` | Version conflict (optimistic locking) |
| `PreConditionFailed` | `If-Unmodified-Since-Version` check failed |
| `TooManyItems` | Batch exceeds 50-item limit |
| `TooManyRequests` | API rate limit exceeded |
| `InvalidItemFields` | Item dict contains unknown fields |

## Basic Error Handling

```python
from pyzotero import Zotero
from pyzotero import zotero_errors
import os

zot = Zotero(
    os.environ['ZOTERO_LIBRARY_ID'],
    os.environ.get('ZOTERO_LIBRARY_TYPE', 'user'),
    os.environ['ZOTERO_API_KEY'],
)

try:
    item = zot.item('BADKEY')
except zotero_errors.ResourceNotFound:
    print('Item not found')
except zotero_errors.UserNotAuthorised:
    print('Invalid API key')
except Exception as e:
    print(f'Unexpected error: {e}')
    if hasattr(e, '__cause__'):
        print(f'Caused by: {e.__cause__}')
```

## Version Conflict Handling

```python
try:
    zot.update_item(item)
except zotero_errors.PreConditionFailed:
    # Item was modified since you retrieved it — re-fetch and retry
    fresh_item = zot.item(item['data']['key'])
    fresh_item['data']['title'] = new_title
    zot.update_item(fresh_item)
```

## Checking for Invalid Fields

```python
from pyzotero import zotero_errors

template = zot.item_template('journalArticle')
template['badField'] = 'bad value'

try:
    zot.check_items([template])
except zotero_errors.InvalidItemFields as e:
    print(f'Invalid fields: {e}')
    # Fix fields before calling create_items
```

## Rate Limiting

The Zotero API rate-limits requests. If you receive `TooManyRequests`:

```python
import time
from pyzotero import zotero_errors

def safe_request(func, *args, **kwargs):
    retries = 3
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except zotero_errors.TooManyRequests:
            wait = 2 ** attempt
            print(f'Rate limited, waiting {wait}s...')
            time.sleep(wait)
    raise RuntimeError('Max retries exceeded')

items = safe_request(zot.items, limit=100)
```

## Accessing Underlying Error

```python
try:
    zot.item('BADKEY')
except Exception as e:
    print(e.__cause__)    # original HTTP error
    print(e.__context__)  # exception context
```

### `references/exports.md`

# Export Formats

## BibTeX

```python
zot.add_parameters(format='bibtex')
bibtex_db = zot.top(limit=50)
# Returns a bibtexparser BibDatabase object

# Access entries as list of dicts
entries = bibtex_db.entries
for entry in entries:
    print(entry.get('title'), entry.get('author'))

# Write to .bib file
import bibtexparser
with open('library.bib', 'w') as f:
    bibtexparser.dump(bibtex_db, f)
```

## CSL-JSON

```python
zot.add_parameters(content='csljson', limit=50)
csl_items = zot.items()
# Returns a list of dicts in CSL-JSON format
```

## Bibliography HTML (formatted citations)

```python
# APA style bibliography
zot.add_parameters(content='bib', style='apa')
bib_entries = zot.items(limit=50)
# Returns list of HTML <div> strings

for entry in bib_entries:
    print(entry)  # e.g. '<div>Smith, J. (2024). Title. <i>Journal</i>...</div>'
```

**Note**: `format='bib'` removes the `limit` parameter. The API enforces a max of 150 items.

### Available Citation Styles

Pass any valid CSL style name from the [Zotero style repository](https://www.zotero.org/styles):
- `'apa'`
- `'chicago-author-date'`
- `'chicago-note-bibliography'`
- `'mla'`
- `'vancouver'`
- `'ieee'`
- `'harvard-cite-them-right'`
- `'nature'`

## In-Text Citations

```python
zot.add_parameters(content='citation', style='apa')
citations = zot.items(limit=50)
# Returns list of HTML <span> elements: ['<span>(Smith, 2024)</span>', ...]
```

## Other Formats

Set `content` to any Zotero export format:

| Format | `content` value | Returns |
|--------|----------------|---------|
| BibTeX | `'bibtex'` | via `format='bibtex'` |
| CSL-JSON | `'csljson'` | list of dicts |
| RIS | `'ris'` | list of unicode strings |
| RDF (Dublin Core) | `'rdf_dc'` | list of unicode strings |
| Zotero RDF | `'rdf_zotero'` | list of unicode strings |
| BibLaTeX | `'biblatex'` | list of unicode strings |
| Wikipedia Citation Templates | `'wikipedia'` | list of unicode strings |

**Note**: When using an export format as `content`, you must provide a `limit` parameter. Multiple simultaneous export formats are not supported.

```python
# Export as RIS
zot.add_parameters(content='ris', limit=50)
ris_data = zot.items()
with open('library.ris', 'w', encoding='utf-8') as f:
    f.write('\n'.join(ris_data))
```

## Keys Only

```python
# Get item keys as a newline-delimited string
zot.add_parameters(format='keys')
keys_str = zot.items()
keys = keys_str.strip().split('\n')
```

## Version Information (for syncing)

```python
# Dict of {key: version} for all items
zot.add_parameters(format='versions')
versions = zot.items()
```

### `references/files-attachments.md`

# Files & Attachments

## Downloading Files

```python
# Get raw binary content of an attachment
raw = zot.file('ATTACHMENTKEY')
with open('paper.pdf', 'wb') as f:
    f.write(raw)

# Convenient wrapper: dump file to disk
# Uses stored filename, saves to current directory
zot.dump('ATTACHMENTKEY')

# Dump to a specific path and filename
zot.dump('ATTACHMENTKEY', 'renamed_paper.pdf', '/home/user/papers/')
# Returns the full file path on success
```

**Note**: HTML snapshots are dumped as `.zip` files named with the item key.

## Finding Attachments

```python
# Get child items (attachments, notes) of a parent item
children = zot.children('PARENTKEY')
attachments = [c for c in children if c['data']['itemType'] == 'attachment']

# Get the attachment key
for att in attachments:
    key = att['data']['key']
    filename = att['data']['filename']
    content_type = att['data']['contentType']
    link_mode = att['data']['linkMode']  # 'imported_file', 'linked_file', 'imported_url', 'linked_url'
```

## Uploading Attachments

**Note**: Attachment upload methods are in beta.

```python
# Simple upload: one or more files by path
result = zot.attachment_simple(['/path/to/paper.pdf', '/path/to/notes.docx'])

# Upload as child items of a parent
result = zot.attachment_simple(['/path/to/paper.pdf'], parentid='PARENTKEY')

# Upload with custom filenames: list of (name, path) tuples
result = zot.attachment_both([
    ('Paper 2024.pdf', '/path/to/paper.pdf'),
    ('Supplementary.pdf', '/path/to/supp.pdf'),
], parentid='PARENTKEY')

# Upload files to existing attachment items
result = zot.upload_attachments(attachment_items, basedir='/path/to/files/')
```

Upload result structure:
```python
{
    'success': [attachment_item1, ...],
    'failure': [attachment_item2, ...],
    'unchanged': [attachment_item3, ...]
}
```

## Attachment Templates

```python
# Get template for a file attachment
template = zot.item_template('attachment', linkmode='imported_file')
# linkmode options: 'imported_file', 'linked_file', 'imported_url', 'linked_url'

# Available link modes
modes = zot.item_attachment_link_modes()
```

## Downloading All PDFs from a Collection

```python
import os

collection_key = 'COLKEY'
output_dir = '/path/to/output/'
os.makedirs(output_dir, exist_ok=True)

items = zot.everything(zot.collection_items(collection_key))
for item in items:
    children = zot.children(item['data']['key'])
    for child in children:
        if child['data']['itemType'] == 'attachment' and \
           child['data'].get('contentType') == 'application/pdf':
            try:
                zot.dump(child['data']['key'], path=output_dir)
            except Exception as e:
                print(f"Failed to download {child['data']['key']}: {e}")
```

### `references/full-text.md`

# Full-Text Content

Pyzotero can retrieve and set full-text index content for attachment items.

## Retrieving Full-Text Content

```python
# Get full-text content for a specific attachment item
data = zot.fulltext_item('ATTACHMENTKEY')
# Returns:
# {
#   "content": "Full text of the document...",
#   "indexedPages": 50,
#   "totalPages": 50
# }
# For text docs: indexedChars/totalChars instead of pages

text = data['content']
coverage = data['indexedPages'] / data['totalPages']
```

## Finding Items with New Full-Text Content

```python
# Get item keys with full-text updated since a library version
new_fulltext = zot.new_fulltext(since='1085')
# Returns dict: {'KEY1': 1090, 'KEY2': 1095, ...}
# Values are the library version at which full-text was indexed
```

## Setting Full-Text Content

```python
# Set full-text for a PDF attachment
payload = {
    'content': 'The full text content of the document.',
    'indexedPages': 50,
    'totalPages': 50
}
zot.set_fulltext('ATTACHMENTKEY', payload)

# For text documents use indexedChars/totalChars
payload = {
    'content': 'Full text here.',
    'indexedChars': 15000,
    'totalChars': 15000
}
zot.set_fulltext('ATTACHMENTKEY', payload)
```

## Full-Text Search via CLI

The CLI provides full-text search across locally indexed PDFs:

```bash
# Search full-text content
pyzotero search -q "CRISPR gene editing" --fulltext

# Output as JSON (retrieves parent bibliographic items for attachments)
pyzotero search -q "climate tipping points" --fulltext --json
```

## Search in API (qmode=everything)

```python
# Search in titles/creators + full-text content
results = zot.items(q='protein folding', qmode='everything', limit=20)
```

### `references/mcp.md`

# MCP Server

Pyzotero 1.12+ ships an optional [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that exposes your **local Zotero library** and Semantic Scholar integration as tools for LLM clients (e.g., Claude Desktop).

## Requirements

- **Zotero 7** with local API access enabled:
  - Zotero → Settings → Advanced → **Allow other applications on this computer to communicate with Zotero**
- Python 3.10+ (required by `pyzotero[mcp]`)

The MCP server reads from your local Zotero installation — it does not use the remote Web API or an API key.

## Installation

```bash
# In a project
uv add "pyzotero[mcp]"

# As a standalone tool
uv tool install "pyzotero[mcp]"
```

Run without installing:

```bash
uvx --from "pyzotero[mcp]" pyzotero-mcp
```

## Claude Desktop Configuration

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

**If `pyzotero-mcp` is installed:**

```json
{
  "mcpServers": {
    "zotero": {
      "command": "pyzotero-mcp"
    }
  }
}
```

**Without installing (via uvx):**

```json
{
  "mcpServers": {
    "zotero": {
      "command": "uvx",
      "args": ["--from", "pyzotero[mcp]", "pyzotero-mcp"]
    }
  }
}
```

## Available Tools

### Zotero Library Tools

| Tool | Description |
|------|-------------|
| `search` | Search the local library by query, item type, collection, tag, or full-text content |
| `get_item` | Get a single item by key |
| `get_children` | Get child items (attachments, notes) of an item |
| `list_collections` | List all collections |
| `list_tags` | List all tags, optionally filtered by collection |
| `get_fulltext` | Get full-text content of a PDF or other attachment |

### Semantic Scholar Tools

| Tool | Description |
|------|-------------|
| `find_related` | Find semantically similar papers (SPECTER2 embeddings) |
| `get_citations` | Find papers that cite a given paper |
| `get_references` | Find papers referenced by a given paper |
| `search_semantic_scholar` | Search Semantic Scholar's paper index |

Semantic Scholar tools can optionally check whether results already exist in your local Zotero library (`check_library` parameter, enabled by default).

## MCP vs Web API vs CLI

| Mode | Access | API key | Best for |
|------|--------|---------|----------|
| Web API (`Zotero(...)`) | Remote library sync | Required | Automation, bulk CRUD, group libraries |
| CLI (`pyzotero[cli]`) | Local Zotero 7 | Not required | Shell scripts, quick local search |
| MCP (`pyzotero[mcp]`) | Local Zotero 7 | Not required | LLM agents in sandboxed apps |

For remote library management from Python, use the Web API client documented in the other reference files. Use MCP or CLI when you need fast access to locally indexed PDFs and full-text search without network calls.

### `references/pagination.md`

# Pagination: follow(), everything(), Generators

Pyzotero returns 100 items by default. Use these methods to retrieve more.

## everything() — Retrieve All Results

The simplest way to get all items:

```python
# All items in the library
all_items = zot.everything(zot.items())

# All top-level items
all_top = zot.everything(zot.top())

# All items in a collection
all_col = zot.everything(zot.collection_items('COLKEY'))

# All items matching a search
all_results = zot.everything(zot.items(q='machine learning', itemType='journalArticle'))
```

`everything()` works with all Read API calls that can return multiple items.

## follow() — Sequential Pagination

```python
# Retrieve items in batches, manually advancing the page
first_batch = zot.top(limit=25)
second_batch = zot.follow()   # next 25 items
third_batch = zot.follow()    # next 25 items
```

**Warning**: `follow()` raises `StopIteration` when no more items are available. Not valid after single-item calls like `zot.item()`.

## iterfollow() — Generator

```python
# Create a generator over follow()
first = zot.top(limit=10)
lazy = zot.iterfollow()

# Retrieve subsequent pages
second = next(lazy)
third = next(lazy)
```

## makeiter() — Generator over Any Method

```python
# Create a generator directly from a method call
gen = zot.makeiter(zot.top(limit=25))

page1 = next(gen)  # first 25 items
page2 = next(gen)  # next 25 items
# Raises StopIteration when exhausted
```

## Manual start/limit Pagination

```python
page_size = 50
offset = 0

while True:
    batch = zot.items(limit=page_size, start=offset)
    if not batch:
        break
    # process batch
    for item in batch:
        process(item)
    offset += page_size
```

## Performance Notes

- `everything()` makes multiple API calls sequentially; large libraries may take time.
- For libraries with thousands of items, use `since=version` to retrieve only changed items (useful for sync workflows).
- All of `follow()`, `everything()`, and `makeiter()` are only valid for methods that return multiple items.

### `references/read-api.md`

# Read API Methods

## Retrieving Items

```python
# All items in library (100 per call by default)
items = zot.items()

# Top-level items only (excludes attachments/notes that are children)
top = zot.top(limit=25)

# A specific item by key
item = zot.item('ITEMKEY')

# Multiple specific items (up to 50 per call)
subset = zot.get_subset(['KEY1', 'KEY2', 'KEY3'])

# Items from trash
trash = zot.trash()

# Deleted items (requires 'since' parameter)
deleted = zot.deleted(since=1000)

# Items from "My Publications"
pubs = zot.publications()  # user libraries only

# Count all items
count = zot.count_items()

# Count top-level items
n = zot.num_items()
```

## Item Data Structure

Items are returned as dicts. Data lives in `item['data']`:

```python
item = zot.item('VDNIEAPH')[0]
title = item['data']['title']
item_type = item['data']['itemType']
creators = item['data']['creators']
tags = item['data']['tags']
key = item['data']['key']
version = item['data']['version']
collections = item['data']['collections']
doi = item['data'].get('DOI', '')
```

## Child Items

```python
# Get child items (notes, attachments) of a parent
children = zot.children('PARENTKEY')
```

## Retrieving Collections

```python
# All collections (including subcollections)
collections = zot.collections()

# Top-level collections only
top_collections = zot.collections_top()

# A specific collection
collection = zot.collection('COLLECTIONKEY')

# Sub-collections of a collection
sub = zot.collections_sub('COLLECTIONKEY')

# All collections and sub-collections in a flat list
all_cols = zot.all_collections()
# Or from a specific collection down:
all_cols = zot.all_collections('COLLECTIONKEY')

# Items in a specific collection (not sub-collections)
col_items = zot.collection_items('COLLECTIONKEY')

# Top-level items in a specific collection
col_top = zot.collection_items_top('COLLECTIONKEY')

# Count items in a collection
n = zot.num_collectionitems('COLLECTIONKEY')
```

## Retrieving Tags

```python
# All tags in the library
tags = zot.tags()

# Tags from a specific item
item_tags = zot.item_tags('ITEMKEY')

# Tags in a collection
col_tags = zot.collection_tags('COLLECTIONKEY')
```

## Retrieving Groups

```python
groups = zot.groups()
# Returns list of group libraries accessible to current key
```

## Version Information

```python
# Last modified version of the library
version = zot.last_modified_version()

# Item versions dict {key: version}
item_versions = zot.item_versions()

# Collection versions dict {key: version}
col_versions = zot.collection_versions()

# Changes since a known version (for syncing)
changed_items = zot.item_versions(since=1000)
```

## Library Settings

```python
settings = zot.settings()
# Returns synced settings (feeds, PDF reading progress, etc.)
# Use 'since' to get only changes:
new_settings = zot.settings(since=500)
```

## Saved Searches

```python
searches = zot.searches()
# Retrieves saved search metadata (not results)
```

### `references/saved-searches.md`

# Saved Searches

## Retrieving Saved Searches

```python
# Get all saved search metadata (not results)
searches = zot.searches()
# Returns list of dicts with name, key, conditions, version

for search in searches:
    print(search['data']['name'], search['data']['key'])
```

**Note**: Saved search *results* cannot be retrieved via the API (as of 2025). Only metadata is returned.

## Creating Saved Searches

Each condition dict must have `condition`, `operator`, and `value`:

```python
conditions = [
    {
        'condition': 'title',
        'operator': 'contains',
        'value': 'machine learning'
    }
]
zot.saved_search('ML Papers', conditions)
```

### Multiple Conditions (AND logic)

```python
conditions = [
    {'condition': 'itemType', 'operator': 'is', 'value': 'journalArticle'},
    {'condition': 'tag', 'operator': 'is', 'value': 'unread'},
    {'condition': 'date', 'operator': 'isAfter', 'value': '2023-01-01'},
]
zot.saved_search('Recent Unread Articles', conditions)
```

## Deleting Saved Searches

```python
# Get search keys first
searches = zot.searches()
keys = [s['data']['key'] for s in searches if s['data']['name'] == 'Old Search']
zot.delete_saved_search(keys)
```

## Discovering Valid Operators and Conditions

```python
# All available operators
operators = zot.show_operators()

# All available conditions
conditions = zot.show_conditions()

# Operators valid for a specific condition
title_operators = zot.show_condition_operators('title')
# e.g. ['is', 'isNot', 'contains', 'doesNotContain', 'beginsWith']
```

## Common Condition/Operator Combinations

| Condition | Common Operators |
|-----------|-----------------|
| `title` | `contains`, `doesNotContain`, `is`, `beginsWith` |
| `tag` | `is`, `isNot` |
| `itemType` | `is`, `isNot` |
| `date` | `isBefore`, `isAfter`, `is` |
| `creator` | `contains`, `is` |
| `publicationTitle` | `contains`, `is` |
| `year` | `is`, `isBefore`, `isAfter` |
| `collection` | `is`, `isNot` |
| `fulltextContent` | `contains` |

### `references/search-params.md`

# Search & Request Parameters

Parameters can be passed directly to any Read API call, or set globally with `add_parameters()`.

```python
# Inline parameters (valid for one call only)
results = zot.items(q='climate change', limit=50, sort='date', direction='desc')

# Set globally (overridden by inline params on the next call)
zot.add_parameters(limit=50, sort='dateAdded')
results = zot.items()
```

## Available Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | str | Quick search — titles and creator fields by default |
| `qmode` | str | `'titleCreatorYear'` (default) or `'everything'` (full-text) |
| `itemType` | str | Filter by item type. See search syntax for operators |
| `tag` | str or list | Filter by tag(s). Multiple tags = AND logic |
| `since` | int | Return only objects modified after this library version |
| `sort` | str | Sort field (see below) |
| `direction` | str | `'asc'` or `'desc'` |
| `limit` | int | 1–100, or `None` |
| `start` | int | Offset into result set |
| `format` | str | Response format (see exports.md) |
| `itemKey` | str | Comma-separated item keys (up to 50) |
| `content` | str | `'bib'`, `'html'`, `'citation'`, or export format |
| `style` | str | CSL style name (used with `content='bib'`) |
| `linkwrap` | str | `'1'` to wrap URLs in `<a>` tags in bibliography output |

## Sort Fields

`dateAdded`, `dateModified`, `title`, `creator`, `type`, `date`, `publisher`,
`publicationTitle`, `journalAbbreviation`, `language`, `accessDate`,
`libraryCatalog`, `callNumber`, `rights`, `addedBy`, `numItems`, `tags`

## Tag Search Syntax

```python
# Single tag
zot.items(tag='machine learning')

# Multiple tags — AND logic (items must have all tags)
zot.items(tag=['climate', 'adaptation'])

# OR logic (items with any tag)
zot.items(tag='climate OR adaptation')

# Exclude a tag
zot.items(tag='-retracted')
```

## Item Type Filtering

```python
# Single type
zot.items(itemType='journalArticle')

# OR multiple types
zot.items(itemType='journalArticle || book')

# Exclude a type
zot.items(itemType='-note')
```

Common item types: `journalArticle`, `book`, `bookSection`, `conferencePaper`,
`thesis`, `report`, `dataset`, `preprint`, `note`, `attachment`, `webpage`,
`patent`, `statute`, `case`, `hearing`, `interview`, `letter`, `manuscript`,
`map`, `artwork`, `audioRecording`, `videoRecording`, `podcast`, `film`,
`radioBroadcast`, `tvBroadcast`, `presentation`, `encyclopediaArticle`,
`dictionaryEntry`, `forumPost`, `blogPost`, `instantMessage`, `email`,
`document`, `computerProgram`, `bill`, `newspaperArticle`, `magazineArticle`

## Examples

```python
# Recent journal articles matching query, sorted by date
zot.items(q='CRISPR', itemType='journalArticle', sort='date', direction='desc', limit=20)

# Items added since a known library version
zot.items(since=4000)

# Items with a specific tag, offset for pagination
zot.items(tag='to-read', limit=25, start=25)

# Full-text search
zot.items(q='gene editing', qmode='everything', limit=10)
```

### `references/tags.md`

# Tag Management

## Retrieving Tags

```python
# All tags in the library
tags = zot.tags()
# Returns list of strings: ['climate change', 'machine learning', ...]

# Tags for a specific item
item_tags = zot.item_tags('ITEMKEY')

# Tags in a specific collection
col_tags = zot.collection_tags('COLKEY')

# Filter tags by prefix (e.g. all tags starting with 'bio')
filtered = zot.tags(q='bio')
```

## Adding Tags to Items

```python
# Add one or more tags to an item (retrieves item first)
item = zot.item('ITEMKEY')
updated = zot.add_tags(item, 'tag1', 'tag2', 'tag3')

# Add a list of tags
tag_list = ['reviewed', 'high-priority', '2024']
updated = zot.add_tags(item, *tag_list)
```

## Deleting Tags

```python
# Delete specific tags from the library
zot.delete_tags('old-tag', 'unused-tag')

# Delete a list of tags
tags_to_remove = ['deprecated', 'temp']
zot.delete_tags(*tags_to_remove)
```

## Searching Items by Tag

```python
# Items with a single tag
items = zot.items(tag='machine learning')

# Items with multiple tags (AND logic)
items = zot.items(tag=['climate', 'adaptation'])

# Items with any of these tags (OR logic)
items = zot.items(tag='climate OR sea level')

# Items NOT having a tag
items = zot.items(tag='-retracted')
```

## Batch Tag Operations

```python
# Add a tag to all items in a collection
items = zot.everything(zot.collection_items('COLKEY'))
for item in items:
    zot.add_tags(item, 'collection-reviewed')

# Find all items with a specific tag and retag them
old_tag_items = zot.everything(zot.items(tag='old-name'))
for item in old_tag_items:
    # Add new tag
    item['data']['tags'].append({'tag': 'new-name'})
    # Remove old tag
    item['data']['tags'] = [t for t in item['data']['tags'] if t['tag'] != 'old-name']
zot.update_items(old_tag_items)
```

## Tag Types

Zotero has two tag types stored in `tag['type']`:
- `0` — User-added tags (default)
- `1` — Automatically imported tags (from bibliographic databases)

```python
item = zot.item('ITEMKEY')
for tag in item['data']['tags']:
    print(tag['tag'], tag.get('type', 0))
```

### `references/write-api.md`

# Write API Methods

## Creating Items

Always use `item_template()` to get a valid template before creating items.

```python
# Get a template for a specific item type
template = zot.item_template('journalArticle')

# Fill in fields
template['title'] = 'Deep Learning for Genomics'
template['date'] = '2024'
template['publicationTitle'] = 'Nature Methods'
template['volume'] = '21'
template['DOI'] = '10.1038/s41592-024-02233-6'
template['creators'] = [
    {'creatorType': 'author', 'firstName': 'Jane', 'lastName': 'Doe'},
    {'creatorType': 'author', 'firstName': 'John', 'lastName': 'Smith'},
]

# Validate fields before creating (raises InvalidItemFields if invalid)
zot.check_items([template])

# Create the item
resp = zot.create_items([template])
# resp: {'success': {'0': 'NEWITEMKEY'}, 'failed': {}, 'unchanged': {}}
new_key = resp['success']['0']
```

### Create Multiple Items at Once

```python
templates = []
for data in paper_data_list:
    t = zot.item_template('journalArticle')
    t['title'] = data['title']
    t['DOI'] = data['doi']
    templates.append(t)

resp = zot.create_items(templates)
```

### Create Child Items

```python
# Create a note as a child of an existing item
note_template = zot.item_template('note')
note_template['note'] = '<p>My annotation here</p>'
zot.create_items([note_template], parentid='PARENTKEY')
```

## Updating Items

```python
# Retrieve, modify, update
item = zot.item('ITEMKEY')
item['data']['title'] = 'Updated Title'
item['data']['abstractNote'] = 'New abstract text.'
success = zot.update_item(item)  # returns True or raises error

# Update many items at once (auto-chunked at 50)
items = zot.items(limit=10)
for item in items:
    item['data']['extra'] += '\nProcessed'
zot.update_items(items)
```

## Deleting Items

```python
# Must retrieve item first (version field is required)
item = zot.item('ITEMKEY')
zot.delete_item([item])

# Delete multiple items
items = zot.items(tag='to-delete')
zot.delete_item(items)
```

## Item Types and Fields

```python
# All available item types
item_types = zot.item_types()
# [{'itemType': 'artwork', 'localized': 'Artwork'}, ...]

# All available fields
fields = zot.item_fields()

# Valid fields for a specific item type
journal_fields = zot.item_type_fields('journalArticle')

# Valid creator types for an item type
creator_types = zot.item_creator_types('journalArticle')
# [{'creatorType': 'author', 'localized': 'Author'}, ...]

# All localised creator field names
creator_fields = zot.creator_fields()

# Attachment link modes (needed for attachment templates)
link_modes = zot.item_attachment_link_modes()

# Template for an attachment
attach_template = zot.item_template('attachment', linkmode='imported_file')
```

## Optimistic Locking

Use `last_modified` to prevent overwriting concurrent changes:

```python
# Only update if library version matches
zot.update_item(item, last_modified=4025)
# Raises an error if the server version differs
```

## Notes

- `create_items()` accepts up to 50 items per call; batch if needed.
- `update_items()` auto-chunks at 50 items.
- If a dict passed to `create_items()` contains a `key` matching an existing item, it will be updated rather than created.
- Always call `check_items()` before `create_items()` to catch field errors early.
