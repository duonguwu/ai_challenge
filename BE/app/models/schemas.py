"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"


class VectorSearchRequest(BaseModel):
    """Request model for vector search"""
    query_vector: List[float] = Field(..., description="Query vector for similarity search")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum number of results")
    score_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum similarity score")
    filter_conditions: Optional[Dict[str, Any]] = Field(default=None, description="Filter conditions")


class VectorSearchResult(BaseModel):
    """Individual search result"""
    id: str
    score: float
    payload: Dict[str, Any]


class VectorSearchResponse(BaseModel):
    """Response model for vector search"""
    results: List[VectorSearchResult]
    total_found: int
    query_time_ms: float


class VectorUploadRequest(BaseModel):
    """Request model for uploading vectors"""
    vectors: List[List[float]] = Field(..., description="List of vectors to upload")
    ids: List[str] = Field(..., description="IDs for each vector")
    payloads: Optional[List[Dict[str, Any]]] = Field(default=None, description="Payload data for each vector")


class VectorUploadResponse(BaseModel):
    """Response model for vector upload"""
    success: bool
    uploaded_count: int
    message: str


class VectorDeleteRequest(BaseModel):
    """Request model for deleting vectors"""
    ids: List[str] = Field(..., description="IDs of vectors to delete")


class VectorDeleteResponse(BaseModel):
    """Response model for vector deletion"""
    success: bool
    deleted_count: int
    message: str


class CollectionInfoResponse(BaseModel):
    """Response model for collection information"""
    name: str
    vector_size: int
    points_count: int
    status: str


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# Video Search API Schemas
class VideoSearchRequest(BaseModel):
    """Request model for video search"""
    query_text: List[str] = Field(..., description="List of text queries for video search")


class VideoSearchResult(BaseModel):
    """Individual video search result"""
    original_id: str = Field(..., description="Original video ID")
    jpg_path: str = Field(..., description="Path to the JPEG image file")
    frame_idx: int = Field(..., description="Frame index in the video")
    similarity_score: float = Field(..., description="Similarity score (0.0-1.0)")


class VideoSearchResponse(BaseModel):
    """Response model for video search"""
    results: List[VideoSearchResult] = Field(..., description="List of search results")
