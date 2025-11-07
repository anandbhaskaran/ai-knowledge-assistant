import logging
from typing import List, Dict, Any, Optional

from app.services.retriever import get_query_engine, filter_by_relevance
from app.core.config import settings

# Get logger
logger = logging.getLogger(__name__)

def generate_outline(
    topic: str,
    thesis: str,
    top_k: Optional[int] = None
) -> Dict[str, Any]:
    """
    Generate an article outline based on a topic and thesis

    Args:
        topic: The topic of the article
        thesis: The thesis statement or main argument
        top_k: Number of similar documents to retrieve (default: from settings)

    Returns:
        Dictionary containing outline and metadata
    """
    if not topic:
        raise ValueError("Topic cannot be empty")
    if not thesis:
        raise ValueError("Thesis statement cannot be empty")

    # Get query engine with increased top_k for better coverage
    if top_k is None:
        top_k = settings.TOP_K_RESULTS

    query_engine = get_query_engine(top_k=top_k)

    # System prompt with strict anti-hallucination instructions
    system_prompt = """
    You are an AI Journalist Assistant. Create a detailed outline for an article.

    ⚠️ CRITICAL RULES - FOLLOW EXACTLY:
    1. ONLY use information from the retrieved source documents provided below
    2. If the retrieved documents do NOT contain relevant information about the topic, you MUST respond:
       "I cannot create an outline for this topic. My knowledge base does not contain relevant articles."
    3. NEVER fabricate statistics, quotes, studies, or sources
    4. NEVER use your general knowledge - ONLY use the retrieved documents
    5. Every fact MUST have a citation in the format [Source filename, Date]
    6. If sources are limited, acknowledge this in your outline

    If relevant sources ARE found, create a detailed outline including:

    1. Introduction
       - Hook and context (from sources only)
       - Thesis statement
       - Scope of the article

    2. Main sections (3-5 sections)
       - Key arguments with citations from retrieved sources
       - Subsections with evidence from provided documents
       - Potential quotes or data points (from sources only)

    3. Attribution plan
       - List sources from the retrieved documents
       - Note what evidence exists in the sources

    4. Conclusion structure
       - Key takeaways based on retrieved information

    Format requirements:
    - Format the outline in hierarchical markdown format
    - Format each citation as [Source filename, Date from metadata]
    - Only cite sources that are actually provided below
    - Include sections for relevant data visualizations if supported by sources

    Return your response in markdown format.
    """

    try:
        # Generate query with relevant prompt
        query = f"""
        Create an article outline about: {topic}

        Thesis statement: {thesis}

        Find relevant facts and sources from your knowledge that would help develop
        this outline. Prioritize recent, authoritative sources. Include diverse
        perspectives and incorporate supporting evidence for the thesis.
        """

        # Generate outline with attribution plan
        logger.info(f"Generating outline for topic: {topic}")
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
                "thesis": thesis,
                "outline": f"I cannot create an outline for '{topic}'. {warning}",
                "source_nodes": [],
                "warning": warning
            }

        # Log quality warning if sources are marginal
        if warning:
            logger.warning(f"Quality warning for topic '{topic}': {warning}")

        # Extract and return outline
        return {
            "topic": topic,
            "thesis": thesis,
            "outline": response.response,
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
        logger.error(f"Error generating outline: {e}")
        raise