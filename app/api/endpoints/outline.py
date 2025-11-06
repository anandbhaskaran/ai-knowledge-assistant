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
    Generate an article outline based on a topic and thesis

    - **topic**: The topic of the article
    - **thesis**: The thesis statement or main argument
    """
    try:
        result = outline_service.generate_outline(
            topic=request.topic,
            thesis=request.thesis
        )
        return result
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating outline: {e}")
        raise HTTPException(status_code=500, detail="Error generating outline")