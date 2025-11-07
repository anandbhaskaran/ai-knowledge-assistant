import logging
from typing import List, Dict, Any, Optional

from app.services.retriever import get_query_engine, filter_by_relevance
from app.core.config import settings

# Get logger
logger = logging.getLogger(__name__)

def load_editorial_guidelines() -> str:
    """Load editorial guidelines from file"""
    import os
    guidelines_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data", "guidlines", "editorial-guidelines.md"
    )
    try:
        with open(guidelines_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        logger.warning(f"Editorial guidelines not found at {guidelines_path}")
        return ""

def generate_outline(
    headline: str,
    thesis: str,
    key_facts: List[str] = None,
    suggested_visualization: str = None,
    top_k: Optional[int] = None
) -> Dict[str, Any]:
    """
    Generate an article outline based on a selected idea

    Args:
        headline: Article headline
        thesis: The thesis statement or main argument
        key_facts: Key facts to incorporate in the outline
        suggested_visualization: Suggested data visualization
        top_k: Number of similar documents to retrieve (default: from settings)

    Returns:
        Dictionary containing outline and metadata
    """
    if not headline:
        raise ValueError("Headline cannot be empty")
    if not thesis:
        raise ValueError("Thesis statement cannot be empty")

    if key_facts is None:
        key_facts = []

    # Get query engine with increased top_k for better coverage
    if top_k is None:
        top_k = settings.TOP_K_RESULTS

    # Load editorial guidelines
    editorial_guidelines = load_editorial_guidelines()

    # Import OpenAI LLM
    from llama_index.llms.openai import OpenAI

    # System prompt with editorial guidelines and detailed structure
    system_prompt = f"""
    You are an AI Journalist Assistant. Create a detailed article outline following our editorial guidelines.

    EDITORIAL GUIDELINES:
    {editorial_guidelines}

    ⚠️ CRITICAL RULES - FOLLOW EXACTLY:
    1. ONLY use information from the retrieved source documents provided below
    2. If the retrieved documents do NOT contain sufficient information, respond:
       "Cannot create outline - insufficient relevant sources in knowledge base."
    3. NEVER fabricate statistics, quotes, studies, or sources
    4. NEVER use your general knowledge - ONLY use the retrieved documents
    5. Every fact MUST have a citation in the format [Source filename, Date]
    6. Follow the editorial guidelines for voice, tone, and structure

    Create a detailed markdown outline with:

    ## Headline
    [Use the provided headline or refine it to 60-80 characters following guidelines]

    ## Introduction (100-150 words)
    **Hook:** [Placeholder: Describe what opening hook should accomplish - make it compelling and timely]

    **Context:** [Placeholder: What background reader needs to know. Cite relevant sources]

    **Thesis:** [The provided thesis statement]

    **Why This Matters Now:** [Placeholder: Explain current relevance and stakes]

    ## Body Sections

    ### [Section 1 Heading - Clear and Specific]
    **Key Point:** [Main argument for this section]

    **To Cover:**
    - [Placeholder: Specific point to make with citation to [source, date]]
    - [Placeholder: Supporting evidence from [source, date]]
    - [Placeholder: Example or data point to include]

    **Sources to Use:**
    - [List specific sources with brief note on what information to extract]

    [Repeat structure for 3-5 body sections]

    ## Data Visualization
    [If suggested visualization provided, detail what data to visualize and why]

    ## Conclusion
    **Synthesis:** [Placeholder: How to tie arguments together - don't just restate]

    **Implications:** [Placeholder: What this means going forward]

    **Final Thought:** [Placeholder: Memorable closing that reinforces thesis]

    ## Sources Used
    [List all sources from retrieved documents with brief description of their contribution]

    Format requirements:
    - Use markdown headers (##, ###)
    - Format each citation as [Source filename, Date from metadata]
    - Include specific placeholders that guide the writer
    - Make structure clear and actionable
    - Follow editorial guidelines for clarity and tone
    - Ensure placeholders reference specific sources from retrieved documents

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

        # Build query with article details
        key_facts_text = "\n".join([f"- {fact}" for fact in key_facts]) if key_facts else "None provided"
        viz_text = suggested_visualization if suggested_visualization else "None suggested"

        query = f"""
        Create a detailed article outline for:

        Headline: {headline}
        Thesis: {thesis}

        Key Facts to Incorporate:
        {key_facts_text}

        Suggested Visualization: {viz_text}

        Find all relevant facts and sources from the knowledge base to support this article.
        Prioritize recent, authoritative sources. Include diverse perspectives.
        Build on the key facts provided and expand with additional evidence from sources.
        """

        # Generate outline with attribution plan
        logger.info(f"Generating outline for headline: {headline}")
        response = query_engine.query(query)

        # Filter results by relevance
        filtered_nodes, warning = filter_by_relevance(response.source_nodes)

        # If no relevant sources found, return early with clear message
        if not filtered_nodes:
            logger.warning(f"No relevant sources found for headline: {headline}. {warning}")
            return {
                "headline": headline,
                "thesis": thesis,
                "outline": f"Cannot create outline - insufficient relevant sources in knowledge base. {warning}",
                "source_nodes": [],
                "warning": warning
            }

        # Log quality warning if sources are marginal
        if warning:
            logger.warning(f"Quality warning for headline '{headline}': {warning}")

        # Extract and return outline
        return {
            "headline": headline,
            "thesis": thesis,
            "key_facts": key_facts,
            "suggested_visualization": suggested_visualization,
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