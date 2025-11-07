from llama_index.core import VectorStoreIndex
from llama_index.core.settings import Settings as LlamaSettings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from qdrant_client import QdrantClient
from app.core.config import settings
import logging
import os

# Get logger
logger = logging.getLogger(__name__)

# Initialize embedding model
def get_embedding_model():
    """Initialize and return the embedding model"""
    try:
        return OpenAIEmbedding(
            api_key=settings.OPENAI_API_KEY,
            model_name="text-embedding-ada-002"
        )
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI embedding model: {e}")
        raise

# Connect to Qdrant and create vector store
def get_vector_store():
    """Initialize and return the vector store"""
    try:
        client_kwargs = {"url": settings.QDRANT_URL}

        # Add API key if provided
        if settings.QDRANT_API_KEY:
            client_kwargs["api_key"] = settings.QDRANT_API_KEY

        client = QdrantClient(**client_kwargs)

        # Check if collection exists, create if not
        collections = client.get_collections().collections
        collection_names = [collection.name for collection in collections]

        if settings.COLLECTION_NAME not in collection_names:
            logger.info(f"Collection '{settings.COLLECTION_NAME}' not found, it will be created when documents are added")

        vector_store = QdrantVectorStore(
            client=client,
            collection_name=settings.COLLECTION_NAME
        )

        logger.info(f"Connected to Qdrant at {settings.QDRANT_URL}")
        return vector_store
    except Exception as e:
        logger.error(f"Failed to connect to Qdrant: {e}")
        raise

# Create or load vector index
def get_index():
    """Initialize and return the vector index"""
    try:
        embed_model = get_embedding_model()
        # Set the embedding model in global settings
        LlamaSettings._embed_model = embed_model
        vector_store = get_vector_store()

        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store
        )

        logger.info(f"Vector index initialized for collection: {settings.COLLECTION_NAME}")
        return index
    except Exception as e:
        logger.error(f"Failed to initialize vector index: {e}")
        raise

# Create query engine
def get_query_engine(top_k=None, llm=None):
    """Get a query engine with the specified parameters"""
    if top_k is None:
        top_k = settings.TOP_K_RESULTS

    try:
        index = get_index()
        return index.as_query_engine(similarity_top_k=top_k, llm=llm)
    except Exception as e:
        logger.error(f"Failed to create query engine: {e}")
        raise

# Filter results by relevance score
def filter_by_relevance(source_nodes, min_score=None):
    """
    Filter source nodes by relevance score

    Args:
        source_nodes: List of source nodes with scores
        min_score: Minimum relevance score threshold (default: from settings)

    Returns:
        Tuple of (filtered_nodes, quality_warning)
    """
    if min_score is None:
        min_score = settings.MIN_RELEVANCE_SCORE

    if not source_nodes:
        return [], "No sources found in knowledge base"

    # Filter by minimum score
    filtered_nodes = [node for node in source_nodes if getattr(node, 'score', 0) >= min_score]

    # Check quality and generate warnings
    if not filtered_nodes:
        max_score = max([getattr(node, 'score', 0) for node in source_nodes])
        return [], f"No relevant sources found (best match score: {max_score:.2f}, threshold: {min_score:.2f})"

    # Check if best results are below high quality threshold
    best_score = max([getattr(node, 'score', 0) for node in filtered_nodes])
    warning = None

    if best_score < settings.HIGH_RELEVANCE_THRESHOLD:
        warning = f"Limited relevant content found (best score: {best_score:.2f}). Results may be tangential to query."

    return filtered_nodes, warning

# Lazy-loaded global index instance
_index = None

def get_global_index():
    """Get or create the global index instance"""
    global _index
    if _index is None:
        _index = get_index()
    return _index

# Function to clear collection data
def clear_collection():
    """Delete and recreate the collection to clear all data"""
    try:
        client_kwargs = {"url": settings.QDRANT_URL}

        # Add API key if provided
        if settings.QDRANT_API_KEY:
            client_kwargs["api_key"] = settings.QDRANT_API_KEY

        client = QdrantClient(**client_kwargs)

        # Check if collection exists
        collections = client.get_collections().collections
        collection_names = [collection.name for collection in collections]

        if settings.COLLECTION_NAME in collection_names:
            # Delete the collection
            client.delete_collection(collection_name=settings.COLLECTION_NAME)
            logger.info(f"Collection '{settings.COLLECTION_NAME}' deleted")

            # Reset the global index since collection has been deleted
            global _index
            _index = None

            return True
        else:
            logger.info(f"Collection '{settings.COLLECTION_NAME}' does not exist, nothing to clear")
            return False
    except Exception as e:
        logger.error(f"Failed to clear collection: {e}")
        raise