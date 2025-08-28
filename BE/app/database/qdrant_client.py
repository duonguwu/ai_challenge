"""
Qdrant client for vector database operations
"""
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchRequest,
    CreateCollection,
    CollectionInfo
)
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from loguru import logger

from app.config import settings


class QdrantManager:
    """Manager class for Qdrant operations"""
    
    def __init__(self):
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port
        )
        self.collection_name = settings.qdrant_collection_name
        self.vector_size = settings.qdrant_vector_size
        
    async def init_collection(self) -> bool:
        """Initialize collection if it doesn't exist"""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Creating collection: {self.collection_name}")
                
                # Create collection with proper configuration
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Collection {self.collection_name} created successfully")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
            
            return True
            
        except Exception as e:
            logger.error(f"Error initializing collection: {e}")
            return False
    
    async def add_vectors(
        self, 
        vectors: List[np.ndarray], 
        ids: List[str],
        payloads: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Add vectors to collection"""
        try:
            if payloads is None:
                payloads = [{} for _ in vectors]
            
            points = []
            for i, (vector, point_id, payload) in enumerate(zip(vectors, ids, payloads)):
                points.append(
                    PointStruct(
                        id=point_id,
                        vector=vector.tolist(),
                        payload=payload
                    )
                )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"Added {len(points)} vectors to collection")
            return True
            
        except Exception as e:
            logger.error(f"Error adding vectors: {e}")
            return False
    
    async def search_vectors(
        self,
        query_vector: np.ndarray,
        limit: int = 10,
        score_threshold: float = 0.7,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Search for similar vectors"""
        try:
            # Build filter if conditions provided
            search_filter = None
            if filter_conditions:
                conditions = []
                for field, value in filter_conditions.items():
                    conditions.append(
                        FieldCondition(
                            key=field,
                            match=MatchValue(value=value)
                        )
                    )
                search_filter = Filter(must=conditions)
            
            # Perform search
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector.tolist(),
                limit=limit,
                score_threshold=score_threshold,
                query_filter=search_filter
            )
            
            # Format results
            results = []
            for point in search_result:
                results.append((
                    point.id,
                    point.score,
                    point.payload
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching vectors: {e}")
            return []
    
    async def delete_vectors(self, ids: List[str]) -> bool:
        """Delete vectors by IDs"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=ids
            )
            logger.info(f"Deleted {len(ids)} vectors from collection")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting vectors: {e}")
            return False
    
    async def get_collection_info(self) -> Optional[CollectionInfo]:
        """Get collection information"""
        try:
            return self.client.get_collection(self.collection_name)
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return None
    
    async def health_check(self) -> bool:
        """Check if Qdrant is healthy"""
        try:
            # Try to get collections to check connection
            self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False


# Global Qdrant manager instance
qdrant_manager = QdrantManager()
