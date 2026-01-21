"""Data models for the blog content pipeline."""
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


class TopicSpec(BaseModel):
    """Specification for a blog post topic."""
    title: str = Field(description="Working title for the blog post")
    description: str = Field(description="Brief description of what to cover")
    keywords: list[str] = Field(default_factory=list, description="Target keywords")
    target_audience: str = Field(default="technical readers", description="Target audience")
    tone: str = Field(default="informative and engaging", description="Writing tone")


class ResearchContext(BaseModel):
    """Research context gathered for the blog post."""
    sources: list[dict] = Field(default_factory=list, description="Source documents")
    key_facts: list[str] = Field(default_factory=list, description="Extracted key facts")
    references: list[str] = Field(default_factory=list, description="Reference URLs/paths")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Overall confidence")


class OutlineSection(BaseModel):
    """A section in the blog post outline."""
    heading: str = Field(description="Section heading")
    level: int = Field(ge=1, le=3, description="Heading level (1-3)")
    content_points: list[str] = Field(default_factory=list, description="Key points to cover")
    estimated_words: int = Field(default=200, description="Estimated word count")


class BlogOutline(BaseModel):
    """Complete blog post outline."""
    title: str = Field(description="Final blog post title")
    introduction: str = Field(description="Introduction summary")
    sections: list[OutlineSection] = Field(description="Outline sections")
    conclusion: str = Field(description="Conclusion summary")
    total_estimated_words: int = Field(description="Total estimated word count")


class BlogContent(BaseModel):
    """Complete blog post content."""
    title: str = Field(description="Blog post title")
    content: str = Field(description="Full blog post content in Markdown")
    meta_description: str = Field(description="SEO meta description")
    tags: list[str] = Field(default_factory=list, description="Content tags")
    category: str = Field(default="Tech", description="Content category")
    word_count: int = Field(description="Actual word count")
    created_at: datetime = Field(default_factory=datetime.now)


class QAResult(BaseModel):
    """Quality assurance result."""
    approved: bool = Field(description="Whether content is approved")
    score: float = Field(ge=0.0, le=1.0, description="Quality score")
    issues: list[str] = Field(default_factory=list, description="Identified issues")
    suggestions: list[str] = Field(default_factory=list, description="Improvement suggestions")
    factual_accuracy: float = Field(ge=0.0, le=1.0, description="Factual accuracy score")


class PublishResult(BaseModel):
    """Result of publishing attempt."""
    success: bool = Field(description="Whether publishing succeeded")
    post_url: str | None = Field(default=None, description="Published post URL")
    post_id: str | None = Field(default=None, description="Platform post ID")
    error_message: str | None = Field(default=None, description="Error message if failed")
    published_at: datetime | None = Field(default=None, description="Publication timestamp")


class PipelineState(BaseModel):
    """State object for the LangGraph pipeline."""
    # Input
    topic: TopicSpec | None = None
    
    # Intermediate
    research_context: ResearchContext | None = None
    outline: BlogOutline | None = None
    draft_content: BlogContent | None = None
    qa_result: QAResult | None = None
    final_content: BlogContent | None = None
    
    # Output
    publish_result: PublishResult | None = None
    
    # Control
    iteration_count: int = 0
    current_stage: str = "initialized"
    errors: list[str] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True