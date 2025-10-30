"""
Qdrant vector database client
"""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from typing import List, Dict, Optional
from uuid import uuid4


class QdrantService:
    """Handle Qdrant vector database operations"""
    
    def __init__(self, host: str, port: int, collection_name: str, vector_dim: int = 384):
        """
        Initialize Qdrant client
        
        Args:
            host: Qdrant host
            port: Qdrant port
            collection_name: Name of the collection
            vector_dim: Dimension of vectors
        """
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self.vector_dim = vector_dim
        self._init_collection()
    
    def _init_collection(self):
        """Initialize collection if it doesn't exist"""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_dim,
                        distance=Distance.COSINE
                    )
                )
                print(f"✅ Created Qdrant collection: {self.collection_name}")
            else:
                print(f"✅ Qdrant collection exists: {self.collection_name}")
                
        except Exception as e:
            print(f"Error initializing collection: {str(e)}")
            raise
    
    def add_vectors(
        self,
        vectors: List[List[float]],
        payloads: List[Dict],
        paper_id: int
    ) -> int:
        """
        Add vectors to collection
        
        Args:
            vectors: List of embedding vectors
            payloads: List of metadata dicts
            paper_id: ID of the paper
            
        Returns:
            Number of vectors added
        """
        try:
            points = []
            for i, (vector, payload) in enumerate(zip(vectors, payloads)):
                # Add paper_id to payload
                payload['paper_id'] = paper_id
                
                point = PointStruct(
                    id=str(uuid4()),
                    vector=vector,
                    payload=payload
                )
                points.append(point)
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            print(f"✅ Added {len(points)} vectors for paper_id={paper_id}")
            return len(points)
            
        except Exception as e:
            print(f"Error adding vectors: {str(e)}")
            return 0
    
    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        paper_ids: Optional[List[int]] = None,
        score_threshold: float = 0.0
    ) -> List[Dict]:
        """
        Search for similar vectors
        
        Args:
            query_vector: Query embedding
            top_k: Number of results to return
            paper_ids: Optional filter by paper IDs
            score_threshold: Minimum similarity score
            
        Returns:
            List of search results with metadata
        """
        try:
            # Build filter if paper_ids provided
            query_filter = None
            if paper_ids:
                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key="paper_id",
                            match=MatchValue(value=paper_ids[0] if len(paper_ids) == 1 else paper_ids)
                        )
                    ]
                )
            
            # Search
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
                query_filter=query_filter,
                score_threshold=score_threshold
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'id': result.id,
                    'score': result.score,
                    'payload': result.payload
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching vectors: {str(e)}")
            return []
    
    def delete_by_paper_id(self, paper_id: int) -> bool:
        """
        Delete all vectors for a paper
        
        Args:
            paper_id: ID of the paper
            
        Returns:
            Success status
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="paper_id",
                            match=MatchValue(value=paper_id)
                        )
                    ]
                )
            )
            print(f"✅ Deleted vectors for paper_id={paper_id}")
            return True
            
        except Exception as e:
            print(f"Error deleting vectors: {str(e)}")
            return False
    
    def count_vectors(self, paper_id: Optional[int] = None) -> int:
        """
        Count vectors in collection
        
        Args:
            paper_id: Optional filter by paper ID
            
        Returns:
            Number of vectors
        """
        try:
            if paper_id:
                # Count for specific paper
                results = self.client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=Filter(
                        must=[
                            FieldCondition(
                                key="paper_id",
                                match=MatchValue(value=paper_id)
                            )
                        ]
                    ),
                    limit=1,
                    with_payload=False,
                    with_vectors=False
                )
                return results[1] if results else 0
            else:
                # Count all
                info = self.client.get_collection(self.collection_name)
                return info.points_count
                
        except Exception as e:
            print(f"Error counting vectors: {str(e)}")
            return 0
