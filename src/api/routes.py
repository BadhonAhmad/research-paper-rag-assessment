"""
API routes for RAG system
"""
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Query as QueryParam
from sqlalchemy.orm import Session
from typing import List, Optional
import tempfile
import os
import shutil
from datetime import datetime

from models.database import Paper, Query as QueryModel
from models.schemas import (
    PaperUploadResponse, QueryRequest, QueryResponse,
    PaperDetail, QueryHistory, PaperStats
)
from models import get_db
from services.pdf_processor import PDFProcessor
from services.embedding_service import EmbeddingService
from services.qdrant_client import QdrantService
from services.rag_pipeline import RAGPipeline
from services.cache_service import QueryCache
import config

# Initialize services (will be injected in main.py)
pdf_processor = None
embedding_service = None
qdrant_service = None
rag_pipeline = None
query_cache = None

router = APIRouter()


def init_services(
    pdf_proc: PDFProcessor,
    embed_svc: EmbeddingService,
    qdrant_svc: QdrantService,
    rag_pipe: RAGPipeline,
    cache: Optional[QueryCache] = None
):
    """Initialize services for routes"""
    global pdf_processor, embedding_service, qdrant_service, rag_pipeline, query_cache
    pdf_processor = pdf_proc
    embedding_service = embed_svc
    qdrant_service = qdrant_svc
    rag_pipeline = rag_pipe
    query_cache = cache


@router.post("/api/papers/upload", response_model=PaperUploadResponse)
async def upload_paper(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process a research paper PDF
    
    - Extracts metadata (title, authors, year)
    - Creates semantic chunks
    - Generates embeddings
    - Stores in Qdrant and database
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Check if paper already exists
    existing = db.query(Paper).filter(Paper.filename == file.filename).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Paper '{file.filename}' already exists")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    try:
        # Process PDF
        chunks, metadata = pdf_processor.process_pdf(tmp_path)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="Failed to extract text from PDF")
        
        # Create paper record
        paper = Paper(
            title=metadata['title'],
            authors=metadata['authors'],
            year=metadata['year'],
            filename=file.filename,
            file_path=tmp_path,
            total_pages=metadata['total_pages'],
            processed=0,  # Processing
            chunk_count=len(chunks)
        )
        db.add(paper)
        db.commit()
        db.refresh(paper)
        
        # Generate embeddings for all chunks
        chunk_texts = [chunk.page_content for chunk in chunks]
        embeddings = embedding_service.embed_texts(chunk_texts)
        
        # Prepare payloads
        payloads = []
        for chunk in chunks:
            payloads.append({
                'text': chunk.page_content,
                'page': chunk.metadata.get('page'),
                'section': chunk.metadata.get('section'),
                'title': metadata['title'],
                'chunk_index': chunk.metadata.get('chunk_index')
            })
        
        # Store in Qdrant
        stored_count = qdrant_service.add_vectors(embeddings, payloads, paper.id)
        
        # Update paper status
        paper.processed = 1
        paper.chunk_count = stored_count
        db.commit()
        
        # Clear cache since new content is available (queries without paper_ids filter should get new results)
        if query_cache and config.CACHE_ENABLED:
            query_cache.clear()  # Simple approach: clear all cache when new paper added
        
        return PaperUploadResponse(
            paper_id=paper.id,
            title=paper.title,
            filename=paper.filename,
            total_pages=paper.total_pages,
            chunk_count=paper.chunk_count,
            message="Paper uploaded and processed successfully"
        )
        
    except Exception as e:
        # Mark as failed
        if 'paper' in locals():
            paper.processed = -1
            db.commit()
        raise HTTPException(status_code=500, detail=f"Error processing paper: {str(e)}")
    
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except:
                pass


@router.post("/api/query", response_model=QueryResponse)
async def query_papers(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    """
    Query research papers using RAG with caching
    
    - Checks cache for repeated queries (instant response)
    - Retrieves relevant chunks using vector similarity
    - Generates answer using Gemini
    - Returns answer with citations
    - Caches result for future queries
    """
    try:
        # Check cache first (if enabled)
        cache_hit = False
        if query_cache and config.CACHE_ENABLED:
            cached_result = query_cache.get(
                question=request.question,
                top_k=request.top_k,
                paper_ids=request.paper_ids
            )
            
            if cached_result:
                cache_hit = True
                result = cached_result
                # Add cache indicator to response
                result['cached'] = True
                result['response_time'] = 0.001  # Near-instant from cache
        
        # Cache miss - run RAG pipeline
        if not cache_hit:
            result = rag_pipeline.query(
                question=request.question,
                top_k=request.top_k,
                paper_ids=request.paper_ids
            )
            result['cached'] = False
            
            # Cache the result for future queries
            if query_cache and config.CACHE_ENABLED:
                query_cache.set(
                    question=request.question,
                    response=result,
                    top_k=request.top_k,
                    paper_ids=request.paper_ids
                )
        
        # Save query to database (even for cache hits to track usage)
        query_record = QueryModel(
            question=request.question,
            answer=result['answer'],
            paper_ids_filter=request.paper_ids,
            top_k=request.top_k,
            response_time=result['response_time'],
            confidence=result['confidence'],
            sources_used=result['sources_used'],
            citations=result['citations']
        )
        db.add(query_record)
        db.commit()
        
        return QueryResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.get("/api/papers", response_model=List[PaperDetail])
async def list_papers(
    skip: int = QueryParam(0, ge=0),
    limit: int = QueryParam(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all uploaded papers"""
    papers = db.query(Paper).filter(Paper.processed == 1).offset(skip).limit(limit).all()
    return papers


@router.get("/api/papers/{paper_id}", response_model=PaperDetail)
async def get_paper(paper_id: int, db: Session = Depends(get_db)):
    """Get details of a specific paper"""
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


@router.delete("/api/papers/{paper_id}")
async def delete_paper(paper_id: int, db: Session = Depends(get_db)):
    """Delete a paper and its vectors"""
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    try:
        # Delete from Qdrant
        qdrant_service.delete_by_paper_id(paper_id)
        
        # Delete file if exists
        if paper.file_path and os.path.exists(paper.file_path):
            os.remove(paper.file_path)
        
        # Invalidate cached queries for this paper
        if query_cache and config.CACHE_ENABLED:
            query_cache.invalidate_by_paper(paper_id)
        
        # Delete from database
        db.delete(paper)
        db.commit()
        
        return {"message": f"Paper '{paper.title}' deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting paper: {str(e)}")


@router.get("/api/papers/{paper_id}/stats", response_model=PaperStats)
async def get_paper_stats(paper_id: int, db: Session = Depends(get_db)):
    """Get statistics for a specific paper"""
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Get queries that referenced this paper
    queries = db.query(QueryModel).filter(
        QueryModel.paper_ids_filter.contains([paper_id])
    ).all()
    
    total_queries = len(queries)
    avg_confidence = sum(q.confidence for q in queries) / total_queries if total_queries > 0 else 0.0
    
    # Extract common topics (simplified)
    most_common_topics = ["methodology", "results", "datasets"]  # Placeholder
    
    return PaperStats(
        paper_id=paper.id,
        title=paper.title,
        total_queries=total_queries,
        avg_confidence=round(avg_confidence, 3),
        most_common_topics=most_common_topics
    )


@router.get("/api/queries/history", response_model=List[QueryHistory])
async def get_query_history(
    skip: int = QueryParam(0, ge=0),
    limit: int = QueryParam(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get recent query history"""
    queries = db.query(QueryModel).order_by(
        QueryModel.query_date.desc()
    ).offset(skip).limit(limit).all()
    
    return queries


@router.get("/api/analytics/popular")
async def get_popular_topics(
    limit: int = QueryParam(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get most queried topics"""
    # Get all queries
    queries = db.query(QueryModel).all()
    
    # Count word frequency in questions (simplified)
    word_freq = {}
    stop_words = {'what', 'is', 'the', 'how', 'in', 'a', 'an', 'of', 'to', 'and', 'for'}
    
    for query in queries:
        words = query.question.lower().split()
        for word in words:
            if len(word) > 3 and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency
    popular = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    return {
        "popular_topics": [{"topic": word, "count": count} for word, count in popular],
        "total_queries": len(queries)
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "pdf_processor": pdf_processor is not None,
            "embedding_service": embedding_service is not None,
            "qdrant": qdrant_service is not None,
            "rag_pipeline": rag_pipeline is not None,
            "query_cache": query_cache is not None and config.CACHE_ENABLED
        }
    }


@router.get("/api/cache/stats")
async def get_cache_stats():
    """Get cache statistics and performance metrics"""
    if not query_cache or not config.CACHE_ENABLED:
        return {
            "enabled": False,
            "message": "Cache is disabled"
        }
    
    stats = query_cache.get_stats()
    stats['enabled'] = True
    return stats


@router.post("/api/cache/clear")
async def clear_cache():
    """Clear all cached queries"""
    if not query_cache or not config.CACHE_ENABLED:
        return {
            "enabled": False,
            "message": "Cache is disabled"
        }
    
    query_cache.clear()
    return {
        "message": "Cache cleared successfully",
        "enabled": True
    }


@router.post("/api/cache/cleanup")
async def cleanup_expired_cache():
    """Remove expired entries from cache"""
    if not query_cache or not config.CACHE_ENABLED:
        return {
            "enabled": False,
            "message": "Cache is disabled"
        }
    
    removed_count = query_cache.cleanup_expired()
    return {
        "message": f"Removed {removed_count} expired entries",
        "removed_count": removed_count,
        "enabled": True
    }
