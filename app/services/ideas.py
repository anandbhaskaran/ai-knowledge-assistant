import logging
from typing import List, Dict, Any, Optional

from app.services.retriever import get_query_engine
from app.core.config import settings

# Get logger
logger = logging.getLogger(__name__)

def generate_ideas(
    topic: str,
    num_ideas: int = 3,
    top_k: Optional[int] = None
) -> Dict[str, Any]:
    """
    Generate article ideas for a given topic

    Args:
        topic: The topic to generate ideas for
        num_ideas: Number of ideas to generate (default: 3)
        top_k: Number of similar documents to retrieve (default: from settings)

    Returns:
        Dictionary containing ideas and metadata
    """
    if not topic:
        raise ValueError("Topic cannot be empty")

    # Validate number of ideas
    if num_ideas < 1:
        num_ideas = 3
    elif num_ideas > 5:
        num_ideas = 5

    # Import OpenAI LLM
    from llama_index.llms.openai import OpenAI

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

    try:
        # Create OpenAI LLM with system prompt
        llm = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            temperature=0.7,
            system_prompt=system_prompt
        )

        # Get query engine with the specified LLM
        query_engine = get_query_engine(top_k=top_k, llm=llm)

        # Generate query with relevant prompt
        query = f"""
        I need {num_ideas} evidence-based article ideas about: {topic}

        Find relevant facts and sources from your knowledge that would help develop
        these ideas. Prioritize recent, authoritative sources. Include diverse
        perspectives and interesting angles.
        """

        # Generate ideas with citations
        logger.info(f"Generating {num_ideas} ideas for topic: {topic}")
        response = query_engine.query(query)

        # Extract and return ideas
        return {
            "topic": topic,
            "num_ideas": num_ideas,
            "ideas": response.response,
            "source_nodes": [
                {
                    "text": node.node.get_text(),
                    "metadata": node.node.metadata
                }
                for node in response.source_nodes
            ]
        }
    except Exception as e:
        logger.error(f"Error generating ideas: {e}")
        raise