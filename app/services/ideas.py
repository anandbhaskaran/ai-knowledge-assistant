import logging
import json
from typing import List, Dict, Any, Optional

from app.services.retriever import get_query_engine, filter_by_relevance
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

    # System prompt with strict anti-hallucination instructions and JSON output
    system_prompt = f"""
    You are an AI Journalist Assistant. Generate {num_ideas} article ideas about the given topic.

    ⚠️ CRITICAL RULES - FOLLOW EXACTLY:
    1. ONLY use information from the retrieved source documents provided below
    2. If the retrieved documents do NOT contain relevant information about the topic, return an empty array: {{"ideas": []}}
    3. NEVER fabricate statistics, quotes, studies, or sources
    4. NEVER use your general knowledge - ONLY use the retrieved documents
    5. Every fact MUST have a citation in the format [Source filename, Date]
    6. If you cannot find 3 relevant facts in the sources, include fewer facts

    If relevant sources ARE found, generate {num_ideas} article ideas, each with:
    1. A compelling headline
    2. A clear thesis statement (1-2 sentences)
    3. Key facts with citations from retrieved sources ONLY (as many as you can find, aim for 3)
    4. A suggested data visualization

    Format requirements:
    - Format each citation as [Source filename, Date from metadata]
    - Only cite sources that are actually provided below
    - Make headlines attention-grabbing but factual

    Return your response as a JSON object with this EXACT structure:
    {{
      "ideas": [
        {{
          "headline": "Article headline here",
          "thesis": "Thesis statement here",
          "key_facts": [
            "Fact 1 with citation [filename, date]",
            "Fact 2 with citation [filename, date]",
            "Fact 3 with citation [filename, date]"
          ],
          "suggested_visualization": "Description of suggested visualization"
        }}
      ]
    }}

    Return ONLY valid JSON, no markdown formatting, no code blocks.
    """

    try:
        # Create OpenAI LLM with system prompt and JSON mode
        llm = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            temperature=0.7,
            system_prompt=system_prompt,
            response_format={"type": "json_object"}
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

        # Filter results by relevance
        filtered_nodes, warning = filter_by_relevance(response.source_nodes)

        # If no relevant sources found, return early with clear message
        if not filtered_nodes:
            logger.warning(f"No relevant sources found for topic: {topic}. {warning}")
            return {
                "topic": topic,
                "num_ideas": 0,
                "ideas": [],
                "source_nodes": [],
                "warning": warning
            }

        # Log quality warning if sources are marginal
        if warning:
            logger.warning(f"Quality warning for topic '{topic}': {warning}")

        # Parse JSON response
        try:
            response_text = response.response.strip()
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```json")[-1].split("```")[0].strip()

            parsed_response = json.loads(response_text)
            ideas_list = parsed_response.get("ideas", [])

            logger.info(f"Successfully parsed {len(ideas_list)} ideas for topic: {topic}")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}. Response: {response.response[:200]}")
            # Fallback: return empty array with error in warning
            return {
                "topic": topic,
                "num_ideas": 0,
                "ideas": [],
                "source_nodes": [
                    {
                        "text": node.node.get_text(),
                        "metadata": node.node.metadata,
                        "relevance_score": getattr(node, 'score', None)
                    }
                    for node in filtered_nodes
                ],
                "warning": f"Failed to parse structured response. {warning if warning else ''}"
            }

        # Extract and return ideas
        return {
            "topic": topic,
            "num_ideas": len(ideas_list),
            "ideas": ideas_list,
            "source_nodes": [
                {
                    "text": node.node.get_text(),
                    "metadata": node.node.metadata,
                    "relevance_score": getattr(node, 'score', None)
                }
                for node in filtered_nodes
            ],
            "warning": warning  # Include warning if sources are low quality
        }
    except Exception as e:
        logger.error(f"Error generating ideas: {e}")
        raise