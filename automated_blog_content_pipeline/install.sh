#!/bin/bash

echo "========================================"
echo "Automated Blog Content Pipeline Setup"
echo "========================================"
echo ""

echo "Step 1: Installing dependencies..."
pip install --upgrade pip
pip install langchain>=0.3.0
pip install langchain-openai>=0.2.0
pip install langchain-community>=0.3.0
pip install langgraph>=0.2.0
pip install openai>=1.12.0
pip install faiss-cpu>=1.7.4
pip install tiktoken>=0.5.2
pip install python-dotenv>=1.0.0
pip install pydantic>=2.5.0
pip install pydantic-settings>=2.1.0
pip install requests>=2.31.0
pip install beautifulsoup4>=4.12.0
pip install markdown>=3.5.0
pip install pypdf>=3.17.0

echo ""
echo "Step 2: Creating directories..."
mkdir -p data/knowledge
mkdir -p data/vector_store
mkdir -p logs
mkdir -p output

echo ""
echo "Step 3: Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file - Please edit it with your API keys!"
else
    echo ".env file already exists"
fi

echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your OPENAI_API_KEY"
echo "2. Add knowledge documents to data/knowledge/ folder"
echo "3. Run: python main.py"
echo ""