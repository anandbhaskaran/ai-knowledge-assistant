from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.core.config import settings
from app.core import logging
from app.models.schemas import HealthResponse
from app.api.endpoints import ideas_router, outline_router, draft_router
import logging as logger

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ideas_router, prefix="/api/v1")
app.include_router(outline_router, prefix="/api/v1")
app.include_router(draft_router, prefix="/api/v1")

@app.get("/", include_in_schema=False)
async def root():
    """Redirect to docs"""
    return RedirectResponse(url="/docs")

@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.API_VERSION
    }