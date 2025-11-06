from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator

# Request models
class TopicRequest(BaseModel):
    """Request model for generating article ideas"""
    topic: str = Field(..., description="Topic to generate ideas for")
    num_ideas: int = Field(3, description="Number of ideas to generate (1-5)", ge=1, le=5)

class OutlineRequest(BaseModel):
    """Request model for generating an article outline"""
    topic: str = Field(..., description="Topic of the article")
    thesis: str = Field(..., description="Thesis statement or main argument")

class DraftRequest(BaseModel):
    """Request model for generating a draft article"""
    topic: str = Field(..., description="Topic of the article")
    outline: str = Field(..., description="Article outline")
    word_count: int = Field(1500, description="Target word count (500-2000)", ge=500, le=2000)

# Source node model
class SourceNode(BaseModel):
    """Model for a source node"""
    text: str = Field(..., description="Text of the source node")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata of the source node")

# Response models
class IdeasResponse(BaseModel):
    """Response model for article ideas"""
    topic: str = Field(..., description="Topic of the ideas")
    num_ideas: int = Field(..., description="Number of ideas generated")
    ideas: str = Field(..., description="Generated ideas in markdown format")
    source_nodes: Optional[List[SourceNode]] = Field(None, description="Source nodes used for generation")

class OutlineResponse(BaseModel):
    """Response model for article outline"""
    topic: str = Field(..., description="Topic of the article")
    thesis: str = Field(..., description="Thesis statement or main argument")
    outline: str = Field(..., description="Generated outline in markdown format")
    source_nodes: Optional[List[SourceNode]] = Field(None, description="Source nodes used for generation")

class DraftResponse(BaseModel):
    """Response model for draft article"""
    topic: str = Field(..., description="Topic of the article")
    word_count: int = Field(..., description="Target word count")
    outline: str = Field(..., description="Article outline")
    draft: str = Field(..., description="Generated draft in markdown format")
    source_nodes: Optional[List[SourceNode]] = Field(None, description="Source nodes used for generation")

# Health check response
class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")