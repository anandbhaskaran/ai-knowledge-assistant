# AI Journalist Assistant (Minimal Version)

A lightweight AI-powered tool to help journalists research topics and draft evidence-backed articles using LlamaIndex and Qdrant.

## Core Features

1. **Article Report Idea Generation**: Given a headline or news topic, the assistant should generate
several article ideas consisting of a concise briefing (~250 words) summarizing key insights and
facts, citing at least three relevant articles from reputable external sources or our own archive.
2. **Outline Generation & Content Expansion**: Given a headline and 3–5 bullet-point notes or key
ideas, the assistant should produce a structured article outline with clear H2 and H3 headings.
3. **Draft Article Generation**: Using the headline and bullet points as input, the assistant should
write a first-draft article of about 1,000–2,000 words. The draft must mimic the publication’s
editorial tone and quality standard, incorporate factual content from the archive and external
sources, and include appropriate citations for any referenced information. A skilled journalist
must be able to finalize the report with minimal changes.

## Simplified Tech Stack

* **Python 3.11+**
* **LlamaIndex**: RAG framework for retrieval and citation
* **Qdrant**: Vector database (local Docker or cloud)
* **FastAPI**: Simple API server
* **OpenAI API**: For embeddings and text generation

## Minimal Setup

### 1. Environment

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install core dependencies
pip install llama-index qdrant-client fastapi uvicorn openai python-dotenv
```

### 2. Configuration

Create `.env` file:

```
OPENAI_API_KEY="your-api-key"
QDRANT_URL="http://localhost:6333"
```

### 3. Vector Database

```bash
# Run local Qdrant with Docker
docker run -p 6333:6333 qdrant/qdrant
```

## Basic Implementation

### Initialize Retriever

```python
# retriever.py
import os
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from dotenv import load_dotenv

load_dotenv()

# Connect to Qdrant
client = QdrantClient(url=os.environ["QDRANT_URL"])
vector_store = QdrantVectorStore(client, collection_name="articles")

# Create vector index
index = VectorStoreIndex.from_vector_store(vector_store)

# Get query engine
query_engine = index.as_query_engine(similarity_top_k=5)
```

### Simple Idea Generator

```python
# ideas.py
from retriever import query_engine

def generate_ideas(topic):
    # System prompt
    system_prompt = """
    You are an AI Journalist Assistant. Generate 3 article ideas about the
    given topic. Each idea should have:
    - A clear thesis statement
    - 3 key facts with citations from retrieved evidence
    - A suggested data visualization

    Always provide sources for your facts. Never invent information.
    """

    # Generate ideas with citations
    response = query_engine.query(
        f"Generate article ideas about: {topic}",
        system_prompt=system_prompt
    )

    return response.response
```

### Minimal API

```python
# api.py
from fastapi import FastAPI
from pydantic import BaseModel
import ideas

app = FastAPI()

class TopicRequest(BaseModel):
    topic: str

@app.post("/ideas")
def generate_ideas(request: TopicRequest):
    return {"ideas": ideas.generate_ideas(request.topic)}

# Run with: uvicorn api:app --reload
```

## Basic Data Ingestion

```python
# ingest.py
import os
import glob
from llama_index.core import SimpleDirectoryReader, Document
from retriever import client, index

def ingest_articles(directory_path):
    # Load documents from directory
    documents = SimpleDirectoryReader(directory_path).load_data()

    # Add metadata
    for doc in documents:
        doc.metadata = {
            "source": doc.metadata.get("file_path", ""),
            "date": "2025-01-01"  # Simple default date
        }

    # Create/update the index
    index.insert_documents(documents)
    print(f"Ingested {len(documents)} documents")

# Usage: ingest_articles("data/articles")
```

## Citation Standards

* Format: `[Source, Title, Date]`
* Minimum: 3 distinct sources per article
* Convert relative dates to exact dates

## Running the Minimal Version

1. Start Qdrant database
2. Ingest sample articles
3. Run the API server
4. Test with a curl request:
   ```
   curl -X POST localhost:8000/ideas -d '{"topic":"renewable energy"}'
   ```

## Future Improvements

* Add outline and draft generation endpoints
* Implement proper chunking strategy
* Add evaluation framework
* Enhance citation tracking