from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator

# Request models
class TopicRequest(BaseModel):
    """Request model for generating article ideas"""
    topic: str = Field(..., description="Topic to generate ideas for")
    num_ideas: int = Field(3, description="Number of ideas to generate (1-5)", ge=1, le=5)

class OutlineRequest(BaseModel):
    """Request model for generating an article outline"""
    headline: str = Field(..., description="Article headline")
    thesis: str = Field(..., description="Thesis statement or main argument")
    key_facts: List[str] = Field(default_factory=list, description="Key facts to incorporate")
    suggested_visualization: Optional[str] = Field(None, description="Suggested data visualization")

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
    relevance_score: Optional[float] = Field(None, description="Relevance score of the source node")

# Enhanced source model for agent-based retrieval
class Source(BaseModel):
    """Model for a retrieved source with full metadata"""
    title: str = Field(..., description="Title of the source")
    source: str = Field(..., description="Source name or publication")
    source_type: str = Field(..., description="Type of source: 'archive' or 'web'")
    date: str = Field(..., description="Publication date")
    url: str = Field(..., description="URL of the source")
    relevance_score: Optional[float] = Field(None, description="Relevance score (0-1)")
    text: str = Field(..., description="Excerpt or full text of the source")

# Individual idea model
class Idea(BaseModel):
    """Model for a single article idea"""
    headline: str = Field(..., description="Compelling headline for the article")
    thesis: str = Field(..., description="Clear thesis statement (1-2 sentences)")
    key_facts: List[str] = Field(..., description="List of 3 key facts with citations")
    suggested_visualization: str = Field(..., description="Suggested data visualization")

# Response models
class IdeasResponse(BaseModel):
    """Response model for article ideas"""
    topic: str = Field(..., description="Topic of the ideas")
    num_ideas: int = Field(..., description="Number of ideas generated")
    ideas: List[Idea] = Field(default_factory=list, description="Array of generated article ideas")
    source_nodes: Optional[List[SourceNode]] = Field(None, description="Source nodes used for generation")
    warning: Optional[str] = Field(None, description="Warning about source quality or relevance")

class OutlineResponse(BaseModel):
    """Response model for article outline"""
    headline: str = Field(..., description="Article headline")
    thesis: str = Field(..., description="Thesis statement or main argument")
    key_facts: Optional[List[str]] = Field(None, description="Key facts incorporated")
    suggested_visualization: Optional[str] = Field(None, description="Suggested data visualization")
    outline: str = Field(..., description="Generated outline in markdown format with placeholders")
    sources: Optional[List[Source]] = Field(None, description="Ranked sources with relevance scores from archive and web, sorted by relevance (highest first)")
    warning: Optional[str] = Field(None, description="Warning about source quality or relevance")

class DraftResponse(BaseModel):
    """Response model for draft article"""
    topic: str = Field(..., description="Topic of the article")
    word_count: int = Field(..., description="Target word count")
    outline: str = Field(..., description="Article outline")
    draft: str = Field(..., description="Generated draft in markdown format")
    source_nodes: Optional[List[SourceNode]] = Field(None, description="Source nodes used for generation")
    warning: Optional[str] = Field(None, description="Warning about source quality or relevance")

# Health check response
class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")