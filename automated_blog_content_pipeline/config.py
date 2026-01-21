"""Configuration management for the blog content pipeline."""
import os
from dotenv import load_dotenv
from typing import Literal

# Load environment variables
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        # API Keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
        self.tistory_api_key = os.getenv("TISTORY_API_KEY")
        self.tistory_blog_name = os.getenv("TISTORY_BLOG_NAME")
        
        # LangSmith Configuration
        self.langsmith_project = os.getenv("LANGSMITH_PROJECT", "blog-content-pipeline")
        self.langsmith_tracing = os.getenv("LANGSMITH_TRACING", "true").lower() == "true"
        
        # Model Configuration
        self.llm_model = os.getenv("LLM_MODEL", "gpt-4-turbo-preview")
        self.llm_temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        self.research_model = os.getenv("RESEARCH_MODEL", "gpt-4-turbo-preview")
        self.research_temperature = float(os.getenv("RESEARCH_TEMPERATURE", "0.3"))
        self.critic_model = os.getenv("CRITIC_MODEL", "gpt-4-turbo-preview")
        self.critic_temperature = float(os.getenv("CRITIC_TEMPERATURE", "0.2"))
        
        # Vector Store Configuration
        self.vector_store_path = os.getenv("VECTOR_STORE_PATH", "./data/vector_store")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))
        
        # Pipeline Configuration
        self.max_research_iterations = int(os.getenv("MAX_RESEARCH_ITERATIONS", "3"))
        self.max_writing_iterations = int(os.getenv("MAX_WRITING_ITERATIONS", "2"))
        self.max_critic_iterations = int(os.getenv("MAX_CRITIC_ITERATIONS", "2"))
        self.fact_confidence_threshold = float(os.getenv("FACT_CONFIDENCE_THRESHOLD", "0.8"))
        self.enable_manual_approval = os.getenv("ENABLE_MANUAL_APPROVAL", "false").lower() == "true"
        
        # Content Configuration
        self.target_word_count = int(os.getenv("TARGET_WORD_COUNT", "1500"))
        self.min_word_count = int(os.getenv("MIN_WORD_COUNT", "800"))
        self.max_word_count = int(os.getenv("MAX_WORD_COUNT", "3000"))
        
        # Publishing Configuration
        self.publish_mode = os.getenv("PUBLISH_MODE", "draft")
        self.auto_publish = os.getenv("AUTO_PUBLISH", "false").lower() == "true"
        self.default_category = os.getenv("DEFAULT_CATEGORY", "Tech")
        
        # Parse default tags
        tags_str = os.getenv("DEFAULT_TAGS", "AI,Tech,Tutorial")
        self.default_tags = [tag.strip() for tag in tags_str.split(",")]
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE", "./logs/pipeline.log")


# Global settings instance
settings = Settings()