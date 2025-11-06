import os
import sys
from dotenv import load_dotenv
from typing import List

# Load environment variables
load_dotenv()

# Import required packages
from llama_index.core import VectorStoreIndex, Document, SimpleDirectoryReader
from llama_index.core.settings import Settings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from qdrant_client import QdrantClient

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_documents(directory_path: str) -> List[Document]:
    """Load documents from a directory"""
    logger.info(f"Loading documents from {directory_path}")
    try:
        return SimpleDirectoryReader(directory_path).load_data()
    except Exception as e:
        logger.error(f"Error loading documents: {e}")
        return []

def setup_vector_store():
    """Setup the vector store and index"""
    # Get Qdrant URL from environment or use default
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    collection_name = os.getenv("COLLECTION_NAME", "articles")

    # Connect to Qdrant
    client_kwargs = {"url": qdrant_url}
    if qdrant_api_key:
        client_kwargs["api_key"] = qdrant_api_key

    client = QdrantClient(**client_kwargs)
    logger.info(f"Connected to Qdrant at {qdrant_url}")

    # Create vector store
    vector_store = QdrantVectorStore(
        client=client,
        collection_name=collection_name
    )

    # Setup embedding model
    embed_model = OpenAIEmbedding(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name="text-embedding-ada-002"
    )

    # Create settings with embedding model
    llama_settings = Settings(_embed_model=embed_model)

    return vector_store, llama_settings

def ingest_documents(documents, vector_store, settings):
    """Ingest documents into the vector store"""
    # Create index
    index = VectorStoreIndex.from_documents(
        documents,
        settings=settings,
        vector_store=vector_store,
        show_progress=True
    )
    logger.info(f"Indexed {len(documents)} documents")
    return index

def generate_ideas(index, topic: str, num_ideas: int = 3):
    """Generate article ideas based on a topic"""
    # System prompt
    system_prompt = f"""
    You are an AI Journalist Assistant. Generate {num_ideas} article ideas about the
    given topic. Each idea should have:

    1. A compelling headline
    2. A clear thesis statement (1-2 sentences)
    3. 3 key facts with citations from retrieved evidence
    4. A suggested data visualization

    Format requirements:
    - Format each idea as a separate section with a clear headline
    - Format each citation as [Source, Title, Date]
    - Always provide sources for your facts
    - Never invent information
    - Ensure you use at least 3 distinct sources across all ideas
    - Make headlines attention-grabbing but factual (not clickbait)

    Return your response in markdown format.
    """

    # Generate query with relevant prompt
    query = f"""
    I need {num_ideas} evidence-based article ideas about: {topic}

    Find relevant facts and sources from your knowledge that would help develop
    these ideas. Prioritize recent, authoritative sources. Include diverse
    perspectives and interesting angles.
    """

    # Create query engine
    query_engine = index.as_query_engine(similarity_top_k=5)

    # Generate ideas
    logger.info(f"Generating {num_ideas} ideas for topic: {topic}")
    response = query_engine.query(
        query,
        system_prompt=system_prompt
    )

    return response.response

def main():
    """Main function"""
    # Load documents
    documents = load_documents("data/articles")
    if not documents:
        logger.error("No documents found")
        return

    # Setup vector store
    vector_store, settings = setup_vector_store()

    # Ingest documents
    index = ingest_documents(documents, vector_store, settings)

    # Generate ideas
    topic = "renewable energy"
    ideas = generate_ideas(index, topic, num_ideas=2)

    # Print ideas
    print("\n\n" + "=" * 50)
    print(f"ARTICLE IDEAS FOR: {topic.upper()}")
    print("=" * 50)
    print(ideas)

if __name__ == "__main__":
    main()