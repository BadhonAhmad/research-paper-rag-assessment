"""
Main FastAPI application for Research Paper RAG System
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import configuration
import config

# Import services
from services.pdf_processor import PDFProcessor
from services.embedding_service import EmbeddingService
from services.qdrant_client import QdrantService
from services.rag_pipeline import RAGPipeline

# Import database initialization
from models import init_db

# Import routes
from api import routes

# Initialize FastAPI app
app = FastAPI(
    title="Research Paper RAG System",
    description="Intelligent assistant for querying research papers using RAG",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
print("🔧 Initializing database...")
init_db()

# Initialize services
print("🔧 Initializing services...")

print("  Loading PDF processor...")
pdf_processor = PDFProcessor(
    chunk_size=config.CHUNK_SIZE,
    chunk_overlap=config.CHUNK_OVERLAP
)

print("  Loading embedding model...")
embedding_service = EmbeddingService(
    model_name=config.EMBEDDING_MODEL
)

print("  Connecting to Qdrant...")
qdrant_service = QdrantService(
    host=config.QDRANT_HOST,
    port=config.QDRANT_PORT,
    collection_name=config.QDRANT_COLLECTION_NAME,
    vector_dim=embedding_service.get_dimension()
)

print("  Initializing RAG pipeline...")
rag_pipeline = RAGPipeline(
    embedding_service=embedding_service,
    qdrant_service=qdrant_service,
    ollama_url=config.OLLAMA_BASE_URL,
    ollama_model=config.OLLAMA_MODEL,
    max_context_length=config.MAX_CONTEXT_LENGTH
)

# Initialize routes with services
routes.init_services(
    pdf_proc=pdf_processor,
    embed_svc=embedding_service,
    qdrant_svc=qdrant_service,
    rag_pipe=rag_pipeline
)

# Include router
app.include_router(routes.router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Research Paper RAG System API",
        "status": "operational",
        "version": "1.0.0",
        "endpoints": {
            "upload": "POST /api/papers/upload",
            "query": "POST /api/query",
            "list_papers": "GET /api/papers",
            "get_paper": "GET /api/papers/{id}",
            "delete_paper": "DELETE /api/papers/{id}",
            "paper_stats": "GET /api/papers/{id}/stats",
            "query_history": "GET /api/queries/history",
            "analytics": "GET /api/analytics/popular",
            "health": "GET /health",
            "docs": "GET /docs"
        }
    }


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Starting Research Paper RAG System")
    print("="*60)
    print(f"📡 API: http://{config.API_HOST}:{config.API_PORT}")
    print(f"📚 Docs: http://{config.API_HOST}:{config.API_PORT}/docs")
    print(f"🔍 Qdrant: {config.QDRANT_HOST}:{config.QDRANT_PORT}")
    print(f"🤖 Ollama: {config.OLLAMA_BASE_URL} (model: {config.OLLAMA_MODEL})")
    print("="*60 + "\n")
    
    # Important: point uvicorn to this module (main_new:app) for reload
    uvicorn.run(
        "main_new:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )
