from fastapi import APIRouter, HTTPException
from app.models.schemas import OutlineRequest, OutlineResponse
from app.services.outline_agent import generate_outline_with_agent
import logging

# Get logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.post("/outlines", response_model=OutlineResponse, status_code=200, tags=["outlines"])
async def generate_outline(request: OutlineRequest):
    """
    Generate a detailed article outline using AI agent with archive and web search tools

    **Request Body:**
    - **headline**: Article headline
    - **thesis**: The thesis statement or main argument
    - **key_facts**: Key facts to incorporate (from idea generation)
    - **suggested_visualization**: Suggested data visualization

    **Returns:**
    A detailed markdown outline with:
    - Clear structure with H2 and H3 headings
    - Placeholder text indicating what to write in each section
    - Citations to relevant sources from both archive and web
    - Ranked sources with relevance scores and source_type (archive/web)
    - Incorporation of editorial guidelines

    **Sources:**
    - Archive sources from Qdrant vector database
    - Web sources from Tavily API (real-time search)
    - All sources ranked by relevance score (0-1)
    """
    try:
        logger.info(f"Generating outline for headline: {request.headline}")

        result = generate_outline_with_agent(
            headline=request.headline,
            thesis=request.thesis,
            key_facts=request.key_facts,
            suggested_visualization=request.suggested_visualization
        )

        logger.info(f"Outline generated successfully with {len(result.get('sources', []))} sources")
        return result

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating outline: {e}")
        raise HTTPException(status_code=500, detail="Error generating outline")