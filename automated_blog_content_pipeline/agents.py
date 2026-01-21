"""Agent definitions for the blog content pipeline."""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from models import (
    TopicSpec,
    ResearchContext,
    BlogOutline,
    BlogContent,
    QAResult,
    OutlineSection,
)
from rag import RAGSystem
from config import settings
import logging
import json

logger = logging.getLogger(__name__)


class ResearchAgent:
    """Agent responsible for researching topics using RAG."""
    
    def __init__(self, rag_system: RAGSystem):
        self.rag = rag_system
        self.llm = ChatOpenAI(
            model=settings.research_model,
            temperature=settings.research_temperature,
            openai_api_key=settings.openai_api_key,
        )
        
    def research(self, topic: TopicSpec) -> ResearchContext:
        """Research a topic using RAG retrieval."""
        logger.info(f"Researching topic: {topic.title}")
        
        # Construct research query
        query = f"{topic.title} {topic.description} {' '.join(topic.keywords)}"
        
        # Retrieve relevant documents
        docs_with_scores = self.rag.retrieve_with_scores(query, k=10)
        
        if not docs_with_scores:
            logger.warning("No documents retrieved")
            return ResearchContext(confidence_score=0.0)
        
        # Extract information
        sources = []
        for doc, score in docs_with_scores:
            sources.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "relevance_score": float(score),
            })
        
        # Use LLM to extract key facts
        context_text = "\n\n---\n\n".join([s["content"] for s in sources[:5]])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a research assistant. Extract key facts from the provided context."),
            ("user", """Topic: {title}
Description: {description}

Context:
{context}

Extract 5-10 key facts that are relevant to writing a blog post about this topic.
Return as JSON with a "facts" array.""")
        ])
        
        chain = prompt | self.llm | JsonOutputParser()
        
        try:
            result = chain.invoke({
                "title": topic.title,
                "description": topic.description,
                "context": context_text,
            })
            key_facts = result.get("facts", [])
        except Exception as e:
            logger.error(f"Error extracting facts: {e}")
            key_facts = []
        
        # Calculate confidence score
        avg_score = sum(s["relevance_score"] for s in sources) / len(sources) if sources else 0
        confidence = min(1.0, avg_score * len(sources) / 5)
        
        return ResearchContext(
            sources=sources,
            key_facts=key_facts,
            references=[s["metadata"].get("source", "") for s in sources],
            confidence_score=confidence,
        )


class OutlineAgent:
    """Agent responsible for creating blog post outlines."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=0.5,
            openai_api_key=settings.openai_api_key,
        )
    
    def generate_outline(self, topic: TopicSpec, research: ResearchContext) -> BlogOutline:
        """Generate a structured outline for the blog post."""
        logger.info(f"Generating outline for: {topic.title}")
        
        facts_text = "\n".join(f"- {fact}" for fact in research.key_facts)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert content strategist. Create detailed blog post outlines 
that are well-structured, logical, and engaging for technical readers."""),
            ("user", """Create a detailed blog post outline for:

Title: {title}
Description: {description}
Target Audience: {audience}
Target Word Count: {word_count}

Key Facts:
{facts}

Return a JSON object with:
- title: Final blog post title (SEO-friendly)
- introduction: Summary of what the intro should cover
- sections: Array of objects with heading, level (1-3), content_points (array), estimated_words
- conclusion: Summary of what the conclusion should cover
- total_estimated_words: Total estimated word count""")
        ])
        
        chain = prompt | self.llm | JsonOutputParser()
        
        result = chain.invoke({
            "title": topic.title,
            "description": topic.description,
            "audience": topic.target_audience,
            "word_count": settings.target_word_count,
            "facts": facts_text,
        })
        
        # Parse sections
        sections = [OutlineSection(**s) for s in result.get("sections", [])]
        
        return BlogOutline(
            title=result.get("title", topic.title),
            introduction=result.get("introduction", ""),
            sections=sections,
            conclusion=result.get("conclusion", ""),
            total_estimated_words=result.get("total_estimated_words", settings.target_word_count),
        )


class WriterAgent:
    """Agent responsible for writing blog post content."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            openai_api_key=settings.openai_api_key,
        )
    
    def write_content(
        self,
        outline: BlogOutline,
        research: ResearchContext,
        topic: TopicSpec,
    ) -> BlogContent:
        """Write the complete blog post content."""
        logger.info(f"Writing content for: {outline.title}")
        
        # Prepare context
        facts_text = "\n".join(f"- {fact}" for fact in research.key_facts)
        outline_text = self._format_outline(outline)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert technical writer. Write engaging, accurate, and well-structured 
blog posts in Markdown format. Use ONLY the provided facts - do not make up information.

Guidelines:
- Write in {tone} tone
- Use Markdown formatting (headers, code blocks, lists, bold/italic)
- Include practical examples where relevant
- Maintain logical flow between sections
- Write for {audience}
- Cite facts from the research context"""),
            ("user", """Write a complete blog post following this outline:

{outline}

Use these verified facts:
{facts}

Target word count: {word_count}

Return the complete blog post in Markdown format.""")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        content = chain.invoke({
            "outline": outline_text,
            "facts": facts_text,
            "word_count": outline.total_estimated_words,
            "tone": topic.tone,
            "audience": topic.target_audience,
        })
        
        # Generate meta description
        meta_desc = self._generate_meta_description(outline.title, content[:500])
        
        word_count = len(content.split())
        
        return BlogContent(
            title=outline.title,
            content=content,
            meta_description=meta_desc,
            tags=topic.keywords,
            word_count=word_count,
        )
    
    def _format_outline(self, outline: BlogOutline) -> str:
        """Format outline as text."""
        lines = [
            f"# {outline.title}",
            f"\nIntroduction: {outline.introduction}\n",
        ]
        
        for section in outline.sections:
            prefix = "#" * (section.level + 1)
            lines.append(f"\n{prefix} {section.heading}")
            lines.append(f"Points to cover:")
            for point in section.content_points:
                lines.append(f"  - {point}")
        
        lines.append(f"\nConclusion: {outline.conclusion}")
        
        return "\n".join(lines)
    
    def _generate_meta_description(self, title: str, excerpt: str) -> str:
        """Generate SEO meta description."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Create a compelling 150-160 character meta description for SEO."),
            ("user", "Title: {title}\n\nExcerpt: {excerpt}\n\nMeta description:")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        return chain.invoke({"title": title, "excerpt": excerpt}).strip()


class CriticAgent:
    """Agent responsible for quality assurance and fact-checking."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.critic_model,
            temperature=settings.critic_temperature,
            openai_api_key=settings.openai_api_key,
        )
    
    def review(self, content: BlogContent, research: ResearchContext) -> QAResult:
        """Review content for quality and accuracy."""
        logger.info(f"Reviewing content: {content.title}")
        
        facts_text = "\n".join(f"- {fact}" for fact in research.key_facts)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a meticulous fact-checker and editor. Review blog posts for:
1. Factual accuracy (all claims must be supported by provided facts)
2. Logical flow and coherence
3. Redundancy or repetition
4. Writing quality
5. Hallucinations or unsupported claims

Be strict but constructive."""),
            ("user", """Review this blog post:

Title: {title}
Content:
{content}

Verified Facts:
{facts}

Minimum confidence threshold: {threshold}

Return JSON with:
- approved: boolean (true if content meets quality standards)
- score: float 0-1 (overall quality score)
- issues: array of identified problems
- suggestions: array of improvement suggestions  
- factual_accuracy: float 0-1 (how well facts are supported)""")
        ])
        
        chain = prompt | self.llm | JsonOutputParser()
        
        result = chain.invoke({
            "title": content.title,
            "content": content.content[:3000],  # Limit for token efficiency
            "facts": facts_text,
            "threshold": settings.fact_confidence_threshold,
        })
        
        return QAResult(**result)


class SEOAgent:
    """Agent responsible for SEO optimization."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=0.3,
            openai_api_key=settings.openai_api_key,
        )
    
    def optimize(self, content: BlogContent) -> BlogContent:
        """Optimize content for SEO."""
        logger.info(f"Optimizing SEO for: {content.title}")
        
        # For now, basic optimization - can be enhanced
        # Add keyword density checks, heading optimization, etc.
        
        return content  # Return as-is for v1