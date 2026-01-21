"""Main application entry point for the automated blog content pipeline."""
import os
import sys
import logging
from pathlib import Path
from typing import Optional
import json
from datetime import datetime

from config import settings
from models import TopicSpec, BlogContent
from rag import RAGSystem
from pipeline import BlogPipeline


# Configure logging
def setup_logging():
    """Configure application logging."""
    log_dir = Path(settings.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(settings.log_file),
            logging.StreamHandler(sys.stdout),
        ]
    )


logger = logging.getLogger(__name__)


class BlogContentApp:
    """Main application class for blog content generation."""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.rag = RAGSystem()
        self.pipeline: Optional[BlogPipeline] = None
    
    def initialize_knowledge_base(self, source_paths: list[str], rebuild: bool = False):
        """
        Initialize the RAG knowledge base.
        
        Args:
            source_paths: List of file/directory paths to load
            rebuild: If True, rebuild even if vector store exists
        """
        logger.info("Initializing knowledge base...")
        
        vector_store_exists = Path(settings.vector_store_path).exists()
        
        if vector_store_exists and not rebuild:
            logger.info("Loading existing vector store...")
            if self.rag.load_vector_store():
                logger.info("Vector store loaded successfully")
                return
            else:
                logger.warning("Failed to load vector store, rebuilding...")
        
        # Build new vector store
        logger.info(f"Building vector store from {len(source_paths)} sources...")
        documents = self.rag.load_documents(source_paths)
        
        if not documents:
            logger.error("No documents loaded!")
            return
        
        self.rag.build_vector_store(documents)
        logger.info("Knowledge base initialized")
    
    def run_pipeline(self, topic: TopicSpec) -> dict:
        """
        Run the complete content generation pipeline.
        
        Args:
            topic: Topic specification
            
        Returns:
            Final pipeline state
        """
        if not self.rag.vector_store:
            logger.error("Knowledge base not initialized!")
            raise RuntimeError("Must initialize knowledge base before running pipeline")
        
        # Create pipeline
        self.pipeline = BlogPipeline(self.rag, dry_run=self.dry_run)
        
        # Run pipeline
        logger.info(f"Running pipeline for: {topic.title}")
        result = self.pipeline.run(topic)
        
        # Save result
        self._save_result(result)
        
        return result
    
    def _save_result(self, state: dict):
        """Save pipeline result to disk."""
        output_dir = Path("./output")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save state
        state_file = output_dir / f"state_{timestamp}.json"
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, default=str)
        logger.info(f"State saved to {state_file}")
        
        # Save final content if available
        if state.get("final_content"):
            from models import BlogContent
            content = BlogContent(**state["final_content"])
            
            content_file = output_dir / f"post_{timestamp}.md"
            with open(content_file, "w", encoding="utf-8") as f:
                f.write(f"---\n")
                f.write(f"title: {content.title}\n")
                f.write(f"tags: {', '.join(content.tags)}\n")
                f.write(f"category: {content.category}\n")
                f.write(f"word_count: {content.word_count}\n")
                f.write(f"created: {content.created_at}\n")
                f.write(f"---\n\n")
                f.write(content.content)
            
            logger.info(f"Content saved to {content_file}")


def main():
    """Main entry point."""
    setup_logging()
    logger.info("=" * 60)
    logger.info("Automated Blog Content Pipeline")
    logger.info("=" * 60)
    
    # Check for OpenAI API key
    if not settings.openai_api_key:
        logger.error("OPENAI_API_KEY not set in environment!")
        sys.exit(1)
    
    # Create app
    app = BlogContentApp(dry_run=True)
    
    # Example: Initialize knowledge base
    # Modify these paths to your actual knowledge sources
    knowledge_sources = [
        "./data/knowledge",  # Directory with markdown/text files
        # "./data/research.pdf",  # Individual PDF
        # "./data/notes.md",  # Individual markdown
    ]
    
    # Only initialize if sources exist
    if any(Path(p).exists() for p in knowledge_sources):
        app.initialize_knowledge_base(knowledge_sources, rebuild=False)
    else:
        logger.warning("No knowledge sources found, creating sample...")
        # Create sample knowledge
        sample_dir = Path("./data/knowledge")
        sample_dir.mkdir(parents=True, exist_ok=True)
        
        sample_file = sample_dir / "sample.md"
        sample_file.write_text("""# Sample Knowledge Base

## LangChain
LangChain is a framework for developing applications powered by language models.
It provides tools for prompt management, chains, and agents.

## RAG (Retrieval-Augmented Generation)
RAG combines retrieval systems with language models to ground responses in factual information.
It helps reduce hallucinations by providing relevant context.

## LangGraph
LangGraph is a library for building stateful, multi-actor applications with LLMs.
It uses graph-based workflows for complex orchestration.
""")
        logger.info(f"Created sample knowledge at {sample_file}")
        app.initialize_knowledge_base([str(sample_dir)], rebuild=True)
    
    # Example: Run pipeline
    topic = TopicSpec(
        title="Building AI-Powered Applications with LangChain",
        description="A comprehensive guide to using LangChain for building production-grade AI applications",
        keywords=["LangChain", "AI", "LLM", "Python", "Tutorial"],
        target_audience="developers and AI engineers",
        tone="technical but accessible",
    )
    
    logger.info("\n" + "=" * 60)
    logger.info("Starting content generation...")
    logger.info("=" * 60 + "\n")
    
    try:
        result = app.run_pipeline(topic)
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Final stage: {result.get('current_stage')}")
        logger.info(f"Iterations: {result.get('iteration_count')}")
        
        if result.get("errors"):
            logger.warning(f"Errors: {len(result['errors'])}")
            for error in result["errors"]:
                logger.warning(f"  - {error}")
        
        if result.get("final_content"):
            content = BlogContent(**result["final_content"])
            logger.info(f"\nGenerated post: {content.title}")
            logger.info(f"Word count: {content.word_count}")
            logger.info(f"Tags: {', '.join(content.tags)}")
        
        if result.get("publish_result"):
            from models import PublishResult
            pub = PublishResult(**result["publish_result"])
            if pub.success:
                logger.info(f"\n✓ Published: {pub.post_url}")
            else:
                logger.error(f"\n✗ Publication failed: {pub.error_message}")
        
        logger.info("\n" + "=" * 60)
        logger.info("Pipeline completed!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()