import logging
from typing import List, Dict, Any, Optional

from app.services.retriever import get_query_engine, filter_by_relevance
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

    # System prompt with strict anti-hallucination instructions
    system_prompt = f"""
    You are an AI Journalist Assistant. Write a {word_count}-word article based on the topic and outline.

    ⚠️ CRITICAL RULES - FOLLOW EXACTLY:
    1. ONLY use information from the retrieved source documents provided below
    2. If the retrieved documents do NOT contain sufficient information, you MUST respond:
       "I cannot write a complete article on this topic. My knowledge base does not contain sufficient relevant articles."
    3. NEVER fabricate quotes, statistics, studies, or sources
    4. NEVER use your general knowledge - ONLY use the retrieved documents
    5. Every fact, statistic, and claim MUST have a citation in the format [Source filename, Date]
    6. If you cannot support a section with retrieved sources, acknowledge this clearly

    If sufficient relevant sources ARE found, write an article that:

    1. Follows the structure in the outline
    2. Includes a compelling headline and introduction
    3. Supports ALL claims with evidence from retrieved sources only
    4. Includes at least 3 distinct sources (if available)
    5. Maintains journalistic tone and objectivity
    6. Ends with a conclusion summarizing key points from sources

    Format requirements:
    - Format the article in markdown
    - Format each citation as [Source filename, Date from metadata]
    - Only cite sources that are actually provided below
    - Convert relative dates to exact dates only if that information exists in sources
    - Distribute citations throughout the article
    - Aim for approximately {word_count} words
    - If sources are insufficient for full article, write what you can and note limitations

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

        # Filter results by relevance
        filtered_nodes, warning = filter_by_relevance(response.source_nodes)

        # If no relevant sources found, return early with clear message
        if not filtered_nodes:
            logger.warning(f"No relevant sources found for topic: {topic}. {warning}")
            return {
                "topic": topic,
                "word_count": word_count,
                "outline": outline,
                "draft": f"I cannot write an article on '{topic}'. {warning}",
                "source_nodes": [],
                "warning": warning
            }

        # Log quality warning if sources are marginal
        if warning:
            logger.warning(f"Quality warning for topic '{topic}': {warning}")

        # Extract and return draft
        return {
            "topic": topic,
            "word_count": word_count,
            "outline": outline,
            "draft": response.response,
            "source_nodes": [
                {
                    "text": node.node.get_text(),
                    "metadata": node.node.metadata,
                    "relevance_score": getattr(node, 'score', None)
                }
                for node in filtered_nodes
            ],
            "warning": warning
        }
    except Exception as e:
        logger.error(f"Error generating draft: {e}")
        raise