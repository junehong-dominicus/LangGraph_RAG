"""Retrieval-Augmented Generation module for fact-grounded content."""
import os
from pathlib import Path
from typing import List, Dict
from langchain_community.document_loaders import (
    TextLoader,
    DirectoryLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS, Chroma
from langchain_core.documents import Document
from config import settings
import logging

logger = logging.getLogger(__name__)


class RAGSystem:
    """Manages document ingestion, embedding, and retrieval."""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )
        
    def load_documents(self, source_paths: List[str]) -> List[Document]:
        """Load documents from various sources."""
        documents = []
        
        for path in source_paths:
            path_obj = Path(path)
            
            try:
                if path_obj.is_file():
                    documents.extend(self._load_single_file(path_obj))
                elif path_obj.is_dir():
                    documents.extend(self._load_directory(path_obj))
                else:
                    logger.warning(f"Path not found: {path}")
            except Exception as e:
                logger.error(f"Error loading {path}: {e}")
                
        logger.info(f"Loaded {len(documents)} documents")
        return documents
    
    def _load_single_file(self, path: Path) -> List[Document]:
        """Load a single file based on extension."""
        suffix = path.suffix.lower()
        
        try:
            if suffix == ".pdf":
                loader = PyPDFLoader(str(path))
            elif suffix == ".md":
                loader = UnstructuredMarkdownLoader(str(path))
            elif suffix in [".txt", ".py", ".json"]:
                loader = TextLoader(str(path))
            else:
                logger.warning(f"Unsupported file type: {suffix}")
                return []
            
            return loader.load()
        except Exception as e:
            logger.error(f"Error loading file {path}: {e}")
            return []
    
    def _load_directory(self, path: Path) -> List[Document]:
        """Load all supported files from a directory."""
        documents = []
        
        for pattern in ["**/*.md", "**/*.txt", "**/*.pdf"]:
            try:
                loader = DirectoryLoader(
                    str(path),
                    glob=pattern,
                    show_progress=True,
                )
                documents.extend(loader.load())
            except Exception as e:
                logger.error(f"Error loading directory {path} with pattern {pattern}: {e}")
        
        return documents
    
    def build_vector_store(self, documents: List[Document]) -> None:
        """Build vector store from documents."""
        if not documents:
            logger.warning("No documents to build vector store")
            return
        
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Split into {len(chunks)} chunks")
        
        # Create vector store
        if settings.vector_store_type == "faiss":
            self.vector_store = FAISS.from_documents(chunks, self.embeddings)
            # Save to disk
            os.makedirs(settings.vector_store_path, exist_ok=True)
            self.vector_store.save_local(settings.vector_store_path)
            logger.info(f"FAISS vector store saved to {settings.vector_store_path}")
        else:  # chroma
            self.vector_store = Chroma.from_documents(
                chunks,
                self.embeddings,
                persist_directory=settings.vector_store_path
            )
            logger.info(f"Chroma vector store saved to {settings.vector_store_path}")
    
    def load_vector_store(self) -> bool:
        """Load existing vector store from disk."""
        try:
            if settings.vector_store_type == "faiss":
                self.vector_store = FAISS.load_local(
                    settings.vector_store_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
            else:  # chroma
                self.vector_store = Chroma(
                    persist_directory=settings.vector_store_path,
                    embedding_function=self.embeddings
                )
            logger.info("Vector store loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return False
    
    def retrieve(self, query: str, k: int = 5) -> List[Document]:
        """Retrieve relevant documents for a query."""
        if not self.vector_store:
            logger.warning("Vector store not initialized")
            return []
        
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            logger.info(f"Retrieved {len(docs)} documents for query: {query[:50]}...")
            return docs
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    def retrieve_with_scores(self, query: str, k: int = 5) -> List[tuple[Document, float]]:
        """Retrieve documents with relevance scores."""
        if not self.vector_store:
            logger.warning("Vector store not initialized")
            return []
        
        try:
            docs_with_scores = self.vector_store.similarity_search_with_score(query, k=k)
            logger.info(f"Retrieved {len(docs_with_scores)} documents with scores")
            return docs_with_scores
        except Exception as e:
            logger.error(f"Error retrieving documents with scores: {e}")
            return []