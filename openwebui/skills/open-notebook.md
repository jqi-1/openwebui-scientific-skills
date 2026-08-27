---
name: open-notebook
description: Encryption key for stored content, if configured.
---

# Open Notebook

## Overview

Open Notebook is an open-source, self-hosted alternative to Google's NotebookLM that enables researchers to organize materials, generate AI-powered insights, create podcasts, and have context-aware conversations with their documents — all while maintaining complete data privacy.

Unlike Google's Notebook LM, which has no publicly available API outside of the Enterprise version, Open Notebook provides a comprehensive REST API, supports 16+ AI providers, and runs entirely on your own infrastructure.

**Key advantages over NotebookLM:**
- Full REST API for programmatic access and automation
- Choice of 16+ AI providers (not locked to Google models)
- Multi-speaker podcast generation with 1-4 customizable speakers (vs. 2-speaker limit)
- Complete data sovereignty through self-hosting
- Open source and fully extensible (MIT license)

**Repository:** https://github.com/lfnovo/open-notebook

## Quick Start

### Prerequisites

- Docker Desktop installed
- API key for at least one AI provider (or local Ollama for free local inference)

### Installation

Deploy Open Notebook using Docker Compose:

```bash
# Download the docker-compose file
curl -o docker-compose.yml https://raw.githubusercontent.com/lfnovo/open-notebook/main/docker-compose.yml

# Set the required encryption key
export OPEN_NOTEBOOK_ENCRYPTION_KEY="your-secret-key-here"

# Launch the services
docker-compose up -d
```

Access the application:
- **Frontend UI:** http://localhost:8502
- **REST API:** http://localhost:5055
- **API Documentation:** http://localhost:5055/docs

### Configure AI Provider

After startup, configure at least one AI provider:

1. Navigate to **Settings > API Keys** in the UI
2. Add credentials for your preferred provider (OpenAI, Anthropic, etc.)
3. Test the connection and discover available models
4. Register models for use across the platform

Or configure via the REST API:

```python
import requests

BASE_URL = "http://localhost:5055/api"

# Add a credential for an AI provider
response = requests.post(f"{BASE_URL}/credentials", json={
    "provider": "openai",
    "name": "My OpenAI Key",
    "api_key": "sk-..."
})
credential = response.json()

# Discover available models
response = requests.post(
    f"{BASE_URL}/credentials/{credential['id']}/discover"
)
discovered = response.json()

# Register discovered models
requests.post(
    f"{BASE_URL}/credentials/{credential['id']}/register-models",
    json={"model_ids": [m["id"] for m in discovered["models"]]}
)
```

## Core Features

### Notebooks
Organize research into separate notebooks, each containing sources, notes, and chat sessions.

```python
import requests

BASE_URL = "http://localhost:5055/api"

# Create a notebook
response = requests.post(f"{BASE_URL}/notebooks", json={
    "name": "Cancer Genomics Research",
    "description": "Literature review on tumor mutational burden"
})
notebook = response.json()
notebook_id = notebook["id"]
```

### Sources
Ingest diverse content types including PDFs, videos, audio files, web pages, and Office documents. Sources are processed for full-text and vector search.

```python
# Add a web URL source
response = requests.post(f"{BASE_URL}/sources", data={
    "url": "https://arxiv.org/abs/2301.00001",
    "notebook_id": notebook_id,
    "process_async": "true"
})
source = response.json()

# Upload a PDF file
with open("paper.pdf", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/sources",
        data={"notebook_id": notebook_id},
        files={"file": ("paper.pdf", f, "application/pdf")}
    )
```

### Notes
Create and manage notes (human or AI-generated) associated with notebooks.

```python
# Create a human note
response = requests.post(f"{BASE_URL}/notes", json={
    "title": "Key Findings",
    "content": "TMB correlates with immunotherapy response in NSCLC...",
    "note_type": "human",
    "notebook_id": notebook_id
})
```

### Context-Aware Chat
Chat with your research materials using AI that cites sources.

```python
# Create a chat session
session = requests.post(f"{BASE_URL}/chat/sessions", json={
    "notebook_id": notebook_id,
    "title": "TMB Discussion"
}).json()

# Send a message with context from sources
response = requests.post(f"{BASE_URL}/chat/execute", json={
    "session_id": session["id"],
    "message": "What are the key biomarkers for immunotherapy response?",
    "context": {"include_sources": True, "include_notes": True}
})
```

### Search
Search across all materials using full-text or vector (semantic) search.

```python
# Vector search across the knowledge base
results = requests.post(f"{BASE_URL}/search", json={
    "query": "tumor mutational burden immunotherapy",
    "search_type": "vector",
    "limit": 10
}).json()

# Ask a question with AI-powered answer
answer = requests.post(f"{BASE_URL}/search/ask/simple", json={
    "query": "How does TMB predict checkpoint inhibitor response?"
}).json()
```

### Podcast Generation
Generate professional multi-speaker podcasts from research materials with 1-4 customizable speakers.

```python
# Generate a podcast episode
job = requests.post(f"{BASE_URL}/podcasts/generate", json={
    "notebook_id": notebook_id,
    "episode_profile_id": episode_profile_id,
    "speaker_profile_ids": [speaker1_id, speaker2_id]
}).json()

# Check generation status
status = requests.get(f"{BASE_URL}/podcasts/jobs/{job['job_id']}").json()

# Download audio when ready
audio = requests.get(
    f"{BASE_URL}/podcasts/episodes/{status['episode_id']}/audio"
)
```

### Content Transformations
Apply custom AI-powered transformations to content for summarization, extraction, and analysis.

```python
# Create a custom transformation
transform = requests.post(f"{BASE_URL}/transformations", json={
    "name": "extract_methods",
    "title": "Extract Methods",
    "description": "Extract methodology details from papers",
    "prompt": "Extract and summarize the methodology section...",
    "apply_default": False
}).json()

# Execute transformation on text
result = requests.post(f"{BASE_URL}/transformations/execute", json={
    "transformation_id": transform["id"],
    "input_text": "...",
    "model_id": "model_id_here"
}).json()
```

## Supported AI Providers

Open Notebook supports 16+ AI providers through the Esperanto library:

| Provider | LLM | Embedding | Speech-to-Text | Text-to-Speech |
|----------|-----|-----------|----------------|----------------|
| OpenAI | Yes | Yes | Yes | Yes |
| Anthropic | Yes | No | No | No |
| Google GenAI | Yes | Yes | No | Yes |
| Vertex AI | Yes | Yes | No | Yes |
| Ollama | Yes | Yes | No | No |
| Groq | Yes | No | Yes | No |
| Mistral | Yes | Yes | No | No |
| Azure OpenAI | Yes | Yes | No | No |
| DeepSeek | Yes | No | No | No |
| xAI | Yes | No | No | No |
| OpenRouter | Yes | No | No | No |
| ElevenLabs | No | No | Yes | Yes |
| Perplexity | Yes | No | No | No |
| Voyage | No | Yes | No | No |

## Environment Variables

Key configuration variables for Docker deployment:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPEN_NOTEBOOK_ENCRYPTION_KEY` | **Required.** Secret key for encrypting stored credentials | None |
| `SURREAL_URL` | SurrealDB connection URL | `ws://surrealdb:8000/rpc` |
| `SURREAL_NAMESPACE` | Database namespace | `open_notebook` |
| `SURREAL_DATABASE` | Database name | `open_notebook` |
| `OPEN_NOTEBOOK_PASSWORD` | Optional password protection for the UI | None |

## API Reference

The REST API is available at `http://localhost:5055/api` with interactive documentation at `/docs`.

Core endpoint groups:
- `/api/notebooks` - Notebook CRUD and source association
- `/api/sources` - Source ingestion, processing, and retrieval
- `/api/notes` - Note management
- `/api/chat/sessions` - Chat session management
- `/api/chat/execute` - Chat message execution
- `/api/search` - Full-text and vector search
- `/api/podcasts` - Podcast generation and management
- `/api/transformations` - Content transformation pipelines
- `/api/models` - AI model configuration and discovery
- `/api/credentials` - Provider credential management

For complete API reference with all endpoints and request/response formats, see `references/api_reference.md`.

## Architecture

Open Notebook uses a modern stack:
- **Backend:** Python with FastAPI
- **Database:** SurrealDB (document + relational)
- **AI Integration:** LangChain with the Esperanto multi-provider library
- **Frontend:** Next.js with React
- **Deployment:** Docker Compose with persistent volumes

## Important Notes

- Open Notebook requires Docker for deployment
- At least one AI provider must be configured for AI features to work
- For free local inference without API costs, use Ollama
- The `OPEN_NOTEBOOK_ENCRYPTION_KEY` must be set before first launch and kept consistent across restarts
- All data is stored locally in Docker volumes for complete data sovereignty

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/open-notebook/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/api_reference.md`

# Open Notebook API Reference

## Base URL

```
http://localhost:5055/api
```

Interactive API documentation is available at `http://localhost:5055/docs` (Swagger UI) and `http://localhost:5055/redoc` (ReDoc).

## Authentication

If `OPEN_NOTEBOOK_PASSWORD` is configured, include the password in requests. The following routes are excluded from authentication: `/`, `/health`, `/docs`, `/openapi.json`, `/redoc`, `/api/auth/status`, `/api/config`.

---

## Notebooks

### List Notebooks

```
GET /api/notebooks
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `archived` | boolean | Filter by archived status |
| `order_by` | string | Sort field (default: `updated_at`) |

**Response:** Array of notebook objects with `source_count` and `note_count`.

### Create Notebook

```
POST /api/notebooks
```

**Request Body:**
```json
{
  "name": "My Research",
  "description": "Optional description"
}
```

### Get Notebook

```
GET /api/notebooks/{notebook_id}
```

### Update Notebook

```
PUT /api/notebooks/{notebook_id}
```

**Request Body:**
```json
{
  "name": "Updated Name",
  "description": "Updated description",
  "archived": false
}
```

### Delete Notebook

```
DELETE /api/notebooks/{notebook_id}
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `delete_sources` | boolean | Also delete exclusive sources (default: false) |

### Delete Preview

```
GET /api/notebooks/{notebook_id}/delete-preview
```

Returns counts of notes and sources that would be affected by deletion.

### Link Source to Notebook

```
POST /api/notebooks/{notebook_id}/sources/{source_id}
```

Idempotent operation to associate a source with a notebook.

### Unlink Source from Notebook

```
DELETE /api/notebooks/{notebook_id}/sources/{source_id}
```

---

## Sources

### List Sources

```
GET /api/sources
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `notebook_id` | string | Filter by notebook |
| `limit` | integer | Number of results |
| `offset` | integer | Pagination offset |
| `order_by` | string | Sort field |

### Create Source

```
POST /api/sources
```

Accepts multipart form data for file uploads or JSON for URL/text sources.

**Form Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `file` | file | Upload file (PDF, DOCX, audio, video) |
| `url` | string | Web URL to ingest |
| `text` | string | Raw text content |
| `notebook_id` | string | Associate with notebook |
| `process_async` | boolean | Process asynchronously (default: true) |

### Create Source (JSON)

```
POST /api/sources/json
```

Legacy JSON-based endpoint for source creation.

### Get Source

```
GET /api/sources/{source_id}
```

### Get Source Status

```
GET /api/sources/{source_id}/status
```

Poll processing status for asynchronously ingested sources.

### Update Source

```
PUT /api/sources/{source_id}
```

**Request Body:**
```json
{
  "title": "Updated Title",
  "topic": "Updated topic"
}
```

### Delete Source

```
DELETE /api/sources/{source_id}
```

### Download Source File

```
GET /api/sources/{source_id}/download
```

Returns the original uploaded file.

### Check Source File

```
HEAD /api/sources/{source_id}/download
```

### Retry Failed Source

```
POST /api/sources/{source_id}/retry
```

Requeue a failed source for processing.

### Get Source Insights

```
GET /api/sources/{source_id}/insights
```

Retrieve AI-generated insights for a source.

---

## Notes

### List Notes

```
GET /api/notes
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `notebook_id` | string | Filter by notebook |

### Create Note

```
POST /api/notes
```

**Request Body:**
```json
{
  "title": "My Note",
  "content": "Note content...",
  "note_type": "human",
  "notebook_id": "notebook:abc123"
}
```

`note_type` must be `"human"` or `"ai"`. AI notes without titles get auto-generated titles.

### Get Note

```
GET /api/notes/{note_id}
```

### Update Note

```
PUT /api/notes/{note_id}
```

**Request Body:**
```json
{
  "title": "Updated Title",
  "content": "Updated content",
  "note_type": "human"
}
```

### Delete Note

```
DELETE /api/notes/{note_id}
```

---

## Chat

### List Sessions

```
GET /api/chat/sessions
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `notebook_id` | string | Filter by notebook |

### Create Session

```
POST /api/chat/sessions
```

**Request Body:**
```json
{
  "notebook_id": "notebook:abc123",
  "title": "Discussion Topic",
  "model_override": "optional_model_id"
}
```

### Get Session

```
GET /api/chat/sessions/{session_id}
```

Returns session details with message history.

### Update Session

```
PUT /api/chat/sessions/{session_id}
```

### Delete Session

```
DELETE /api/chat/sessions/{session_id}
```

### Execute Chat

```
POST /api/chat/execute
```

**Request Body:**
```json
{
  "session_id": "chat_session:abc123",
  "message": "Your question here",
  "context": {
    "include_sources": true,
    "include_notes": true
  },
  "model_override": "optional_model_id"
}
```

### Build Context

```
POST /api/chat/context
```

Build contextual data from sources and notes for a chat session.

---

## Search

### Search Knowledge Base

```
POST /api/search
```

**Request Body:**
```json
{
  "query": "search terms",
  "search_type": "vector",
  "limit": 10,
  "source_ids": [],
  "note_ids": [],
  "min_similarity": 0.7
}
```

`search_type` can be `"vector"` (requires embedding model) or `"text"` (keyword matching).

### Ask with Streaming

```
POST /api/search/ask
```

Returns Server-Sent Events with AI-generated answers based on knowledge base content.

### Ask Simple

```
POST /api/search/ask/simple
```

Non-streaming version that returns a complete response.

---

## Podcasts

### Generate Podcast

```
POST /api/podcasts/generate
```

**Request Body:**
```json
{
  "notebook_id": "notebook:abc123",
  "episode_profile_id": "episode_profile:xyz",
  "speaker_profile_ids": ["speaker:a", "speaker:b"]
}
```

Returns a `job_id` for tracking generation progress.

### Get Job Status

```
GET /api/podcasts/jobs/{job_id}
```

### List Episodes

```
GET /api/podcasts/episodes
```

### Get Episode

```
GET /api/podcasts/episodes/{episode_id}
```

### Get Episode Audio

```
GET /api/podcasts/episodes/{episode_id}/audio
```

Streams the podcast audio file.

### Retry Failed Episode

```
POST /api/podcasts/episodes/{episode_id}/retry
```

### Delete Episode

```
DELETE /api/podcasts/episodes/{episode_id}
```

---

## Transformations

### List Transformations

```
GET /api/transformations
```

### Create Transformation

```
POST /api/transformations
```

**Request Body:**
```json
{
  "name": "summarize",
  "title": "Summarize Content",
  "description": "Generate a concise summary",
  "prompt": "Summarize the following text...",
  "apply_default": false
}
```

### Execute Transformation

```
POST /api/transformations/execute
```

**Request Body:**
```json
{
  "transformation_id": "transformation:abc",
  "input_text": "Text to transform...",
  "model_id": "model:xyz"
}
```

### Get Default Prompt

```
GET /api/transformations/default-prompt
```

### Update Default Prompt

```
PUT /api/transformations/default-prompt
```

### Get Transformation

```
GET /api/transformations/{transformation_id}
```

### Update Transformation

```
PUT /api/transformations/{transformation_id}
```

### Delete Transformation

```
DELETE /api/transformations/{transformation_id}
```

---

## Models

### List Models

```
GET /api/models
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `model_type` | string | Filter by type (llm, embedding, stt, tts) |

### Create Model

```
POST /api/models
```

### Delete Model

```
DELETE /api/models/{model_id}
```

### Test Model

```
POST /api/models/{model_id}/test
```

### Get Default Models

```
GET /api/models/defaults
```

Returns default model assignments for seven service slots: chat, transformation, embedding, speech-to-text, text-to-speech, podcast, and summary.

### Update Default Models

```
PUT /api/models/defaults
```

### Get Providers

```
GET /api/models/providers
```

### Discover Models

```
GET /api/models/discover/{provider}
```

### Sync Models (Single Provider)

```
POST /api/models/sync/{provider}
```

### Sync All Models

```
POST /api/models/sync
```

### Auto-Assign Defaults

```
POST /api/models/auto-assign
```

Automatically populate empty default model slots using provider priority rankings.

### Get Model Count

```
GET /api/models/count/{provider}
```

### Get Models by Provider

```
GET /api/models/by-provider/{provider}
```

---

## Credentials

### Get Status

```
GET /api/credentials/status
```

### Get Environment Status

```
GET /api/credentials/env-status
```

### List Credentials

```
GET /api/credentials
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `provider` | string | Filter by provider |

### List by Provider

```
GET /api/credentials/by-provider/{provider}
```

### Create Credential

```
POST /api/credentials
```

**Request Body:**
```json
{
  "provider": "openai",
  "name": "My OpenAI Key",
  "api_key": "sk-...",
  "base_url": null
}
```

### Get Credential

```
GET /api/credentials/{credential_id}
```

Note: API key values are never returned.

### Update Credential

```
PUT /api/credentials/{credential_id}
```

### Delete Credential

```
DELETE /api/credentials/{credential_id}
```

### Test Credential

```
POST /api/credentials/{credential_id}/test
```

### Discover Models via Credential

```
POST /api/credentials/{credential_id}/discover
```

### Register Models via Credential

```
POST /api/credentials/{credential_id}/register-models
```

---

## Error Responses

The API returns standard HTTP status codes with JSON error bodies:

| Status | Meaning |
|--------|---------|
| 400 | Invalid input |
| 401 | Authentication required |
| 404 | Resource not found |
| 422 | Configuration error |
| 429 | Rate limited |
| 500 | Internal server error |
| 502 | External service error |

**Error Response Format:**
```json
{
  "detail": "Description of the error"
}
```

### `references/architecture.md`

# Open Notebook Architecture

## System Overview

Open Notebook is built as a modern Python web application with a clear separation between frontend and backend, using Docker for deployment.

```
┌─────────────────────────────────────────────────────┐
│                   Docker Compose                    │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │   Next.js    │  │   FastAPI    │  │ SurrealDB │  │
│  │   Frontend   │──│   Backend    │──│           │  │
│  │  (port 8502) │  │  (port 5055) │  │ (port 8K) │  │
│  └──────────────┘  └──────────────┘  └───────────┘  │
│                          │                          │
│                    ┌─────┴─────┐                    │
│                    │ LangChain │                    │
│                    │ Esperanto │                    │
│                    └─────┬─────┘                    │
│                          │                          │
│              ┌───────────┼───────────┐              │
│              │           │           │              │
│          ┌───┴───┐   ┌───┴───┐   ┌───┴───┐          │
│          │OpenAI │   │Claude │   │Ollama │  ...     │
│          └───────┘   └───────┘   └───────┘          │
└─────────────────────────────────────────────────────┘
```

## Core Components

### FastAPI Backend

The REST API is built with FastAPI and organized into routers:

- **20 route modules** covering notebooks, sources, notes, chat, search, podcasts, transformations, models, credentials, embeddings, settings, and more
- Async/await throughout for non-blocking I/O
- Pydantic models for request/response validation
- Custom exception handlers mapping domain errors to HTTP status codes
- CORS middleware for cross-origin access
- Optional password authentication middleware

### SurrealDB

SurrealDB serves as the primary data store, providing both document and relational capabilities:

- **Document storage** for notebooks, sources, notes, transformations, and models
- **Relational references** for notebook-source associations
- **Full-text search** across indexed content
- **RocksDB** backend for persistent storage on disk
- Schema migrations run automatically on application startup

### LangChain Integration

AI features are powered by LangChain with the Esperanto multi-provider library:

- **LangGraph** manages conversational state for chat sessions
- **Embedding models** power vector search across content
- **LLM chains** drive transformations, note generation, and podcast scripting
- **Prompt templates** stored in the `prompts/` directory

### Esperanto Multi-Provider Library

Esperanto provides a unified interface to 16+ AI providers:

- Abstracts provider-specific API differences
- Supports LLM, embedding, speech-to-text, and text-to-speech capabilities
- Handles credential management and model discovery
- Enables runtime provider switching without code changes

### Next.js Frontend

The user interface is a React application built with Next.js:

- Responsive design for desktop and tablet use
- Real-time updates for chat and processing status
- File upload with progress tracking
- Audio player for podcast episodes

## Data Flow

### Source Ingestion

```
Upload/URL → Source Record Created → Processing Queue
                                         │
                              ┌──────────┼──────────┐
                              ▼          ▼          ▼
                          Text       Embedding   Metadata
                        Extraction   Generation  Extraction
                              │          │          │
                              └──────────┼──────────┘
                                         ▼
                                  Source Updated
                                  (searchable)
```

### Chat Execution

```
User Message → Build Context (sources + notes)
                    │
                    ▼
              LangGraph State Machine
                    │
                    ├─ Retrieve relevant context
                    ├─ Format prompt with citations
                    └─ Stream LLM response
                         │
                         ▼
                   Response with
                   source citations
```

### Podcast Generation

```
Notebook Content → Episode Profile → Script Generation (LLM)
                                          │
                                          ▼
                                    Speaker Assignment
                                          │
                                          ▼
                                    Text-to-Speech
                                    (per segment)
                                          │
                                          ▼
                                    Audio Assembly
                                          │
                                          ▼
                                    Episode Record
                                    + Audio File
```

## Key Design Decisions

1. **Multi-provider by default**: Not locked to any single AI provider, enabling cost optimization and capability matching
2. **Async processing**: Long-running operations (source ingestion, podcast generation) run asynchronously with status polling
3. **Self-hosted data**: All data stays on the user's infrastructure with encrypted credential storage
4. **REST-first API**: Every UI action is backed by an API endpoint for automation
5. **Docker-native**: Designed for containerized deployment with persistent volumes

## File Structure

```
open-notebook/
├── api/               # FastAPI REST API
│   ├── main.py        # App setup, middleware, routers
│   ├── routers/       # Route handlers (20 modules)
│   ├── models.py      # Pydantic request/response models
│   └── auth.py        # Authentication middleware
├── open_notebook/     # Core library
│   ├── ai/            # AI integration (LangChain, Esperanto)
│   ├── database/      # SurrealDB operations
│   ├── domain/        # Domain models and business logic
│   ├── graphs/        # LangGraph chat and processing graphs
│   ├── podcasts/      # Podcast generation pipeline
│   └── utils/         # Shared utilities
├── frontend/          # Next.js React application
├── prompts/           # AI prompt templates
├── tests/             # Test suite
└── docker-compose.yml # Deployment configuration
```

### `references/configuration.md`

# Open Notebook Configuration Guide

## Docker Deployment

Open Notebook is deployed as a Docker Compose stack with two main services: the application server and SurrealDB.

### Minimal docker-compose.yml

```yaml
version: "3.8"

services:
  surrealdb:
    image: surrealdb/surrealdb:latest
    command: start --user root --pass root rocksdb://data/database.db
    volumes:
      - surrealdb_data:/data
    ports:
      - "8000:8000"

  open-notebook:
    image: ghcr.io/lfnovo/open-notebook:latest
    depends_on:
      - surrealdb
    environment:
      - OPEN_NOTEBOOK_ENCRYPTION_KEY=${OPEN_NOTEBOOK_ENCRYPTION_KEY}
      - SURREAL_URL=ws://surrealdb:8000/rpc
      - SURREAL_NAMESPACE=open_notebook
      - SURREAL_DATABASE=open_notebook
    ports:
      - "8502:8502"   # Frontend UI
      - "5055:5055"   # REST API
    volumes:
      - on_uploads:/app/uploads

volumes:
  surrealdb_data:
  on_uploads:
```

### Starting the Stack

```bash
# Set the encryption key (required)
export OPEN_NOTEBOOK_ENCRYPTION_KEY="your-secure-random-key"

# Start services
docker-compose up -d

# View logs
docker-compose logs -f open-notebook

# Stop services
docker-compose down

# Stop and remove data
docker-compose down -v
```

## Environment Variables

### Required

| Variable | Description |
|----------|-------------|
| `OPEN_NOTEBOOK_ENCRYPTION_KEY` | Secret key for encrypting stored API credentials. Must be set before first launch and kept consistent. |

### Database

| Variable | Default | Description |
|----------|---------|-------------|
| `SURREAL_URL` | `ws://surrealdb:8000/rpc` | SurrealDB WebSocket connection URL |
| `SURREAL_NAMESPACE` | `open_notebook` | SurrealDB namespace |
| `SURREAL_DATABASE` | `open_notebook` | SurrealDB database name |
| `SURREAL_USER` | `root` | SurrealDB username |
| `SURREAL_PASS` | `root` | SurrealDB password |

### Application

| Variable | Default | Description |
|----------|---------|-------------|
| `OPEN_NOTEBOOK_PASSWORD` | None | Optional password protection for the web UI |
| `UPLOAD_DIR` | `/app/uploads` | Directory for uploaded file storage |

### AI Provider Keys (Legacy)

API keys can also be set via environment variables for legacy compatibility. The preferred method is using the credentials API or UI.

| Variable | Provider |
|----------|----------|
| `OPENAI_API_KEY` | OpenAI |
| `ANTHROPIC_API_KEY` | Anthropic |
| `GOOGLE_API_KEY` | Google GenAI |
| `GROQ_API_KEY` | Groq |
| `MISTRAL_API_KEY` | Mistral |
| `ELEVENLABS_API_KEY` | ElevenLabs |

## AI Provider Configuration

### Via UI

1. Go to **Settings > API Keys**
2. Click **Add Credential**
3. Select provider, enter API key and optional base URL
4. Click **Test Connection** to verify
5. Click **Discover Models** to find available models
6. Select models to register

### Via API

```python
import requests

BASE_URL = "http://localhost:5055/api"

# 1. Create credential
cred = requests.post(f"{BASE_URL}/credentials", json={
    "provider": "anthropic",
    "name": "Anthropic Production",
    "api_key": "sk-ant-..."
}).json()

# 2. Test connection
test = requests.post(f"{BASE_URL}/credentials/{cred['id']}/test").json()
assert test["success"]

# 3. Discover and register models
discovered = requests.post(
    f"{BASE_URL}/credentials/{cred['id']}/discover"
).json()

requests.post(
    f"{BASE_URL}/credentials/{cred['id']}/register-models",
    json={"model_ids": [m["id"] for m in discovered["models"]]}
)

# 4. Auto-assign defaults
requests.post(f"{BASE_URL}/models/auto-assign")
```

### Using Ollama (Free Local Inference)

For free AI inference without API costs, use Ollama:

```yaml
# docker-compose-ollama.yml addition
services:
  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
```

Then configure Ollama as a provider with base URL `http://ollama:11434`.

## Security Configuration

### Password Protection

Set `OPEN_NOTEBOOK_PASSWORD` to require authentication:

```bash
export OPEN_NOTEBOOK_PASSWORD="your-ui-password"
```

### Reverse Proxy (Nginx Example)

```nginx
server {
    listen 443 ssl;
    server_name notebook.example.com;

    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;

    location / {
        proxy_pass http://localhost:8502;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location /api/ {
        proxy_pass http://localhost:5055/api/;
        proxy_set_header Host $host;
    }
}
```

## Backup and Restore

### Backup SurrealDB Data

```bash
# Export database
docker exec surrealdb surreal export \
  --conn ws://localhost:8000 \
  --user root --pass root \
  --ns open_notebook --db open_notebook \
  /tmp/backup.surql

# Copy backup from container
docker cp surrealdb:/tmp/backup.surql ./backup.surql
```

### Backup Uploaded Files

```bash
# Copy upload volume contents
docker cp open-notebook:/app/uploads ./uploads_backup/
```

### Restore

```bash
# Import database backup
docker cp ./backup.surql surrealdb:/tmp/backup.surql
docker exec surrealdb surreal import \
  --conn ws://localhost:8000 \
  --user root --pass root \
  --ns open_notebook --db open_notebook \
  /tmp/backup.surql
```

### `references/examples.md`

# Open Notebook Examples

## Complete Research Workflow

This example demonstrates a full research workflow: creating a notebook, adding sources, generating notes, chatting with the AI, and searching across materials.

```python
import requests
import time

BASE_URL = "http://localhost:5055/api"


def complete_research_workflow():
    """End-to-end research workflow with Open Notebook."""

    # 1. Create a research notebook
    notebook = requests.post(f"{BASE_URL}/notebooks", json={
        "name": "Drug Resistance in Cancer",
        "description": "Review of mechanisms of drug resistance in solid tumors"
    }).json()
    notebook_id = notebook["id"]
    print(f"Created notebook: {notebook_id}")

    # 2. Add sources from URLs
    urls = [
        "https://www.nature.com/articles/s41568-020-0281-y",
        "https://www.cell.com/cancer-cell/fulltext/S1535-6108(20)30211-8",
    ]

    source_ids = []
    for url in urls:
        source = requests.post(f"{BASE_URL}/sources", data={
            "url": url,
            "notebook_id": notebook_id,
            "process_async": "true"
        }).json()
        source_ids.append(source["id"])
        print(f"Added source: {source['id']}")

    # 3. Wait for processing to complete
    for source_id in source_ids:
        while True:
            status = requests.get(
                f"{BASE_URL}/sources/{source_id}/status"
            ).json()
            if status.get("status") in ("completed", "failed"):
                break
            time.sleep(5)
        print(f"Source {source_id}: {status['status']}")

    # 4. Create a chat session and ask questions
    session = requests.post(f"{BASE_URL}/chat/sessions", json={
        "notebook_id": notebook_id,
        "title": "Resistance Mechanisms"
    }).json()

    answer = requests.post(f"{BASE_URL}/chat/execute", json={
        "session_id": session["id"],
        "message": "What are the primary mechanisms of drug resistance in solid tumors?",
        "context": {"include_sources": True, "include_notes": True}
    }).json()
    print(f"AI response: {answer}")

    # 5. Search across materials
    results = requests.post(f"{BASE_URL}/search", json={
        "query": "efflux pump resistance mechanism",
        "search_type": "vector",
        "limit": 5
    }).json()
    print(f"Found {results['total']} search results")

    # 6. Create a human note summarizing findings
    note = requests.post(f"{BASE_URL}/notes", json={
        "title": "Summary of Resistance Mechanisms",
        "content": "Key findings from the literature...",
        "note_type": "human",
        "notebook_id": notebook_id
    }).json()
    print(f"Created note: {note['id']}")


if __name__ == "__main__":
    complete_research_workflow()
```

## File Upload Example

```python
import requests

BASE_URL = "http://localhost:5055/api"


def upload_research_papers(notebook_id, file_paths):
    """Upload multiple research papers to a notebook."""
    for path in file_paths:
        with open(path, "rb") as f:
            response = requests.post(
                f"{BASE_URL}/sources",
                data={
                    "notebook_id": notebook_id,
                    "process_async": "true",
                },
                files={"file": (path.split("/")[-1], f)},
            )
        if response.status_code == 200:
            print(f"Uploaded: {path}")
        else:
            print(f"Failed: {path} - {response.text}")


# Usage
upload_research_papers("notebook:abc123", [
    "papers/study_1.pdf",
    "papers/study_2.pdf",
    "papers/supplementary.docx",
])
```

## Podcast Generation Example

```python
import requests
import time

BASE_URL = "http://localhost:5055/api"


def generate_research_podcast(notebook_id):
    """Generate a podcast episode from notebook contents."""

    # Get available episode and speaker profiles
    # (these must be configured in the UI or via API first)

    # Submit podcast generation job
    job = requests.post(f"{BASE_URL}/podcasts/generate", json={
        "notebook_id": notebook_id,
        "episode_profile_id": "episode_profile:default",
        "speaker_profile_ids": [
            "speaker_profile:host",
            "speaker_profile:expert"
        ]
    }).json()
    job_id = job["job_id"]
    print(f"Podcast generation started: {job_id}")

    # Poll for completion
    while True:
        status = requests.get(f"{BASE_URL}/podcasts/jobs/{job_id}").json()
        print(f"Status: {status.get('status', 'processing')}")
        if status.get("status") in ("completed", "failed"):
            break
        time.sleep(10)

    if status["status"] == "completed":
        # Download the audio
        episode_id = status["episode_id"]
        audio = requests.get(
            f"{BASE_URL}/podcasts/episodes/{episode_id}/audio"
        )
        with open("research_podcast.mp3", "wb") as f:
            f.write(audio.content)
        print("Podcast saved to research_podcast.mp3")


if __name__ == "__main__":
    generate_research_podcast("notebook:abc123")
```

## Custom Transformation Pipeline

```python
import requests

BASE_URL = "http://localhost:5055/api"


def create_and_run_transformations():
    """Create custom transformations and apply them to content."""

    # Create a methodology extraction transformation
    transform = requests.post(f"{BASE_URL}/transformations", json={
        "name": "extract_methods",
        "title": "Extract Methods",
        "description": "Extract and structure methodology from papers",
        "prompt": (
            "Extract the methodology section from this text. "
            "Organize into: Study Design, Sample Size, Statistical Methods, "
            "and Key Variables. Format as structured markdown."
        ),
        "apply_default": False,
    }).json()

    # Get models to find a suitable one
    models = requests.get(f"{BASE_URL}/models", params={
        "model_type": "llm"
    }).json()
    model_id = models[0]["id"]

    # Execute the transformation
    result = requests.post(f"{BASE_URL}/transformations/execute", json={
        "transformation_id": transform["id"],
        "input_text": "We conducted a randomized controlled trial with...",
        "model_id": model_id,
    }).json()
    print(f"Extracted methods:\n{result['output']}")


if __name__ == "__main__":
    create_and_run_transformations()
```

## Semantic Search with Filtering

```python
import requests

BASE_URL = "http://localhost:5055/api"


def advanced_search(notebook_id, query):
    """Perform filtered semantic search and get AI answers."""

    # Get sources from a specific notebook
    sources = requests.get(f"{BASE_URL}/sources", params={
        "notebook_id": notebook_id
    }).json()
    source_ids = [s["id"] for s in sources]

    # Vector search restricted to notebook sources
    results = requests.post(f"{BASE_URL}/search", json={
        "query": query,
        "search_type": "vector",
        "limit": 10,
        "source_ids": source_ids,
        "min_similarity": 0.75,
    }).json()

    print(f"Found {results['total']} results:")
    for result in results["results"]:
        print(f"  - {result.get('title', 'Untitled')} "
              f"(similarity: {result.get('similarity', 'N/A')})")

    # Get an AI-powered answer
    answer = requests.post(f"{BASE_URL}/search/ask/simple", json={
        "query": query,
    }).json()
    print(f"\nAI Answer: {answer['response']}")


if __name__ == "__main__":
    advanced_search("notebook:abc123", "CRISPR gene editing efficiency")
```

## Model Management

```python
import requests

BASE_URL = "http://localhost:5055/api"


def setup_ai_models():
    """Configure AI models for Open Notebook."""

    # Check available providers
    providers = requests.get(f"{BASE_URL}/models/providers").json()
    print(f"Available providers: {providers}")

    # Discover models from a provider
    discovered = requests.get(
        f"{BASE_URL}/models/discover/openai"
    ).json()
    print(f"Discovered {len(discovered)} OpenAI models")

    # Sync models to make them available
    requests.post(f"{BASE_URL}/models/sync/openai")

    # Auto-assign default models
    requests.post(f"{BASE_URL}/models/auto-assign")

    # Check current defaults
    defaults = requests.get(f"{BASE_URL}/models/defaults").json()
    print(f"Default models: {defaults}")


if __name__ == "__main__":
    setup_ai_models()
```

### `scripts/chat_interaction.py`

```python
"""
Open Notebook - Chat Interaction Example

Demonstrates creating chat sessions, sending messages with context,
and searching across research materials.

Prerequisites:
    uv pip install requests

Usage:
    export OPEN_NOTEBOOK_URL="http://localhost:5055"
    python chat_interaction.py
"""

import os
import requests

BASE_URL = os.getenv("OPEN_NOTEBOOK_URL", "http://localhost:5055") + "/api"


def create_chat_session(notebook_id, title, model_override=None):
    """Create a new chat session within a notebook."""
    payload = {
        "notebook_id": notebook_id,
        "title": title,
    }
    if model_override:
        payload["model_override"] = model_override
    response = requests.post(f"{BASE_URL}/chat/sessions", json=payload)
    response.raise_for_status()
    session = response.json()
    print(f"Created chat session: {session['id']} - {title}")
    return session


def list_chat_sessions(notebook_id):
    """List all chat sessions for a notebook."""
    response = requests.get(
        f"{BASE_URL}/chat/sessions",
        params={"notebook_id": notebook_id},
    )
    response.raise_for_status()
    sessions = response.json()
    print(f"Found {len(sessions)} chat session(s):")
    for s in sessions:
        print(f"  - {s['id']}: {s.get('title', 'Untitled')} "
              f"({s.get('message_count', 0)} messages)")
    return sessions


def send_chat_message(session_id, message, include_sources=True,
                      include_notes=True, model_override=None):
    """Send a message to a chat session with context from sources and notes."""
    payload = {
        "session_id": session_id,
        "message": message,
        "context": {
            "include_sources": include_sources,
            "include_notes": include_notes,
        },
    }
    if model_override:
        payload["model_override"] = model_override
    response = requests.post(f"{BASE_URL}/chat/execute", json=payload)
    response.raise_for_status()
    result = response.json()
    print(f"\nUser: {message}")
    print(f"AI: {result.get('response', result)}")
    return result


def get_session_history(session_id):
    """Retrieve full message history for a chat session."""
    response = requests.get(f"{BASE_URL}/chat/sessions/{session_id}")
    response.raise_for_status()
    session = response.json()
    messages = session.get("messages", [])
    print(f"\n--- Session History ({len(messages)} messages) ---")
    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        print(f"[{role}]: {content[:200]}...")
    return session


def build_context(notebook_id, source_ids=None, note_ids=None):
    """Build context data from sources and notes for inspection."""
    payload = {"notebook_id": notebook_id}
    if source_ids:
        payload["source_ids"] = source_ids
    if note_ids:
        payload["note_ids"] = note_ids
    response = requests.post(f"{BASE_URL}/chat/context", json=payload)
    response.raise_for_status()
    context = response.json()
    print(f"Context built: {context.get('token_count', '?')} tokens, "
          f"{context.get('char_count', '?')} characters")
    return context


def search_knowledge_base(query, search_type="vector", limit=5):
    """Search across all materials in the knowledge base."""
    response = requests.post(f"{BASE_URL}/search", json={
        "query": query,
        "search_type": search_type,
        "limit": limit,
    })
    response.raise_for_status()
    results = response.json()
    print(f"\nSearch results for '{query}' ({results.get('total', 0)} hits):")
    for r in results.get("results", []):
        title = r.get("title", "Untitled")
        similarity = r.get("similarity", "N/A")
        print(f"  - {title} (similarity: {similarity})")
    return results


def ask_question(query):
    """Ask a question and get an AI-generated answer from the knowledge base."""
    response = requests.post(f"{BASE_URL}/search/ask/simple", json={
        "query": query,
    })
    response.raise_for_status()
    result = response.json()
    print(f"\nQ: {query}")
    print(f"A: {result.get('response', result)}")
    return result


def delete_chat_session(session_id):
    """Delete a chat session."""
    response = requests.delete(f"{BASE_URL}/chat/sessions/{session_id}")
    response.raise_for_status()
    print(f"Deleted chat session: {session_id}")


if __name__ == "__main__":
    print("=== Chat Interaction Demo ===\n")

    # Create a notebook with some content first
    notebook = requests.post(f"{BASE_URL}/notebooks", json={
        "name": "Chat Demo",
        "description": "Demonstrating chat interactions",
    }).json()
    notebook_id = notebook["id"]

    # Add a text source for context
    requests.post(f"{BASE_URL}/sources", data={
        "text": (
            "Immunotherapy has revolutionized cancer treatment. "
            "Checkpoint inhibitors targeting PD-1 and PD-L1 have shown "
            "remarkable efficacy in non-small cell lung cancer, melanoma, "
            "and several other tumor types. Tumor mutational burden (TMB) "
            "has emerged as a key biomarker for predicting response to "
            "immunotherapy. Patients with high TMB tend to generate more "
            "neoantigens, making their tumors more visible to the immune system."
        ),
        "notebook_id": notebook_id,
        "process_async": "false",
    })

    # Create a chat session
    session = create_chat_session(notebook_id, "Immunotherapy Discussion")

    # Have a conversation
    print()
    send_chat_message(
        session["id"],
        "What are the main biomarkers for immunotherapy response?",
    )

    send_chat_message(
        session["id"],
        "How does TMB relate to neoantigen load?",
    )

    # View conversation history
    get_session_history(session["id"])

    # Search the knowledge base
    search_knowledge_base("checkpoint inhibitor efficacy")

    # Ask a standalone question
    ask_question("What is the role of PD-L1 in cancer immunotherapy?")

    # Clean up
    print()
    delete_chat_session(session["id"])
    requests.delete(f"{BASE_URL}/notebooks/{notebook_id}")
    print("Cleanup complete")
```

### `scripts/notebook_management.py`

```python
"""
Open Notebook - Notebook Management Example

Demonstrates creating, listing, updating, and deleting notebooks
using the Open Notebook REST API.

Prerequisites:
    uv pip install requests

Usage:
    export OPEN_NOTEBOOK_URL="http://localhost:5055"
    python notebook_management.py
"""

import os
import requests

BASE_URL = os.getenv("OPEN_NOTEBOOK_URL", "http://localhost:5055") + "/api"


def create_notebook(name, description=""):
    """Create a new notebook."""
    response = requests.post(f"{BASE_URL}/notebooks", json={
        "name": name,
        "description": description,
    })
    response.raise_for_status()
    notebook = response.json()
    print(f"Created notebook: {notebook['id']} - {notebook['name']}")
    return notebook


def list_notebooks(archived=False):
    """List all notebooks, optionally filtering by archived status."""
    response = requests.get(f"{BASE_URL}/notebooks", params={
        "archived": archived,
    })
    response.raise_for_status()
    notebooks = response.json()
    print(f"Found {len(notebooks)} notebook(s):")
    for nb in notebooks:
        print(f"  - {nb['id']}: {nb['name']} "
              f"(sources: {nb.get('source_count', 0)}, "
              f"notes: {nb.get('note_count', 0)})")
    return notebooks


def get_notebook(notebook_id):
    """Retrieve a single notebook by ID."""
    response = requests.get(f"{BASE_URL}/notebooks/{notebook_id}")
    response.raise_for_status()
    return response.json()


def update_notebook(notebook_id, name=None, description=None, archived=None):
    """Update notebook fields."""
    payload = {}
    if name is not None:
        payload["name"] = name
    if description is not None:
        payload["description"] = description
    if archived is not None:
        payload["archived"] = archived
    response = requests.put(
        f"{BASE_URL}/notebooks/{notebook_id}", json=payload
    )
    response.raise_for_status()
    updated = response.json()
    print(f"Updated notebook: {updated['id']} - {updated['name']}")
    return updated


def delete_notebook(notebook_id, delete_sources=False):
    """Delete a notebook and optionally its exclusive sources."""
    # Preview what will be deleted
    preview = requests.get(
        f"{BASE_URL}/notebooks/{notebook_id}/delete-preview"
    ).json()
    print(f"Deletion will affect {preview.get('note_count', 0)} notes "
          f"and {preview.get('source_count', 0)} sources")

    response = requests.delete(
        f"{BASE_URL}/notebooks/{notebook_id}",
        params={"delete_sources": delete_sources},
    )
    response.raise_for_status()
    print(f"Deleted notebook: {notebook_id}")


def link_source_to_notebook(notebook_id, source_id):
    """Associate an existing source with a notebook."""
    response = requests.post(
        f"{BASE_URL}/notebooks/{notebook_id}/sources/{source_id}"
    )
    response.raise_for_status()
    print(f"Linked source {source_id} to notebook {notebook_id}")


def unlink_source_from_notebook(notebook_id, source_id):
    """Remove the association between a source and a notebook."""
    response = requests.delete(
        f"{BASE_URL}/notebooks/{notebook_id}/sources/{source_id}"
    )
    response.raise_for_status()
    print(f"Unlinked source {source_id} from notebook {notebook_id}")


if __name__ == "__main__":
    # Demo workflow
    print("=== Notebook Management Demo ===\n")

    # Create notebooks
    nb1 = create_notebook(
        "Protein Folding Research",
        "Literature review on AlphaFold and related methods"
    )
    nb2 = create_notebook(
        "CRISPR Gene Editing",
        "Survey of CRISPR-Cas9 applications in therapeutics"
    )

    # List all notebooks
    print()
    list_notebooks()

    # Update a notebook
    print()
    update_notebook(nb1["id"], description="Updated: Including ESMFold comparisons")

    # Archive a notebook
    print()
    update_notebook(nb2["id"], archived=True)
    print("\nActive notebooks:")
    list_notebooks(archived=False)

    print("\nArchived notebooks:")
    list_notebooks(archived=True)

    # Clean up
    print()
    delete_notebook(nb1["id"])
    delete_notebook(nb2["id"])
```

### `scripts/source_ingestion.py`

```python
"""
Open Notebook - Source Ingestion Example

Demonstrates ingesting various content types (URLs, files, text) into
Open Notebook and monitoring processing status.

Prerequisites:
    uv pip install requests

Usage:
    export OPEN_NOTEBOOK_URL="http://localhost:5055"
    python source_ingestion.py
"""

import os
import time
import requests

BASE_URL = os.getenv("OPEN_NOTEBOOK_URL", "http://localhost:5055") + "/api"


def add_url_source(notebook_id, url, process_async=True):
    """Add a web URL as a source to a notebook."""
    response = requests.post(f"{BASE_URL}/sources", data={
        "url": url,
        "notebook_id": notebook_id,
        "process_async": str(process_async).lower(),
    })
    response.raise_for_status()
    source = response.json()
    print(f"Added URL source: {source['id']} - {url}")
    return source


def add_text_source(notebook_id, title, text):
    """Add raw text as a source."""
    response = requests.post(f"{BASE_URL}/sources", data={
        "text": text,
        "notebook_id": notebook_id,
        "process_async": "false",
    })
    response.raise_for_status()
    source = response.json()
    print(f"Added text source: {source['id']} - {title}")
    return source


def upload_file_source(notebook_id, file_path, process_async=True):
    """Upload a file (PDF, DOCX, audio, video) as a source."""
    filename = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/sources",
            data={
                "notebook_id": notebook_id,
                "process_async": str(process_async).lower(),
            },
            files={"file": (filename, f)},
        )
    response.raise_for_status()
    source = response.json()
    print(f"Uploaded file source: {source['id']} - {filename}")
    return source


def wait_for_processing(source_id, poll_interval=5, timeout=300):
    """Poll source processing status until completion or timeout."""
    elapsed = 0
    while elapsed < timeout:
        response = requests.get(f"{BASE_URL}/sources/{source_id}/status")
        response.raise_for_status()
        status = response.json()
        current_status = status.get("status", "unknown")
        print(f"  Source {source_id}: {current_status}")

        if current_status in ("completed", "failed"):
            return status
        time.sleep(poll_interval)
        elapsed += poll_interval

    print(f"  Source {source_id}: timed out after {timeout}s")
    return None


def list_sources(notebook_id=None, limit=20):
    """List sources, optionally filtered by notebook."""
    params = {"limit": limit}
    if notebook_id:
        params["notebook_id"] = notebook_id
    response = requests.get(f"{BASE_URL}/sources", params=params)
    response.raise_for_status()
    sources = response.json()
    print(f"Found {len(sources)} source(s):")
    for src in sources:
        print(f"  - {src['id']}: {src.get('title', 'Untitled')}")
    return sources


def get_source_insights(source_id):
    """Retrieve AI-generated insights for a source."""
    response = requests.get(f"{BASE_URL}/sources/{source_id}/insights")
    response.raise_for_status()
    return response.json()


def retry_failed_source(source_id):
    """Retry processing for a failed source."""
    response = requests.post(f"{BASE_URL}/sources/{source_id}/retry")
    response.raise_for_status()
    print(f"Retrying source: {source_id}")
    return response.json()


def delete_source(source_id):
    """Delete a source."""
    response = requests.delete(f"{BASE_URL}/sources/{source_id}")
    response.raise_for_status()
    print(f"Deleted source: {source_id}")


if __name__ == "__main__":
    print("=== Source Ingestion Demo ===\n")

    # Create a notebook first
    notebook = requests.post(f"{BASE_URL}/notebooks", json={
        "name": "Source Ingestion Demo",
        "description": "Testing various source types",
    }).json()
    notebook_id = notebook["id"]
    print(f"Created notebook: {notebook_id}\n")

    # Add a URL source
    url_source = add_url_source(
        notebook_id,
        "https://en.wikipedia.org/wiki/CRISPR_gene_editing",
    )

    # Add a text source
    text_source = add_text_source(
        notebook_id,
        "Research Notes",
        "CRISPR-Cas9 is a genome editing tool that allows researchers to "
        "alter DNA sequences and modify gene function. It has transformed "
        "biological research and offers potential for treating genetic diseases.",
    )

    # Wait for async processing
    print("\nWaiting for processing...")
    wait_for_processing(url_source["id"])

    # List all sources in the notebook
    print()
    list_sources(notebook_id)

    # Clean up
    print()
    delete_source(url_source["id"])
    delete_source(text_source["id"])
    requests.delete(f"{BASE_URL}/notebooks/{notebook_id}")
    print("Cleanup complete")
```
