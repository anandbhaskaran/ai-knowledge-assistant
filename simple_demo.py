"""
Simple demo script for the AI Journalist Assistant
"""
import os
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.settings import Settings

# Load environment variables
load_dotenv()

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Load documents
    logger.info("Loading documents from data/articles")
    documents = SimpleDirectoryReader("data/articles").load_data()
    logger.info(f"Loaded {len(documents)} documents")

    # Create embedding model
    embed_model = OpenAIEmbedding(
        api_key=os.environ["OPENAI_API_KEY"],
        model_name="text-embedding-ada-002"
    )

    # Set embedding model in settings
    Settings._embed_model = embed_model

    # Create index from documents
    logger.info("Creating index from documents")
    index = VectorStoreIndex.from_documents(documents)
    logger.info("Index created successfully")

    # Query the index
    topic = "renewable energy"
    logger.info(f"Generating article ideas for topic: {topic}")

    # Create system prompt
    system_prompt = """
    You are an AI Journalist Assistant. Generate 2 article ideas about the
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
    - Make headlines attention-grabbing but factual (not clickbait)

    Return your response in markdown format.
    """

    # Create query
    query = f"Generate evidence-based article ideas about: {topic}"

    # Import OpenAI LLM
    from llama_index.llms.openai import OpenAI

    # Create OpenAI LLM with system prompt
    llm = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        temperature=0.7,
        system_prompt=system_prompt
    )

    # Create query engine with the LLM
    query_engine = index.as_query_engine(llm=llm)

    # Execute query
    response = query_engine.query(query)

    # Print response
    print("\n" + "="*50)
    print(f"ARTICLE IDEAS FOR: {topic.upper()}")
    print("="*50)
    print(response.response)

if __name__ == "__main__":
    main()