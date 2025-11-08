"""
Agent tools for archive retrieval and web search
"""
import logging
from typing import List
from llama_index.core.tools import FunctionTool
from app.services.retriever import get_query_engine, filter_by_relevance

logger = logging.getLogger(__name__)


def archive_retrieval_tool_fn(query: str, top_k: int = 10) -> str:
    """
    Retrieve relevant information from the article archive in Qdrant.

    Args:
        query: The search query to find relevant articles
        top_k: Number of documents to retrieve (default: 10)

    Returns:
        A formatted string containing retrieved articles with metadata and relevance scores
    """
    try:
        logger.info(f"Archive retrieval for query: {query}")

        # Get query engine
        query_engine = get_query_engine(top_k=top_k)

        # Perform retrieval
        response = query_engine.query(query)

        # Filter by relevance
        filtered_nodes, warning = filter_by_relevance(response.source_nodes)

        if not filtered_nodes:
            return f"No relevant articles found in archive. {warning}"

        # Format results
        results = []
        for i, node in enumerate(filtered_nodes, 1):
            metadata = node.node.metadata
            score = getattr(node, 'score', 0)

            result = f"""
Source {i} [Relevance: {score:.3f}]
Title: {metadata.get('title', 'Unknown')}
Source: {metadata.get('source', 'Unknown')}
Date: {metadata.get('date', 'Unknown')}
URL: {metadata.get('url', 'N/A')}

Content:
{node.node.get_text()[:500]}...

---
"""
            results.append(result)

        output = "\n".join(results)
        if warning:
            output = f"WARNING: {warning}\n\n{output}"

        return output

    except Exception as e:
        logger.error(f"Error in archive retrieval: {e}")
        return f"Error retrieving from archive: {str(e)}"


def web_search_tool_fn(query: str, max_results: int = 3) -> str:
    """
    Search the web for recent information on a topic using Tavily API.

    Args:
        query: The search query
        max_results: Maximum number of results to return (default: 3)

    Returns:
        A formatted string containing web search results with URLs and snippets
    """
    try:
        from tavily import TavilyClient
        from app.core.config import settings

        logger.info(f"Web search for query: {query}")

        # Check if API key is configured
        if not settings.TAVILY_API_KEY:
            return "Web search unavailable: TAVILY_API_KEY not configured in environment"

        # Initialize Tavily client
        tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)

        # Perform search
        response = tavily_client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced",  # Use advanced search for better quality
            include_raw_content=False  # Don't include full page content
        )

        # Check if we got results
        if not response.get("results"):
            return f"No web search results found for query: {query}"

        # Format results
        results = []
        for i, result in enumerate(response["results"], 1):
            formatted_result = f"""
Source {i} [Web Search Result]
Title: {result.get('title', 'Unknown')}
URL: {result.get('url', 'N/A')}
Published Date: {result.get('published_date', 'Unknown')}

Content:
{result.get('content', 'No content available')}

Relevance Score: {result.get('score', 'N/A')}

---
"""
            results.append(formatted_result)

        output = f"Found {len(response['results'])} web search results:\n\n" + "\n".join(results)

        # Add answer summary if available
        if response.get("answer"):
            output = f"Summary: {response['answer']}\n\n{output}"

        return output

    except ImportError:
        logger.error("tavily-python package not installed")
        return "Web search unavailable: Please install tavily-python package (pip install tavily-python)"
    except Exception as e:
        logger.error(f"Error in web search: {e}")
        return f"Error performing web search: {str(e)}"


# Create the tools
archive_retrieval_tool = FunctionTool.from_defaults(
    fn=archive_retrieval_tool_fn,
    name="archive_retrieval",
    description="""
    Retrieve relevant articles and information from the internal article archive stored in Qdrant.
    Use this tool to find facts, statistics, quotes, and context from previously published articles.
    Returns articles with relevance scores, metadata (title, source, date, URL), and content excerpts.

    When to use:
    - Finding historical context or background information
    - Looking for previously covered stories on related topics
    - Gathering facts and data from trusted internal sources
    - Finding quotes or expert opinions from past articles

    Parameters:
    - query: Clear, specific search query describing what information you need
    - top_k: Number of results to retrieve (default: 10, higher for broader research)
    """
)

web_search_tool = FunctionTool.from_defaults(
    fn=web_search_tool_fn,
    name="web_search",
    description="""
    Search the web for recent information, breaking news, and external sources using Tavily API.
    Use this tool when archive doesn't have recent or comprehensive information.
    Returns web search results with URLs, titles, content snippets, and relevance scores.

    When to use:
    - Finding very recent developments or breaking news (past few days/weeks)
    - Getting diverse external perspectives and authoritative sources
    - Fact-checking or finding current data and statistics
    - Researching topics not well-covered in archive
    - Finding expert opinions and analysis from reputable publications

    Parameters:
    - query: Clear, specific search query (e.g., "AI healthcare diagnostics 2024", "climate change agriculture impacts")
    - max_results: Number of results to return (default: 3, maximum recommended: 5)

    Returns:
    - Title, URL, published date, content excerpt, and relevance score for each result
    - Summary answer when available
    """
)


def citation_formatter_tool_fn(source_name: str, source_title: str, date: str) -> str:
    """
    Format citation in standard [Source, Title, Date] format.

    Args:
        source_name: Name of the source/publication
        source_title: Title of the article/document
        date: Publication date

    Returns:
        Properly formatted citation string
    """
    try:
        logger.info(f"Formatting citation: {source_name}, {source_title}, {date}")
        return f"[{source_name}, {source_title}, {date}]"
    except Exception as e:
        logger.error(f"Error formatting citation: {e}")
        return f"[{source_name}, {source_title}, {date}]"


# Create citation formatter tool
citation_formatter_tool = FunctionTool.from_defaults(
    fn=citation_formatter_tool_fn,
    name="citation_formatter",
    description="""
    Format citations in the standard format: [Source, Title, Date]

    Use this tool to ensure all citations follow the publication's citation standard.
    Every factual claim, statistic, or quote in the article MUST have a properly formatted citation.

    Parameters:
    - source_name: The publication or source name (e.g., "Nature", "The New York Times", "Internal Archive")
    - source_title: The article or document title
    - date: Publication date in format YYYY-MM-DD or readable format

    Returns: Formatted citation string to place inline after the claim

    Example: citation_formatter("Nature", "AI in Healthcare Study", "2024-11-01")
    Returns: "[Nature, AI in Healthcare Study, 2024-11-01]"
    """
)


def get_outline_tools() -> List[FunctionTool]:
    """
    Get the list of tools available for the outline agent

    Returns:
        List of LlamaIndex FunctionTool objects
    """
    return [archive_retrieval_tool, web_search_tool]


def get_draft_tools() -> List[FunctionTool]:
    """
    Get the list of tools available for the draft agent

    Returns:
        List of LlamaIndex FunctionTool objects
    """
    # Only archive retrieval - citations use simple [Source X] format
    return [archive_retrieval_tool]
