from fastapi import APIRouter, HTTPException
from app.models.schemas import DraftRequest, DraftResponse
from app.services.draft_agent import generate_draft_with_agent
import logging

# Get logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.post("/drafts", response_model=DraftResponse, status_code=200, tags=["drafts"])
async def generate_draft(request: DraftRequest):
    """
    Generate a publication-ready article draft using AI agent with citation tools

    **Request Body:**
    - **headline**: Article headline
    - **thesis**: The thesis statement or main argument
    - **outline**: Article outline in markdown (from outline endpoint)
    - **sources**: Sources from outline endpoint (list of Source objects)
    - **key_facts**: Optional key facts to incorporate
    - **target_word_count**: Target word count (1000-2000, default: 1500)

    **Returns:**
    A complete article draft with:
    - Full markdown article with H1/H2/H3 headings
    - Inline citations in [Source, Title, Date] format
    - Word count and editorial compliance score
    - Lists of sources used vs. available
    - Section headings generated
    - Quality warnings if applicable

    **Process:**
    The agent expands the outline into a full article by:
    1. Using provided sources from the outline endpoint
    2. Retrieving additional sources only when needed via archive_retrieval tool
    3. Formatting citations properly using citation_formatter tool
    4. Following editorial guidelines for voice, tone, and structure
    5. Validating quality and compliance

    **Editorial Standards:**
    - Intelligent, conversational tone
    - 15-20 words per sentence average
    - 2-4 sentences per paragraph
    - Every factual claim cited
    - No clickbait or sensationalism
    """
    try:
        logger.info(f"Generating draft for headline: {request.headline}")

        # Convert sources to dict format if provided
        sources = []
        if request.sources:
            sources = [source.dict() for source in request.sources]

        result = generate_draft_with_agent(
            headline=request.headline,
            thesis=request.thesis,
            outline=request.outline,
            sources=sources,
            target_word_count=request.target_word_count,
            key_facts=request.key_facts,
            enable_web_search=request.enable_web_search
        )

        logger.info(f"Draft generated: {result['word_count']} words, "
                   f"{len(result['sources_used'])} sources cited, "
                   f"compliance score: {result.get('editorial_compliance_score', 0):.2f}")

        return result

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating draft: {e}")
        raise HTTPException(status_code=500, detail="Error generating draft")