"""
Agent-based outline generation using archive retrieval and web search tools
"""
import logging
from typing import List, Dict, Any
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from app.services.tools import get_outline_tools, archive_retrieval_tool_fn
from app.core.config import settings
import re

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


def extract_sources_from_tool_output(tool_output: str, source_type: str = "archive") -> List[Dict[str, Any]]:
    """
    Extract source information from tool output and return as structured list

    Args:
        tool_output: Raw output from archive retrieval or web search tool
        source_type: Type of source ("archive" or "web")

    Returns:
        List of source dictionaries with metadata and relevance scores
    """
    sources = []

    # Split by separator
    source_blocks = tool_output.split("---")

    for block in source_blocks:
        if not block.strip():
            continue

        # Extract relevance score
        # Try different patterns for archive vs web sources
        # Archive format: [Relevance: 0.850]
        # Web format: Relevance Score: 0.92
        relevance_match = re.search(r'\[Relevance:\s*([\d.]+)\]', block)
        if not relevance_match:
            relevance_match = re.search(r'Relevance Score:\s*([\d.]+)', block)
        if not relevance_match:
            relevance_match = re.search(r'Relevance:\s*([\d.]+)', block, re.IGNORECASE)

        relevance_score = float(relevance_match.group(1)) if relevance_match else None

        # Extract metadata
        title_match = re.search(r'Title:\s*(.+)', block)

        # For archive sources, extract from "Source:" field
        # For web sources, derive from domain or use "Web"
        source_match = re.search(r'Source:\s*(.+)', block)

        # Date can be "Date:" or "Published Date:"
        date_match = re.search(r'(?:Published )?Date:\s*(.+)', block)

        url_match = re.search(r'URL:\s*(.+)', block)

        # Extract content
        content_match = re.search(r'Content:\s*(.+?)(?:Relevance|---|\Z)', block, re.DOTALL | re.IGNORECASE)

        # Determine source name
        if source_match:
            source_name = source_match.group(1).strip()
        elif url_match and source_type == "web":
            # Extract domain from URL for web sources
            url_str = url_match.group(1).strip()
            domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url_str)
            source_name = domain_match.group(1) if domain_match else "Web"
        else:
            source_name = "Archive" if source_type == "archive" else "Web"

        source = {
            "title": title_match.group(1).strip() if title_match else "Unknown",
            "source": source_name,
            "source_type": source_type,  # 'archive' or 'web'
            "date": date_match.group(1).strip() if date_match else "Unknown",
            "url": url_match.group(1).strip() if url_match else "N/A",
            "relevance_score": relevance_score,
            "text": content_match.group(1).strip() if content_match else ""
        }

        if source["title"] != "Unknown" or source["text"]:
            sources.append(source)

    # Sort by relevance score (descending)
    sources.sort(key=lambda x: x.get("relevance_score") or 0, reverse=True)

    return sources


def generate_outline_with_agent(
    headline: str,
    thesis: str,
    key_facts: List[str] = None,
    suggested_visualization: str = None
) -> Dict[str, Any]:
    """
    Generate an article outline using an agent with archive and web search tools

    Args:
        headline: Article headline
        thesis: The thesis statement or main argument
        key_facts: Key facts to incorporate in the outline
        suggested_visualization: Suggested data visualization

    Returns:
        Dictionary containing outline, sources, and metadata
    """
    if not headline:
        raise ValueError("Headline cannot be empty")
    if not thesis:
        raise ValueError("Thesis statement cannot be empty")

    if key_facts is None:
        key_facts = []

    # Load editorial guidelines
    editorial_guidelines = load_editorial_guidelines()

    # Create LLM
    llm = OpenAI(
        api_key=settings.OPENAI_API_KEY,
        model="gpt-4",
        temperature=0.7
    )

    # Get tools
    tools = get_outline_tools()

    # Create agent
    agent = ReActAgent.from_tools(
        tools=tools,
        llm=llm,
        verbose=True,
        max_iterations=10
    )

    # Build prompt
    key_facts_text = "\n".join([f"- {fact}" for fact in key_facts]) if key_facts else "None provided"
    viz_text = suggested_visualization if suggested_visualization else "None suggested"

    agent_prompt = f"""
You are an AI Journalist Assistant creating a detailed article outline. Follow the editorial guidelines strictly.

EDITORIAL GUIDELINES:
{editorial_guidelines}

ARTICLE DETAILS:
- Headline: {headline}
- Thesis: {thesis}
- Key Facts to Incorporate:
{key_facts_text}
- Suggested Visualization: {viz_text}

YOUR TASK:
1. Use the archive_retrieval tool to find relevant articles and information from our archive
   - Search for background context on this topic
   - Find supporting facts, statistics, and quotes
   - Look for expert opinions and analysis
   - Retrieve multiple perspectives

2. Use the web_search tool for very recent information and external perspectives
   - Find breaking news and recent developments
   - Get diverse viewpoints from authoritative sources
   - Gather current statistics and data
   - Find expert opinions from reputable publications

3. Based on retrieved sources, create a detailed markdown outline with this structure:

## Headline
[Use the provided headline or refine it to 60-80 characters following guidelines]

## Introduction (100-150 words)
**Hook:** [Describe what opening hook should accomplish - make it compelling and timely]

**Context:** [What background reader needs to know. Cite relevant sources with [Source, Date]]

**Thesis:** {thesis}

**Why This Matters Now:** [Explain current relevance and stakes]

## Body Sections

### [Section 1 Heading - Clear and Specific]
**Key Point:** [Main argument for this section]

**To Cover:**
- [Specific point to make with citation [Source, Title, Date]]
- [Supporting evidence from [Source, Title, Date]]
- [Example or data point to include]

**Sources to Use:**
- [List specific sources with what information to extract]

[Repeat for 3-5 body sections]

## Data Visualization
{viz_text if viz_text != "None suggested" else "[Suggest what data to visualize based on retrieved information]"}

## Conclusion
**Synthesis:** [How to tie arguments together - don't just restate]

**Implications:** [What this means going forward]

**Final Thought:** [Memorable closing that reinforces thesis]

## Sources Used
[List all sources with [Source, Title, Date] and brief description of contribution]

CRITICAL RULES:
- ONLY use information from the retrieved sources - never invent facts
- Every claim must cite a source in format [Source, Title, Date]
- Follow editorial guidelines for voice, tone, and structure
- Make the outline actionable with specific placeholders
- If insufficient sources found, state clearly: "Insufficient sources found in archive"

Begin by using the archive_retrieval tool to gather information.
"""

    try:
        logger.info(f"Generating outline with agent for headline: {headline}")

        # Run agent
        response = agent.chat(agent_prompt)

        # Extract the outline from response
        outline = str(response)

        # Get all sources from tool calls
        # We'll parse the agent's tool call history to extract sources
        all_sources = []

        # Try to directly retrieve from archive to get structured sources
        try:
            from app.services.tools import web_search_tool_fn

            search_query = f"{headline} {thesis}"

            # Get archive sources
            logger.info("Extracting archive sources...")
            archive_output = archive_retrieval_tool_fn(search_query, top_k=10)
            archive_sources = extract_sources_from_tool_output(archive_output, source_type="archive")

            # Get web sources
            logger.info("Extracting web search sources...")
            web_output = web_search_tool_fn(search_query, max_results=5)
            web_sources = extract_sources_from_tool_output(web_output, source_type="web")

            # Combine and rank all sources by relevance score
            all_sources = archive_sources + web_sources
            all_sources.sort(key=lambda x: x.get("relevance_score") or 0, reverse=True)

            logger.info(f"Extracted {len(archive_sources)} archive sources and {len(web_sources)} web sources")

        except Exception as e:
            logger.warning(f"Could not extract structured sources: {e}")

        # Check for warnings in outline
        warning = None
        if "insufficient sources" in outline.lower() or "no relevant" in outline.lower():
            warning = "Limited relevant content found in archive. Consider adding more sources."

        return {
            "headline": headline,
            "thesis": thesis,
            "key_facts": key_facts,
            "suggested_visualization": suggested_visualization,
            "outline": outline,
            "sources": all_sources,
            "warning": warning
        }

    except Exception as e:
        logger.error(f"Error generating outline with agent: {e}")
        raise
