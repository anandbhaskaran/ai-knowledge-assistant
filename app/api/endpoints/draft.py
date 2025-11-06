from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import DraftRequest, DraftResponse
from app.services import draft as draft_service
import logging

# Get logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.post("/drafts", response_model=DraftResponse, status_code=200, tags=["drafts"])
async def generate_draft(request: DraftRequest):
    """
    Generate a draft article based on a topic and outline

    - **topic**: The topic of the article
    - **outline**: The article outline
    - **word_count**: Target word count (default: 1500, min: 500, max: 2000)
    """
    try:
        result = draft_service.generate_draft(
            topic=request.topic,
            outline=request.outline,
            word_count=request.word_count
        )
        return result
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating draft: {e}")
        raise HTTPException(status_code=500, detail="Error generating draft")