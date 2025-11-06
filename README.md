# AI Journalist Assistant

A lightweight AI-powered tool to help journalists research topics and draft evidence-backed articles using LlamaIndex and Qdrant.

## Core Features

1. **Idea Generation**: Convert topic into 3-5 evidence-backed article angles
2. **Article Outline**: Create structured outline with attribution plan
3. **Draft Article**: Generate 1000-2000 word draft with citations

## Tech Stack

* **Python 3.11+**
* **LlamaIndex**: RAG framework for retrieval and citation
* **Qdrant**: Vector database (local Docker or cloud)
* **FastAPI**: Simple API server
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

```
OPENAI_API_KEY=your-openai-api-key
QDRANT_URL=http://localhost:6333  # Or your Qdrant cloud URL
QDRANT_API_KEY=your-qdrant-api-key-if-using-cloud
COLLECTION_NAME=articles
TOP_K_RESULTS=5
```

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
python clear_and_ingest_demo.py
```

### 1. Ingest Articles

Before generating content, you need to ingest articles into the vector database:

```bash
# Create a data directory with articles (txt, md, pdf, etc.)
mkdir -p data/articles
# Add your articles to the data/articles directory

# Run the ingestion script (appends to existing data)
python -c "from app.services.ingestion import ingest_articles; ingest_articles('data/articles')"

# Run the ingestion script with clearing existing data (default behavior you want)
python -c "from app.services.ingestion import ingest_articles; ingest_articles('data/articles', clear_data=True)"

# Alternatively, use the ingestion module directly with --clear flag
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

```bash
curl -X POST http://127.0.0.1:8000/api/v1/outlines \
  -H "Content-Type: application/json" \
  -d '{"topic": "renewable energy", "thesis": "Solar energy adoption is accelerating in rural communities due to decreasing costs and policy incentives"}'
```

Note: The outline endpoint is implemented but may need updating to use the latest LlamaIndex APIs.

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
│   │       ├── outline.py
│   │       └── draft.py
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   ├── models/
│   │   └── schemas.py
│   ├── services/
│   │   ├── retriever.py
│   │   ├── ingestion.py
│   │   ├── ideas.py
│   │   ├── outline.py
│   │   └── draft.py
│   └── main.py
├── data/
│   └── articles/
├── tests/
├── .env
├── requirements.txt
└── README.md
```

### Running Tests

```bash
pytest
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

## Future Improvements

* Add a web UI for journalists
* Implement proper chunking strategies for different document types
* Add evaluation framework for generated content
* Enhance citation tracking and verification
* Connect to external sources (news APIs, research databases)
* Expand metadata extraction with NER models

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Built with ❤️ using LlamaIndex and Qdrant.