"""
Configuration settings for RAG system
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Qdrant Settings
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "research_papers")

# Google Gemini Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Embedding Settings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_DIM = 384  # Dimension for all-MiniLM-L6-v2

# Database Settings
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./research_papers.db")

# Processing Settings
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))

# Query Settings
MAX_CONTEXT_LENGTH = int(os.getenv("MAX_CONTEXT_LENGTH", "2000"))
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))
