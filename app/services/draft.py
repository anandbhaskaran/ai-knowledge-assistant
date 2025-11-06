import logging
from typing import List, Dict, Any, Optional

from app.services.retriever import get_query_engine
from app.core.config import settings

# Get logger
logger = logging.getLogger(__name__)

def generate_draft(
    topic: str,
    outline: str,
    word_count: int = 1500,
    top_k: Optional[int] = None
) -> Dict[str, Any]:
    """
    Generate a draft article based on a topic and outline

    Args:
        topic: The topic of the article
        outline: The article outline
        word_count: Target word count (default: 1500)
        top_k: Number of similar documents to retrieve (default: from settings)

    Returns:
        Dictionary containing draft article and metadata
    """
    if not topic:
        raise ValueError("Topic cannot be empty")
    if not outline:
        raise ValueError("Outline cannot be empty")

    # Validate word count
    if word_count < 500:
        word_count = 500
    elif word_count > 2000:
        word_count = 2000

    # Get query engine with increased top_k for better coverage
    if top_k is None:
        top_k = settings.TOP_K_RESULTS * 2  # Double the default for more sources

    query_engine = get_query_engine(top_k=top_k)

    # System prompt
    system_prompt = f"""
    You are an AI Journalist Assistant. Write a {word_count}-word article
    based on the provided topic and outline. Your article should:

    1. Follow the structure in the outline
    2. Include a compelling headline and introduction
    3. Support all claims with evidence from the retrieved sources
    4. Format each citation as [Source, Title, Date]
    5. Include at least 3 distinct sources
    6. Maintain journalistic tone and objectivity
    7. End with a conclusion summarizing key points

    Format requirements:
    - Format the article in markdown
    - Never invent quotes, statistics, or facts
    - Only use information from the retrieved sources and properly cite them
    - Convert relative dates (e.g., "last year") to exact dates
    - Distribute citations throughout the article, not just at the end
    - Aim for approximately {word_count} words

    Return your response in markdown format with citations.
    """

    try:
        # Generate query with relevant prompt
        query = f"""
        Write a {word_count}-word article about: {topic}

        Following this outline:

        {outline}

        Find relevant facts and sources from your knowledge to support the article.
        Prioritize recent, authoritative sources. Include diverse perspectives and
        incorporate supporting evidence for each section of the outline.
        """

        # Generate draft with citations
        logger.info(f"Generating {word_count}-word draft for topic: {topic}")
        response = query_engine.query(
            query,
            system_prompt=system_prompt
        )

        # Extract and return draft
        return {
            "topic": topic,
            "word_count": word_count,
            "outline": outline,
            "draft": response.response,
            "source_nodes": [
                {
                    "text": node.node.get_text(),
                    "metadata": node.node.metadata
                }
                for node in response.source_nodes
            ]
        }
    except Exception as e:
        logger.error(f"Error generating draft: {e}")
        raise