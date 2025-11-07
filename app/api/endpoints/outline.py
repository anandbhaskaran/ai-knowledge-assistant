from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import OutlineRequest, OutlineResponse
from app.services import outline as outline_service
import logging

# Get logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.post("/outlines", response_model=OutlineResponse, status_code=200, tags=["outlines"])
async def generate_outline(request: OutlineRequest):
    """
    Generate a detailed article outline based on a selected idea

    - **headline**: Article headline
    - **thesis**: The thesis statement or main argument
    - **key_facts**: Key facts to incorporate (from idea generation)
    - **suggested_visualization**: Suggested data visualization

    Returns a detailed markdown outline with:
    - Clear structure and headings
    - Placeholder text indicating what to write in each section
    - Citations to relevant sources
    - Incorporation of editorial guidelines
    """
    try:
        result = outline_service.generate_outline(
            headline=request.headline,
            thesis=request.thesis,
            key_facts=request.key_facts,
            suggested_visualization=request.suggested_visualization
        )
        return result
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating outline: {e}")
        raise HTTPException(status_code=500, detail="Error generating outline")