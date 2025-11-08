"""
Agent-based draft article generation using archive retrieval and citation tools
"""
import logging
from typing import List, Dict, Any, Optional
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from app.services.tools import get_draft_tools
from app.services.draft_validator import (
    count_words,
    validate_editorial_compliance,
    track_source_usage,
    expand_citations
)
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


def format_sources_for_prompt(sources: List[Dict[str, Any]]) -> str:
    """
    Format sources into a readable list for the agent prompt

    Args:
        sources: List of source dictionaries

    Returns:
        Formatted string listing all sources with their numbers
    """
    if not sources:
        return "No sources provided."

    formatted = []
    for i, source in enumerate(sources, 1):
        formatted.append(f"""
Source {i}:
- Title: {source.get('title', 'Unknown')}
- Source: {source.get('source', 'Unknown')}
- Type: {source.get('source_type', 'unknown')}
- Date: {source.get('date', 'Unknown')}
- URL: {source.get('url', 'N/A')}
- Relevance: {source.get('relevance_score', 'N/A')}
- Excerpt: {source.get('text', '')[:300]}...
""")

    return "\n".join(formatted)


def clean_draft_response(draft: str, headline: str) -> str:
    """
    Clean up meta-commentary from agent response and extract actual article

    Args:
        draft: Raw response from agent
        headline: Expected article headline

    Returns:
        Cleaned article text
    """
    import re

    # Check if draft starts with headline
    if draft.startswith(f"# {headline}"):
        return draft

    # Common meta-commentary patterns to remove
    meta_patterns = [
        r"^(?:Here is|Here's|Please find|I've (?:created|written|prepared)).*?(?:\n|$)",
        r"^(?:The article is|This article is|It is).*?(?:ready|complete|finished).*?(?:\n|$)",
        r"^(?:I have|I've).*?(?:followed|adhered to|incorporated).*?(?:\n|$)",
        r"^(?:This draft|The draft).*?(?:\n|$)",
    ]

    for pattern in meta_patterns:
        draft = re.sub(pattern, '', draft, flags=re.IGNORECASE | re.MULTILINE)

    # Remove trailing meta-commentary
    trailing_patterns = [
        r"(?:\n|^)(?:This article|The article|It).*?(?:ready for review|ready for publication|adheres to).*?$",
        r"(?:\n|^)(?:Please|Feel free to).*?(?:review|edit|revise).*?$",
    ]

    for pattern in trailing_patterns:
        draft = re.sub(pattern, '', draft, flags=re.IGNORECASE | re.MULTILINE)

    # If headline is not at the start, try to find where article actually begins
    if not draft.strip().startswith('#'):
        # Look for the headline in the text
        headline_match = re.search(rf'^#\s+{re.escape(headline)}', draft, re.MULTILINE)
        if headline_match:
            draft = draft[headline_match.start():]
        else:
            # Look for any markdown heading
            heading_match = re.search(r'^#\s+', draft, re.MULTILINE)
            if heading_match:
                draft = draft[heading_match.start():]

    return draft.strip()


def generate_draft_with_agent(
    headline: str,
    thesis: str,
    outline: str,
    sources: List[Dict[str, Any]],
    target_word_count: int = 1500,
    key_facts: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generate article draft using ReActAgent with citation tools

    Args:
        headline: Article headline
        thesis: The thesis statement
        outline: Structured outline (markdown)
        sources: List of sources from outline endpoint
        target_word_count: Target word count (1000-2000)
        key_facts: Optional key facts to incorporate

    Returns:
        Dictionary containing draft, word_count, sources_used, and metadata
    """
    if not headline:
        raise ValueError("Headline cannot be empty")
    if not thesis:
        raise ValueError("Thesis statement cannot be empty")
    if not outline:
        raise ValueError("Outline cannot be empty")

    # Validate word count range
    if target_word_count < 1000:
        target_word_count = 1000
    elif target_word_count > 2000:
        target_word_count = 2000

    if key_facts is None:
        key_facts = []

    # Load editorial guidelines
    editorial_guidelines = load_editorial_guidelines()

    # Create system prompt for better instruction following
    system_prompt = """You are a professional journalist writing articles for publication.
When given an outline and sources, you write the complete article directly without any preamble or meta-commentary.
You ONLY output the article markdown text itself, starting with the headline (# format).
You NEVER say "here is the article" or provide explanations - you just write the article."""

    # Create LLM
    llm = OpenAI(
        api_key=settings.OPENAI_API_KEY,
        model="gpt-4",
        temperature=0.7,
        system_prompt=system_prompt
    )

    # Get tools
    tools = get_draft_tools()

    # Create agent
    agent = ReActAgent.from_tools(
        tools=tools,
        llm=llm,
        verbose=True,
        max_iterations=20
    )

    # Format sources for prompt
    sources_text = format_sources_for_prompt(sources)
    key_facts_text = "\n".join([f"- {fact}" for fact in key_facts]) if key_facts else "None provided"

    # Build comprehensive prompt
    agent_prompt = f"""
You are an AI Journalist Assistant. Your task is to write a complete article NOW.

CRITICAL INSTRUCTION:
Your response must be ONLY the article text itself. Do NOT write explanations, do NOT say "here is the article", do NOT provide meta-commentary. Start directly with the article headline (# format) and content.

EDITORIAL GUIDELINES:
{editorial_guidelines}

ARTICLE DETAILS:
Headline: {headline}
Thesis: {thesis}
Target Word Count: {target_word_count} words (acceptable range: 1000-2000 words)

KEY FACTS TO INCORPORATE:
{key_facts_text}

OUTLINE TO FOLLOW:
{outline}

AVAILABLE SOURCES (from outline generation):
{sources_text}

WRITING INSTRUCTIONS:

1. STRUCTURE:
   - Follow the outline structure exactly
   - Use the section headings from the outline as H2 (##) and H3 (###) headings
   - DO NOT include word count indicators like "(100-150 words)" in the article
   - DO NOT include placeholder instructions like "**To Cover:**" or "**Key Point:**"
   - Start with a compelling introduction (hook + context + thesis + why it matters now)
   - Write 2-4 well-developed paragraphs for each body section
   - End with a strong conclusion (synthesis + implications + memorable closing)

2. CONTENT QUALITY:
   - Write for intelligent non-specialists
   - Explain technical terms on first use
   - Use concrete examples to illustrate points
   - Average 15-20 words per sentence
   - Keep paragraphs to 2-4 sentences
   - Maintain conversational yet authoritative tone

3. SOURCES & CITATIONS:
   - PRIMARY RULE: Use ONLY the sources numbered above (Source 1, Source 2, etc.)
   - Every factual claim, statistic, or quote MUST have an inline citation
   - Citation format: Use the source number like [1], [2], [3], etc.
   - Place citations immediately after the claim, before the period
   - Example: "AI systems achieve 95% accuracy in cancer detection [1]."
   - Use the exact source numbers from the list above
   - Include at least 3 distinct sources throughout the article
   - If you cite the same source multiple times, use the same number each time

4. WORD COUNT:
   - Target: {target_word_count} words
   - Acceptable range: 1000-2000 words
   - Distribute words evenly across sections
   - Do not pad with unnecessary content

5. EDITORIAL STANDARDS:
   - No clickbait or sensationalism
   - No hype or hyperbole
   - No unverified claims
   - Clear positions while acknowledging complexity
   - Distinguished between facts and analysis

6. WHEN TO USE TOOLS:
   - Use archive_retrieval tool ONLY if you need additional specific information not in provided sources
   - Do NOT use tools unnecessarily - prioritize the provided sources
   - Remember: citations are simply [1], [2], [3], etc. - no tool needed

CRITICAL RULES:
- NEVER fabricate sources, statistics, or quotes
- NEVER cite sources not provided to you or retrieved via tools
- NEVER use general knowledge - only use provided sources
- ALWAYS cite claims - uncited factual claims are unacceptable
- ALWAYS follow editorial guidelines for voice and tone

REQUIRED OUTPUT FORMAT:
Your ENTIRE response must be the article itself, starting with:

# {headline}

[Then immediately start the introduction paragraph...]

Do NOT include:
- Any preamble like "Here is the article"
- Any explanations or meta-commentary
- Any notes about following guidelines
- Any "ready for review" statements
- Any word count indicators like "(100-150 words)" from the outline
- Any placeholder instructions like "**To Cover:**", "**Key Point:**", "**Hook:**" from the outline
- Any bracketed placeholders from the outline

The outline contains guidance notes - expand them into actual prose. Write real paragraphs, not templates.

Example:
Outline says: "**Hook:** [Placeholder: Describe what opening hook should accomplish]"
You write: "Medical professionals worldwide are witnessing an unprecedented transformation in diagnostic medicine..."

Just write the article directly. Start NOW with "# {headline}" followed by the article content.
"""

    try:
        logger.info(f"Generating draft for headline: {headline} (target: {target_word_count} words)")

        # Run agent
        response = agent.chat(agent_prompt)

        # Extract the draft from response
        draft_raw = str(response)
        logger.debug(f"Raw agent response (first 500 chars): {draft_raw[:500]}")

        # Clean up meta-commentary if present
        draft = clean_draft_response(draft_raw, headline)

        # Log if cleaning was needed
        if draft != draft_raw:
            logger.info("Cleaned meta-commentary from agent response")

        # Track source usage (with number-based citations [1], [2], [3], etc.)
        source_tracking = track_source_usage(draft, sources)
        logger.info(f"Tracked source usage: {source_tracking['unique_sources_count']} unique sources used")

        # Expand [X] citations to full [X, Source, Title, Date] format
        draft_expanded = expand_citations(draft, sources)

        # Count words (on expanded version)
        word_count = count_words(draft_expanded)
        logger.info(f"Draft generated: {word_count} words")

        # Validate editorial compliance (on expanded version)
        compliance_score = validate_editorial_compliance(draft_expanded, editorial_guidelines)

        # Generate warnings
        warnings = []
        if word_count < 1000:
            warnings.append(f"Word count below minimum: {word_count} words (target: {target_word_count})")
        elif word_count > 2000:
            warnings.append(f"Word count above maximum: {word_count} words (target: {target_word_count})")
        elif abs(word_count - target_word_count) > 200:
            warnings.append(f"Word count significantly different from target: {word_count} vs {target_word_count}")

        if source_tracking['unique_sources_count'] < 3:
            warnings.append(f"Low source diversity: only {source_tracking['unique_sources_count']} unique sources cited")

        if compliance_score < 0.7:
            warnings.append(f"Low editorial compliance score: {compliance_score:.2f}")

        if source_tracking['citation_count'] == 0:
            warnings.append("No citations found in draft - all claims must be cited")

        warning_text = "; ".join(warnings) if warnings else None

        return {
            "headline": headline,
            "thesis": thesis,
            "draft": draft_expanded,  # Return expanded version with full citations
            "word_count": word_count,
            "sources_used": source_tracking['sources_used'],
            "sources_available": source_tracking['sources_available'],
            "sections_generated": extract_sections(draft_expanded),
            "editorial_compliance_score": compliance_score,
            "warning": warning_text
        }

    except Exception as e:
        logger.error(f"Error generating draft with agent: {e}")
        raise


def extract_sections(draft: str) -> List[str]:
    """
    Extract H2 section headings from draft

    Args:
        draft: Markdown draft text

    Returns:
        List of section headings
    """
    import re
    sections = re.findall(r'^##\s+(.+)$', draft, re.MULTILINE)
    return sections
