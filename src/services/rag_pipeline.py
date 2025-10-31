"""
RAG Pipeline - orchestrates retrieval and generation
"""
import time
import requests
from typing import List, Dict, Tuple
from services.embedding_service import EmbeddingService
from services.qdrant_client import QdrantService
from services.llm_service import LLMService


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline"""
    
    def __init__(
        self,
        embedding_service: EmbeddingService,
        qdrant_service: QdrantService,
        llm_service: LLMService,
        max_context_length: int = 2000
    ):
        """
        Initialize RAG pipeline
        
        Args:
            embedding_service: Service for generating embeddings
            qdrant_service: Service for vector search
            llm_service: Text generation service (Google Gemini)
            max_context_length: Maximum context length in tokens
        """
        self.embedding_service = embedding_service
        self.qdrant_service = qdrant_service
        self.llm_service = llm_service
        self.max_context_length = max_context_length
    
    def query(
        self,
        question: str,
        top_k: int = 5,
        paper_ids: List[int] = None
    ) -> Dict:
        """
        Process a query through the RAG pipeline
        
        Args:
            question: User's question
            top_k: Number of chunks to retrieve
            paper_ids: Optional filter by paper IDs
            
        Returns:
            Dict with answer, citations, confidence, etc.
        """
        start_time = time.time()
        
        try:
            # Step 1: Embed the question
            query_embedding = self.embedding_service.embed_text(question)
            
            # Step 2: Retrieve relevant chunks
            search_results = self.qdrant_service.search(
                query_vector=query_embedding,
                top_k=top_k,
                paper_ids=paper_ids
            )
            
            if not search_results:
                return {
                    'answer': "I couldn't find any relevant information in the papers to answer this question.",
                    'citations': [],
                    'sources_used': [],
                    'confidence': 0.0,
                    'response_time': time.time() - start_time
                }
            
            # Step 3: Assemble context and prepare citations
            context, citations = self._prepare_context(search_results)
            
            # Step 4: Generate answer using Gemini
            answer = self._generate_answer(question, context)
            
            # Step 5: Calculate confidence
            confidence = self._calculate_confidence(search_results)
            
            # Step 6: Extract unique sources
            sources_used = list(set([c['paper_title'] for c in citations]))
            
            response_time = time.time() - start_time
            
            return {
                'answer': answer,
                'citations': citations,
                'sources_used': sources_used,
                'confidence': confidence,
                'response_time': response_time
            }
            
        except Exception as e:
            print(f"Error in RAG pipeline: {str(e)}")
            return {
                'answer': f"An error occurred while processing your query: {str(e)}",
                'citations': [],
                'sources_used': [],
                'confidence': 0.0,
                'response_time': time.time() - start_time
            }
    
    def _prepare_context(self, search_results: List[Dict]) -> Tuple[str, List[Dict]]:
        """
        Prepare context from search results and create citations
        
        Args:
            search_results: Results from vector search
            
        Returns:
            Tuple of (context_string, citations_list)
        """
        context_parts = []
        citations = []
        
        for i, result in enumerate(search_results):
            payload = result['payload']
            score = result['score']
            
            # Build context chunk with source info
            chunk_text = payload.get('text', '')
            title = payload.get('title', 'Unknown')
            page = payload.get('page', 0)
            section = payload.get('section', 'Unknown')
            
            # Add to context with reference number
            context_parts.append(f"[{i+1}] {chunk_text}")
            
            # Create citation
            citations.append({
                'paper_title': title,
                'section': section,
                'page': page,
                'relevance_score': round(score, 3),
                'chunk_text': chunk_text[:200] + '...' if len(chunk_text) > 200 else chunk_text
            })
        
        # Join context, limit by length
        full_context = '\n\n'.join(context_parts)
        
        # Truncate if too long (rough estimate: 4 chars = 1 token)
        max_chars = self.max_context_length * 4
        if len(full_context) > max_chars:
            full_context = full_context[:max_chars] + '...'
        
        return full_context, citations
    
    def _generate_answer(self, question: str, context: str) -> str:
        """
        Generate answer using Gemini
        
        Args:
            question: User's question
            context: Retrieved context
            
        Returns:
            Generated answer
        """
        # Construct prompt with instructions
        prompt = f"""You are a helpful research assistant. Answer the question based ONLY on the provided context from research papers.

Context from research papers:
{context}

Question: {question}

Instructions:
- Answer concisely and accurately based on the context
- Reference specific papers or sections when possible
- If the context doesn't contain enough information, say so
- Do not make up information outside the provided context
- Use technical language appropriate for researchers

Answer:"""
        
        try:
            return self.llm_service.generate_text(prompt)
        except Exception as e:
            print(f"Error generating with LLM service: {e}")
            return f"Error generating answer: {e}"
    
    def _calculate_confidence(self, search_results: List[Dict]) -> float:
        """
        Calculate confidence score based on retrieval scores
        
        Args:
            search_results: Results from vector search
            
        Returns:
            Confidence score between 0 and 1
        """
        if not search_results:
            return 0.0
        
        # Use average of top-3 scores
        top_scores = [r['score'] for r in search_results[:3]]
        avg_score = sum(top_scores) / len(top_scores)
        
        # Normalize to 0-1 range (cosine similarity is already 0-1)
        confidence = min(max(avg_score, 0.0), 1.0)
        
        return round(confidence, 3)
