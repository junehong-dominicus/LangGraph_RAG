"""LangGraph-based pipeline orchestration for blog content generation."""
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END
from models import PipelineState, TopicSpec
from agents import ResearchAgent, OutlineAgent, WriterAgent, CriticAgent, SEOAgent
from publisher import get_publisher
from rag import RAGSystem
from config import settings
import logging

logger = logging.getLogger(__name__)


class BlogPipeline:
    """Orchestrates the entire blog content generation pipeline using LangGraph."""
    
    def __init__(self, rag_system: RAGSystem, dry_run: bool = False):
        self.rag = rag_system
        self.dry_run = dry_run
        
        # Initialize agents
        self.research_agent = ResearchAgent(rag_system)
        self.outline_agent = OutlineAgent()
        self.writer_agent = WriterAgent()
        self.critic_agent = CriticAgent()
        self.seo_agent = SEOAgent()
        self.publisher = get_publisher(dry_run)
        
        # Build graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(dict)
        
        # Add nodes
        workflow.add_node("research", self._research_node)
        workflow.add_node("outline", self._outline_node)
        workflow.add_node("write", self._write_node)
        workflow.add_node("critique", self._critique_node)
        workflow.add_node("optimize", self._optimize_node)
        workflow.add_node("publish", self._publish_node)
        
        # Define edges
        workflow.set_entry_point("research")
        workflow.add_edge("research", "outline")
        workflow.add_edge("outline", "write")
        workflow.add_edge("write", "critique")
        
        # Conditional edge after critique
        workflow.add_conditional_edges(
            "critique",
            self._should_revise,
            {
                "revise": "write",
                "optimize": "optimize",
            }
        )
        
        workflow.add_edge("optimize", "publish")
        workflow.add_edge("publish", END)
        
        return workflow.compile()
    
    def _research_node(self, state: dict) -> dict:
        """Research node: gather context using RAG."""
        logger.info("=== RESEARCH NODE ===")
        
        topic = TopicSpec(**state["topic"])
        state["current_stage"] = "research"
        
        try:
            research_context = self.research_agent.research(topic)
            state["research_context"] = research_context.model_dump()
            
            if research_context.confidence_score < settings.fact_confidence_threshold:
                logger.warning(
                    f"Low confidence score: {research_context.confidence_score:.2f}"
                )
                state["errors"].append(
                    f"Research confidence below threshold: {research_context.confidence_score:.2f}"
                )
        except Exception as e:
            logger.error(f"Research node error: {e}")
            state["errors"].append(f"Research error: {str(e)}")
        
        return state
    
    def _outline_node(self, state: dict) -> dict:
        """Outline node: create structured outline."""
        logger.info("=== OUTLINE NODE ===")
        
        state["current_stage"] = "outline"
        
        try:
            from models import ResearchContext
            topic = TopicSpec(**state["topic"])
            research = ResearchContext(**state["research_context"])
            
            outline = self.outline_agent.generate_outline(topic, research)
            state["outline"] = outline.model_dump()
            
            logger.info(f"Generated outline with {len(outline.sections)} sections")
        except Exception as e:
            logger.error(f"Outline node error: {e}")
            state["errors"].append(f"Outline error: {str(e)}")
        
        return state
    
    def _write_node(self, state: dict) -> dict:
        """Write node: generate blog content."""
        logger.info("=== WRITE NODE ===")
        
        state["current_stage"] = "write"
        state["iteration_count"] = state.get("iteration_count", 0) + 1
        
        try:
            from models import BlogOutline, ResearchContext
            topic = TopicSpec(**state["topic"])
            outline = BlogOutline(**state["outline"])
            research = ResearchContext(**state["research_context"])
            
            content = self.writer_agent.write_content(outline, research, topic)
            state["draft_content"] = content.model_dump()
            
            logger.info(f"Generated content: {content.word_count} words")
        except Exception as e:
            logger.error(f"Write node error: {e}")
            state["errors"].append(f"Write error: {str(e)}")
        
        return state
    
    def _critique_node(self, state: dict) -> dict:
        """Critique node: review content quality."""
        logger.info("=== CRITIQUE NODE ===")
        
        state["current_stage"] = "critique"
        
        try:
            from models import BlogContent, ResearchContext
            content = BlogContent(**state["draft_content"])
            research = ResearchContext(**state["research_context"])
            
            qa_result = self.critic_agent.review(content, research)
            state["qa_result"] = qa_result.model_dump()
            
            logger.info(f"QA Score: {qa_result.score:.2f}, Approved: {qa_result.approved}")
            
            if qa_result.issues:
                logger.info(f"Issues found: {len(qa_result.issues)}")
                for issue in qa_result.issues:
                    logger.info(f"  - {issue}")
        except Exception as e:
            logger.error(f"Critique node error: {e}")
            state["errors"].append(f"Critique error: {str(e)}")
        
        return state
    
    def _optimize_node(self, state: dict) -> dict:
        """Optimize node: SEO optimization."""
        logger.info("=== OPTIMIZE NODE ===")
        
        state["current_stage"] = "optimize"
        
        try:
            from models import BlogContent
            content = BlogContent(**state["draft_content"])
            
            optimized = self.seo_agent.optimize(content)
            state["final_content"] = optimized.model_dump()
            
            logger.info("Content optimized for SEO")
        except Exception as e:
            logger.error(f"Optimize node error: {e}")
            state["errors"].append(f"Optimize error: {str(e)}")
            # Use draft as final if optimization fails
            state["final_content"] = state["draft_content"]
        
        return state
    
    def _publish_node(self, state: dict) -> dict:
        """Publish node: publish to Tistory."""
        logger.info("=== PUBLISH NODE ===")
        
        state["current_stage"] = "publish"
        
        try:
            from models import BlogContent
            content = BlogContent(**state["final_content"])
            
            # Check manual approval if enabled
            if settings.enable_manual_approval:
                logger.info("Manual approval required")
                approval = input(f"Approve publication of '{content.title}'? (yes/no): ")
                if approval.lower() != "yes":
                    logger.info("Publication cancelled by user")
                    state["publish_result"] = {
                        "success": False,
                        "error_message": "Cancelled by user",
                    }
                    return state
            
            # Publish
            visibility = settings.publish_mode if settings.auto_publish else "draft"
            result = self.publisher.publish(content, visibility=visibility)
            state["publish_result"] = result.model_dump()
            
            if result.success:
                logger.info(f"Published successfully: {result.post_url}")
            else:
                logger.error(f"Publication failed: {result.error_message}")
        except Exception as e:
            logger.error(f"Publish node error: {e}")
            state["errors"].append(f"Publish error: {str(e)}")
        
        return state
    
    def _should_revise(self, state: dict) -> str:
        """Determine if content needs revision."""
        from models import QAResult
        
        qa = QAResult(**state["qa_result"])
        iteration = state.get("iteration_count", 0)
        
        # Check if approved
        if qa.approved:
            logger.info("Content approved, moving to optimization")
            return "optimize"
        
        # Check iteration limit
        if iteration >= settings.max_writing_iterations:
            logger.warning(
                f"Max iterations reached ({iteration}), proceeding despite issues"
            )
            return "optimize"
        
        # Revise
        logger.info(f"Content needs revision (iteration {iteration})")
        return "revise"
    
    def run(self, topic: TopicSpec) -> dict:
        """Run the complete pipeline."""
        logger.info(f"Starting pipeline for topic: {topic.title}")
        
        # Initialize state
        initial_state = {
            "topic": topic.model_dump(),
            "current_stage": "initialized",
            "iteration_count": 0,
            "errors": [],
        }
        
        # Run graph
        try:
            final_state = self.graph.invoke(initial_state)
            logger.info("Pipeline completed successfully")
            return final_state
        except Exception as e:
            logger.error(f"Pipeline execution error: {e}")
            initial_state["errors"].append(f"Pipeline error: {str(e)}")
            return initial_state