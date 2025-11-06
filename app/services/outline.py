import logging
from typing import List, Dict, Any, Optional

from app.services.retriever import get_query_engine
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

    # System prompt
    system_prompt = """
    You are an AI Journalist Assistant. Create a detailed outline for an
    article with the given topic and thesis. The outline should include:

    1. Introduction
       - Hook and context
       - Thesis statement
       - Scope of the article

    2. Main sections (3-5 sections)
       - Key arguments or points
       - Subsections with evidence needed
       - Potential quotes or data points

    3. Attribution plan
       - List of required sources for each section
       - Types of expertise needed
       - Specific data or research to cite

    4. Conclusion structure
       - Key takeaways
       - Call to action or future implications

    Format requirements:
    - Format the outline in hierarchical markdown format
    - Format each citation as [Source, Title, Date]
    - For each section, suggest specific facts that need attribution
    - Ensure you plan for at least 3 distinct sources across the article
    - Include sections for relevant data visualizations or multimedia elements

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

        # Extract and return outline
        return {
            "topic": topic,
            "thesis": thesis,
            "outline": response.response,
            "source_nodes": [
                {
                    "text": node.node.get_text(),
                    "metadata": node.node.metadata
                }
                for node in response.source_nodes
            ]
        }
    except Exception as e:
        logger.error(f"Error generating outline: {e}")
        raise