"""
Embedding service using sentence-transformers (lazy-loaded to speed up API startup)
"""
from typing import List, Optional
import numpy as np


class EmbeddingService:
    """Generate embeddings for text using sentence-transformers"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embedding service (model is loaded on first use)
        """
        self.model_name = model_name
        self.model: Optional[object] = None
        self.dimension: Optional[int] = None

    def _ensure_model(self):
        """Lazily load the embedding model when first needed"""
        if self.model is None:
            print(f"Loading embedding model: {self.model_name}")
            # Import here to avoid heavy import at server startup
            from sentence_transformers import SentenceTransformer  # type: ignore
            self.model = SentenceTransformer(self.model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            print(f"✅ Embedding model loaded. Dimension: {self.dimension}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding
        """
        try:
            self._ensure_model()
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            print(f"Error embedding text: {str(e)}")
            dim = self.dimension or 384
            return [0.0] * dim
    
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            
        Returns:
            List of embeddings
        """
        try:
            self._ensure_model()
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            return embeddings.tolist()
        except Exception as e:
            print(f"Error embedding texts: {str(e)}")
            dim = self.dimension or 384
            return [[0.0] * dim] * len(texts)
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        return self.dimension or 384
