# Automated Blog Content Pipeline

An end-to-end automated content generation pipeline for publishing high-quality blog posts to Tistory using **LangChain**, **RAG (Retrieval-Augmented Generation)**, and **LangGraph**.

## 🎯 Features

- **Automated Content Generation**: Full lifecycle from research to publication
- **RAG-Grounded**: Uses retrieval-augmented generation to ensure factual accuracy
- **Multi-Agent Architecture**: Research, writing, critique, SEO, and publishing agents
- **LangGraph Orchestration**: State-based workflow with conditional logic and retries
- **Quality Assurance**: Built-in fact-checking and content review
- **Tistory Integration**: Direct publishing to Tistory blog platform
- **Observability**: LangSmith integration for tracing and debugging

## 🏗️ Architecture

```
User Topic Input
      ↓
┌─────────────────────────┐
│  LangGraph Orchestrator │
└─────────────────────────┘
      ↓
┌─────────────────────────┐
│   Research Agent (RAG)  │ ← Vector Store (FAISS/Chroma)
└─────────────────────────┘
      ↓
┌─────────────────────────┐
│   Outline Generator     │
└─────────────────────────┘
      ↓
┌─────────────────────────┐
│   Content Writer        │
└─────────────────────────┘
      ↓
┌─────────────────────────┐
│   Critic / QA Agent     │
└─────────────────────────┘
      ↓ (approved?)
┌─────────────────────────┐
│   SEO Optimizer         │
└─────────────────────────┘
      ↓
┌─────────────────────────┐
│   Tistory Publisher     │
└─────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- OpenAI API key
- Tistory API credentials (optional for dry-run mode)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd automated-blog-content-pipeline
```

2. Install dependencies:
```bash
pip install -e .
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Create knowledge base directory:
```bash
mkdir -p data/knowledge
```

5. Add your knowledge sources (markdown, PDF, text files) to `data/knowledge/`

### Running the Pipeline

```bash
python main.py
```

This will:
1. Initialize the RAG knowledge base
2. Run the complete pipeline for the example topic
3. Generate and save the blog post
4. Publish to Tistory (in dry-run mode by default)

## 📁 Project Structure

```
automated-blog-content-pipeline/
├── main.py                 # Application entry point
├── config.py              # Configuration management
├── models.py              # Pydantic data models
├── rag.py                 # RAG system implementation
├── agents.py              # Agent definitions
├── pipeline.py            # LangGraph pipeline orchestration
├── publisher.py           # Tistory publishing module
├── pyproject.toml         # Project dependencies
├── .env.example           # Environment template
├── README.md              # This file
├── data/
│   ├── knowledge/         # Knowledge base documents
│   └── vector_store/      # Vector embeddings
├── logs/                  # Application logs
└── output/                # Generated content
```

## 🔧 Configuration

All configuration is managed through environment variables (see `.env.example`):

### Key Settings

- **Models**: Configure which OpenAI models to use for each agent
- **RAG**: Vector store type (FAISS/Chroma), chunk size, embedding model
- **Pipeline**: Max iterations, confidence thresholds, manual approval
- **Publishing**: Draft vs publish mode, auto-publish, default tags

## 📝 Usage Examples

### Basic Usage

```python
from config import settings
from models import TopicSpec
from rag import RAGSystem
from pipeline import BlogPipeline

# Initialize RAG
rag = RAGSystem()
rag.load_documents(["./data/knowledge"])
rag.build_vector_store(documents)

# Create pipeline
pipeline = BlogPipeline(rag, dry_run=True)

# Define topic
topic = TopicSpec(
    title="Introduction to LangChain",
    description="A beginner's guide to LangChain",
    keywords=["LangChain", "AI", "Tutorial"],
    target_audience="developers",
    tone="educational and friendly"
)

# Run pipeline
result = pipeline.run(topic)
```

### Custom Knowledge Base

Add your own documents to the knowledge base:

```bash
# Add markdown files
cp my-research/*.md data/knowledge/

# Add PDFs
cp papers/*.pdf data/knowledge/

# Rebuild vector store
python -c "from main import BlogContentApp; app = BlogContentApp(); app.initialize_knowledge_base(['./data/knowledge'], rebuild=True)"
```

### Publishing to Tistory

1. Get your Tistory API credentials from https://www.tistory.com/guide/api/manage/list
2. Update `.env`:
```bash
TISTORY_API_KEY=your_api_key
TISTORY_BLOG_NAME=your_blog_name
```

3. Enable real publishing:
```python
app = BlogContentApp(dry_run=False)
```

## 🧪 Testing

Run in dry-run mode (default) to test without actual publication:

```python
app = BlogContentApp(dry_run=True)
result = app.run_pipeline(topic)
```

Output will be saved to `./output/` directory.

## 📊 Observability

Enable LangSmith tracing for detailed pipeline monitoring:

1. Get API key from https://smith.langchain.com
2. Set in `.env`:
```bash
LANGSMITH_API_KEY=your_key
LANGSMITH_TRACING=true
```

3. View traces at https://smith.langchain.com

## 🔒 Security

- API keys are loaded from environment variables only
- Source attribution tracking for all generated content
- Prompt injection protection in RAG retrieval
- Strict fact-checking to prevent hallucinations

## 🛠️ Customization

### Adding New Agents

1. Create agent class in `agents.py`
2. Add node to pipeline in `pipeline.py`
3. Update graph edges and conditional logic

### Custom Publishers

Implement the publisher interface:

```python
class CustomPublisher:
    def publish(self, content: BlogContent, visibility: str) -> PublishResult:
        # Your implementation
        pass
```

### Different LLM Providers

Update `config.py` and agent initialization to use:
- Anthropic Claude
- Local models (Ollama, LlamaCpp)
- Azure OpenAI
- Other LangChain-supported providers

## 📈 Future Enhancements

- [ ] Image generation integration
- [ ] Multi-language support
- [ ] Cross-posting (Medium, Dev.to)
- [ ] Analytics feedback loop
- [ ] Scheduled publishing
- [ ] Content update detection and refresh

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional quality metrics
- More sophisticated SEO optimization
- Enhanced error handling
- Additional publishing platforms
- UI/web interface

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

Built with:
- [LangChain](https://python.langchain.com/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [OpenAI](https://openai.com/)
- [FAISS](https://github.com/facebookresearch/faiss)

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check documentation at [https://junehongdominicus.com]
- Contact: junehong.dominicus@gmail.com

---
