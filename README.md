# AI Journalist Assistant

A lightweight AI-powered tool to help journalists research topics and draft evidence-backed articles using LlamaIndex and Qdrant.

## Core Features

1. **Idea Generation**: Convert topic into 3-5 evidence-backed article angles
2. **Article Outline**: Agent-based outline with archive + web sources, ranked by relevance
3. **Draft Article**: Generate 1000-2000 word draft with citations

## Tech Stack

* **Python 3.11+**
* **LlamaIndex**: RAG framework with ReActAgent for multi-source retrieval
* **Qdrant**: Vector database for article archive
* **Tavily API**: Real-time web search for current information
* **FastAPI**: API server
* **OpenAI API**: For embeddings and text generation

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/knowledge-assistant.git
cd knowledge-assistant
```

### 2. Set Up Environment

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create or update the `.env` file in the project root:

```bash
# Required API Keys
OPENAI_API_KEY=your-openai-api-key
TAVILY_API_KEY=your-tavily-api-key  # Get free key at https://tavily.com

# Qdrant Configuration
QDRANT_URL=http://localhost:6333  # Or your Qdrant cloud URL
QDRANT_API_KEY=your-qdrant-api-key-if-using-cloud

# Settings
COLLECTION_NAME=articles
TOP_K_RESULTS=5
MIN_RELEVANCE_SCORE=0.75
HIGH_RELEVANCE_THRESHOLD=0.85
```
### 4. Setup with docker (Recomended)
Quick Start

  # 1. Make sure your .env file has the required API keys
  # (Your existing .env file should work fine)

  # 2. Start all services
  docker-compose up -d

  # Or use the startup script
  ./docker-start.sh

  # 3. Access the application
  # Frontend: http://localhost:3000
  # Backend:  http://localhost:8000
  # Qdrant:   http://localhost:6333/dashboard

  Service Architecture

  ┌─────────────────┐
  │   Frontend      │  http://localhost:3000
  │  (React+Nginx)  │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │    Backend      │  http://localhost:8000
  │    (FastAPI)    │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │    Qdrant       │  http://localhost:6333
  │ (Vector Store)  │
  └─────────────────┘

  Key Features

  - Health Checks: All services monitor each other's health
  - Dependency Management: Services start in correct order
  - Persistent Storage: Qdrant data survives container restarts
  - Environment Variables: Loaded from your existing .env file
  - Network Isolation: Services communicate on private bridge network
  - Production Ready: Includes security headers, compression, and optimization

  Common Commands

  # View logs
  docker-compose logs -f

  # Stop services
  docker-compose down

  # Rebuild and restart
  docker-compose up -d --build

  # Ingest articles
  docker-compose exec backend python -m app.services.ingestion data/articles --clear

  All the Docker configuration is now ready! Just run docker-compose up -d to start everything. Check out DOCKER.md for detailed documentation and troubleshooting.

### 4. Set Up Vector Database

#### Option 1: Local Qdrant with Docker

```bash
docker run -d -p 6333:6333 -p 6334:6334 --name qdrant qdrant/qdrant
```

#### Option 2: Qdrant Cloud

Sign up at [Qdrant Cloud](https://cloud.qdrant.io/) and update your `.env` file with the provided URL and API key.

## Usage

### Quick Demo

To quickly try out the core functionality without running the API server, you can use the included demo script:

```bash
# Activate virtual environment if not already done
source .venv/bin/activate

# Run the demo script
python simple_demo.py
```

This will load the sample articles, create an index, and generate article ideas for the topic "renewable energy".

You can also use the clear-and-ingest demo script which demonstrates both clearing data and ingestion:

```bash
python -m app.services.ingestion data/articles --clear
```

### 2. Run the API Server

```bash
uvicorn app.main:app --reload
```

The API will be available at http://127.0.0.1:8000, with interactive documentation at:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

You can use these interfaces to explore and test the API endpoints.

### 3. API Endpoints

#### Generate Article Ideas

```bash
curl -X POST http://127.0.0.1:8000/api/v1/ideas \
  -H "Content-Type: application/json" \
  -d '{"topic": "renewable energy", "num_ideas": 3}'
```

The response will include the generated ideas in markdown format and source information used to generate the ideas.

#### Generate Article Outline

Uses AI agent with archive retrieval + web search to create structured outlines with ranked sources.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/outlines \
  -H "Content-Type: application/json" \
  -d '{
    "headline": "Solar Energy Transforms Rural Communities",
    "thesis": "Solar energy adoption is accelerating in rural communities due to decreasing costs and policy incentives",
    "key_facts": [
      "Solar panel costs dropped 90% since 2010",
      "Rural solar installations increased 150% in 2023"
    ],
    "suggested_visualization": "Map showing rural solar adoption rates"
  }'
```

**Returns:**
- Structured markdown outline with H2/H3 headings
- Ranked sources from archive (Qdrant) and web (Tavily)
- Each source includes: title, source, source_type ('archive'/'web'), date, URL, relevance_score, excerpt
- Editorial guidelines compliance

#### Generate Draft Article

```bash
curl -X POST http://127.0.0.1:8000/api/v1/drafts \
  -H "Content-Type: application/json" \
  -d '{"topic": "renewable energy", "outline": "1. Introduction\n2. Current State of Solar\n3. Rural Adoption Trends\n4. Cost Analysis\n5. Policy Incentives\n6. Conclusion", "word_count": 1500}'
```

Note: The draft endpoint is implemented but may need updating to use the latest LlamaIndex APIs.

## Citation Standards

* Format: `[Source, Title, Date]`
* Minimum: 3 distinct sources per article
* Convert relative dates to exact dates

## Development

### Project Structure

```
knowledge-assistant/
├── app/
│   ├── api/
│   │   └── endpoints/
│   │       ├── ideas.py
│   │       ├── outline.py         # Agent-based outline generation
│   │       └── draft.py
│   ├── core/
│   │   ├── config.py              # Settings with TAVILY_API_KEY
│   │   └── logging.py
│   ├── models/
│   │   └── schemas.py             # Source with source_type field
│   ├── services/
│   │   ├── retriever.py           # Archive retrieval from Qdrant
│   │   ├── tools.py               # Archive + web search tools
│   │   ├── outline_agent.py       # ReActAgent for outline generation
│   │   ├── ingestion.py
│   │   ├── ideas.py
│   │   ├── outline.py             # Legacy (can be removed)
│   │   └── draft.py
│   └── main.py
├── data/
│   ├── articles/                  # Article archive
│   └── guidlines/
│       └── editorial-guidelines.md
├── tests/
├── .env
├── requirements.txt
└── README.md
```

## Enhanced Metadata

The system automatically extracts rich metadata from article content during ingestion, improving retrieval quality and relevance:

### Metadata Attributes

* **Basic Information**: File details, title, date
* **Content Analysis**:
  - Sections extracted from headings
  - Keywords extracted from frequency analysis
  - Entities detected (organizations, years, percentages)
* **Statistical Information**: Content length, section count

This rich metadata enables better article retrieval, more precise citations, and improved contextual understanding by the AI.

## Key Implementation Details

### Agent-Based Outline Generation
- Uses LlamaIndex ReActAgent to intelligently combine multiple data sources
- Archive retrieval tool searches Qdrant vector database for historical context
- Web search tool uses Tavily API for real-time information
- All sources ranked by relevance score (0-1) and tagged with source_type
- Follows editorial guidelines from `data/guidlines/editorial-guidelines.md`

### Source Classification
Each source includes:
- `source_type`: 'archive' or 'web'
- `relevance_score`: Vector similarity (archive) or search relevance (web)
- Complete metadata: title, source, date, URL, text excerpt

## Future Improvements
* Implement proper chunking strategies for different document types
* Add evaluation framework for generated content
* Enhance citation tracking and verification
* Expand metadata extraction with NER models
* Add more specialized tools (e.g., fact-checking, expert databases)

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Built with ❤️ using LlamaIndex and Qdrant.