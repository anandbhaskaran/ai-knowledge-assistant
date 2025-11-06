from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import TopicRequest, IdeasResponse
from app.services import ideas as ideas_service
import logging

# Get logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.post("/ideas", response_model=IdeasResponse, status_code=200, tags=["ideas"])
async def generate_ideas(request: TopicRequest):
    """
    Generate article ideas based on a topic

    - **topic**: Topic to generate ideas for
    - **num_ideas**: Number of ideas to generate (default: 3, max: 5)
    """
    try:
        result = ideas_service.generate_ideas(
            topic=request.topic,
            num_ideas=request.num_ideas
        )
        return result
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating ideas: {e}")
        raise HTTPException(status_code=500, detail="Error generating ideas")