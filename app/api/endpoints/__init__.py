# Import routers
from app.api.endpoints.ideas import router as ideas_router
from app.api.endpoints.outline import router as outline_router
from app.api.endpoints.draft import router as draft_router

# Export routers
__all__ = ["ideas_router", "outline_router", "draft_router"]