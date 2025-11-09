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
    enable_web_search: bool = Field(True, description="Enable web search for current information (default: True)")

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
    citation_number: Optional[int] = Field(None, description="Citation number if used in draft (1, 2, 3, etc.)")

class DraftRequest(BaseModel):
    """Request model for generating a draft article"""
    headline: str = Field(..., description="Article headline")
    thesis: str = Field(..., description="Thesis statement or main argument")
    outline: str = Field(..., description="Article outline in markdown format (from outline endpoint)")
    sources: Optional[List[Source]] = Field(None, description="Sources from outline endpoint to use for draft")
    key_facts: Optional[List[str]] = Field(None, description="Key facts to incorporate")
    target_word_count: int = Field(1500, description="Target word count (1000-2000)", ge=1000, le=2000)
    enable_web_search: bool = Field(False, description="Enable web search for additional sources (default: False)")

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
    headline: str = Field(..., description="Article headline")
    thesis: str = Field(..., description="Thesis statement")
    draft: str = Field(..., description="Generated draft article in markdown format with inline citations")
    word_count: int = Field(..., description="Actual word count of the draft")
    sources_used: Optional[List[Source]] = Field(None, description="Sources actually cited in the draft")
    sources_available: Optional[List[Source]] = Field(None, description="Sources provided but not cited")
    sections_generated: Optional[List[str]] = Field(None, description="List of H2 section headings generated")
    editorial_compliance_score: Optional[float] = Field(None, description="Editorial compliance score (0-1)")
    warning: Optional[str] = Field(None, description="Warnings about quality, word count, or compliance")

# Health check response
class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")