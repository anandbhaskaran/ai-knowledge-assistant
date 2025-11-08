# AI Journalist Assistant

A lightweight AI-powered tool to help journalists research topics and draft evidence-backed articles using LlamaIndex, Qdrant, and Tavily.

## Core Features

1. **Article Idea Generation**: Generate 3-5 evidence-backed article angles with citations from archive sources
2. **Outline Generation (Agent-Based)**: AI agent combines archive + web sources to create structured outlines with H2/H3 headings, ranked sources, and editorial guidelines compliance
3. **Draft Article Generation**: Generate 1,000-2,000 word drafts with proper citations and editorial tone

## Tech Stack

* **Python 3.11+**
* **LlamaIndex**: RAG framework with ReActAgent for multi-source retrieval
* **Qdrant**: Vector database for article archive
* **Tavily API**: Real-time web search for current information
* **FastAPI**: API server
* **OpenAI API**: For embeddings and text generation

## Minimal Setup

### 1. Environment

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create `.env` file:

```bash
# Required API Keys
OPENAI_API_KEY="your-openai-api-key"
TAVILY_API_KEY="your-tavily-api-key"  # Get free key at https://tavily.com

# Qdrant Configuration
QDRANT_URL="http://localhost:6333"

# Settings
COLLECTION_NAME="articles"
TOP_K_RESULTS=5
MIN_RELEVANCE_SCORE=0.75
```

### 3. Vector Database

```bash
# Run local Qdrant with Docker
docker run -p 6333:6333 qdrant/qdrant
```

## Implementation Overview

### Agent-Based Outline Generation

The outline endpoint uses a **ReActAgent** with two specialized tools:

1. **Archive Retrieval Tool** (`app/services/tools.py`)
   - Searches Qdrant vector database for relevant historical articles
   - Returns sources with relevance scores from vector similarity
   - Tagged as `source_type: 'archive'`

2. **Web Search Tool** (`app/services/tools.py`)
   - Uses Tavily API for real-time web search
   - Returns current information with relevance scores
   - Tagged as `source_type: 'web'`

The agent intelligently combines both sources, ranks them by relevance, and generates structured outlines following editorial guidelines from `data/guidlines/editorial-guidelines.md`.

### Key Files

- `app/services/outline_agent.py`: ReActAgent implementation
- `app/services/tools.py`: Archive + web search tools
- `app/api/endpoints/outline.py`: FastAPI endpoint
- `app/models/schemas.py`: Source model with source_type field

### Data Ingestion

```bash
# Ingest articles into Qdrant
python -m app.services.ingestion data/articles --clear
```

## Usage

### 1. Start Services

```bash
# Start Qdrant (in one terminal)
docker run -p 6333:6333 qdrant/qdrant

# Start API server (in another terminal)
uvicorn app.main:app --reload
```

### 2. Generate Outline

```bash
curl -X POST http://localhost:8000/api/v1/outlines \
  -H "Content-Type: application/json" \
  -d '{
    "headline": "AI Transforms Healthcare Diagnostics",
    "thesis": "AI is revolutionizing medical diagnostics through improved accuracy and efficiency",
    "key_facts": [
      "95% accuracy in cancer detection",
      "50% reduction in diagnosis time"
    ],
    "suggested_visualization": "Chart comparing AI vs traditional diagnostic accuracy"
  }'
```

### 3. Response Format

```json
{
  "headline": "...",
  "thesis": "...",
  "outline": "## Headline\n...\n## Introduction\n...",
  "sources": [
    {
      "title": "AI Diagnostics Study 2024",
      "source": "nature.com",
      "source_type": "web",
      "relevance_score": 0.92,
      "date": "2024-11-01",
      "url": "https://...",
      "text": "..."
    },
    {
      "title": "Healthcare AI Report",
      "source": "Internal Archive",
      "source_type": "archive",
      "relevance_score": 0.87,
      "date": "2024-06-15",
      "url": "https://...",
      "text": "..."
    }
  ],
  "warning": null
}
```

## Citation Standards

* Format: `[Source, Title, Date]`
* Minimum: 3 distinct sources per article
* All sources ranked by relevance score (0-1)
* Each source tagged with source_type ('archive' or 'web')

## Documentation

- **AGENT_OUTLINE.md**: Detailed agent architecture and flow
- **WEB_SEARCH_SETUP.md**: Tavily integration setup guide
- **README.md**: Full installation and usage guide

## Future Improvements

* Implement draft article generation with agent
* Add proper chunking strategy for long documents
* Add evaluation framework for generated content
* Enhance citation tracking and verification
* Add more specialized tools (fact-checking, expert databases)