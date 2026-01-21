# Quick Start Guide

## Installation (Windows)

### Option 1: Using the install script (Recommended)
```bash
install.bat
```

### Option 2: Manual installation
```bash
# Install dependencies
pip install langchain langchain-openai langchain-community langgraph openai faiss-cpu tiktoken python-dotenv pydantic pydantic-settings requests beautifulsoup4 markdown pypdf

# Create directories
mkdir data\knowledge data\vector_store logs output

# Create .env file
copy .env.example .env
```

## Installation (Mac/Linux)

### Option 1: Using the install script (Recommended)
```bash
chmod +x install.sh
./install.sh
```

### Option 2: Manual installation
```bash
# Install dependencies
pip install langchain langchain-openai langchain-community langgraph openai faiss-cpu tiktoken python-dotenv pydantic pydantic-settings requests beautifulsoup4 markdown pypdf

# Create directories
mkdir -p data/knowledge data/vector_store logs output

# Create .env file
cp .env.example .env
```

## Configuration

1. **Edit `.env` file** and add your OpenAI API key:
```bash
OPENAI_API_KEY=sk-your-key-here
```

2. **Add knowledge documents** to `data/knowledge/`:
   - Markdown files (.md)
   - Text files (.txt)
   - PDF files (.pdf)
   - Python files (.py)

Example:
```bash
# Windows
copy my-docs\*.md data\knowledge\

# Mac/Linux
cp my-docs/*.md data/knowledge/
```

## Running the Pipeline

```bash
python main.py
```

### What happens:
1. ✅ Loads or creates knowledge base from `data/knowledge/`
2. ✅ Researches the example topic using RAG
3. ✅ Generates outline
4. ✅ Writes blog post
5. ✅ Reviews and fact-checks
6. ✅ Optimizes for SEO
7. ✅ Saves output to `output/` directory

### Output files:
- `output/state_TIMESTAMP.json` - Complete pipeline state
- `output/post_TIMESTAMP.md` - Final blog post with metadata

## Customizing the Topic

Edit `main.py` around line 100:

```python
topic = TopicSpec(
    title="Your Blog Post Title",
    description="What you want to write about",
    keywords=["keyword1", "keyword2", "keyword3"],
    target_audience="your target readers",
    tone="informative and engaging",
)
```

## Testing Without Knowledge Base

The pipeline includes a sample knowledge base if no documents are found. To test immediately:

```bash
# Just run it - sample content will be created automatically
python main.py
```

## Troubleshooting

### ModuleNotFoundError
```bash
# Reinstall dependencies
pip install --upgrade langchain langchain-openai langchain-community langgraph
```

### OpenAI API Error
- Check your `.env` file has `OPENAI_API_KEY=sk-...`
- Verify your API key is valid at https://platform.openai.com/api-keys
- Check you have credits available

### No documents loaded
- Add at least one `.md`, `.txt`, or `.pdf` file to `data/knowledge/`
- Or let it create sample content automatically

### Vector store errors
```bash
# Delete and rebuild
rmdir /s data\vector_store  # Windows
rm -rf data/vector_store    # Mac/Linux

# Run again
python main.py
```

## Publishing to Tistory (Optional)

1. Get API credentials from https://www.tistory.com/guide/api/manage/list

2. Edit `.env`:
```bash
TISTORY_API_KEY=your_api_key
TISTORY_BLOG_NAME=your_blog_name
```

3. Edit `main.py` line 79 to disable dry-run:
```python
app = BlogContentApp(dry_run=False)  # Change to False
```

## Next Steps

1. **Add your own knowledge**: Put your documents in `data/knowledge/`
2. **Customize topics**: Edit the topic specification in `main.py`
3. **Adjust settings**: Modify `.env` for different models, word counts, etc.
4. **Enable publishing**: Set up Tistory credentials for real publishing

## Support

- Check logs in `logs/pipeline.log` for detailed information
- Review generated content in `output/` directory
- See full documentation in `README.md`

---

**Note**: First run may take a few minutes as it downloads models and builds the vector store.