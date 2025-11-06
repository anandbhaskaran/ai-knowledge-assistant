"""
Test script to verify enhanced metadata extraction and retrieval.
"""
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import required LlamaIndex components
from llama_index.core import VectorStoreIndex
from llama_index.core.settings import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

# Import retriever
from app.services.retriever import get_global_index, get_query_engine
from llama_index.llms.openai import OpenAI

def print_node_metadata(node, indent=""):
    """Print node metadata in a readable format"""
    print(f"{indent}Source: {node.metadata.get('source')}")
    print(f"{indent}Title: {node.metadata.get('title')}")

    # Print enhanced metadata
    sections = node.metadata.get('sections', [])
    if sections:
        print(f"{indent}Sections: {', '.join(sections[:3])}{'...' if len(sections) > 3 else ''}")

    keywords = node.metadata.get('keywords', [])
    if keywords:
        print(f"{indent}Keywords: {', '.join(keywords[:5])}{'...' if len(keywords) > 5 else ''}")

    orgs = node.metadata.get('organizations', [])
    if orgs:
        print(f"{indent}Organizations: {', '.join(orgs[:3])}{'...' if len(orgs) > 3 else ''}")

    years = node.metadata.get('years_mentioned', [])
    if years:
        print(f"{indent}Years: {', '.join(years[:5])}{'...' if len(years) > 5 else ''}")

    # Print a sample of text
    text = node.get_text()
    preview = text[:150] + "..." if len(text) > 150 else text
    print(f"{indent}Text preview: {preview.replace(chr(10), ' ')}")
    print()

def main():
    """Test enhanced metadata"""
    print("\n===== TESTING ENHANCED METADATA =====\n")

    # Set OpenAI API key
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

    # Get the global index
    index = get_global_index()
    print(f"Successfully connected to index")

    # Run a test query with a system prompt that mentions metadata
    system_prompt = """
    You are an AI Journalist Assistant. Generate 1 article idea about the
    given topic. Each idea should have:

    1. A compelling headline
    2. A clear thesis statement (1-2 sentences)
    3. 3 key facts with citations from retrieved evidence, including years and percentages when available
    4. A suggested data visualization

    Format requirements:
    - Format each idea as a separate section with a clear headline
    - Format each citation as [Source, Title, Date]
    - Include specific years and statistics from the metadata when available
    - Always provide sources for your facts
    - Never invent information

    Return your response in markdown format.
    """

    # Create OpenAI LLM with system prompt
    llm = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        temperature=0.7,
        system_prompt=system_prompt
    )

    # Test topics
    topics = [
        "renewable energy trends",
        "climate change impacts",
        "sustainable farming methods"
    ]

    for topic in topics:
        print(f"\n--- Query: '{topic}' ---")

        # Get query engine
        query_engine = get_query_engine(top_k=2, llm=llm)

        # Execute query
        query = f"Generate evidence-based article ideas about: {topic}"
        response = query_engine.query(query)

        # Print source nodes and their metadata
        print("\nSource nodes used:")
        for i, node in enumerate(response.source_nodes):
            print(f"Node {i+1}:")
            print_node_metadata(node.node)

        # Print the response
        print("\nGenerated response:")
        print("-" * 50)
        print(response.response)
        print("-" * 50)
        print("\n")

if __name__ == "__main__":
    main()