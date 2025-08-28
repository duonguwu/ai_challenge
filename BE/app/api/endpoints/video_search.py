"""
Video search endpoints
"""
from fastapi import APIRouter, HTTPException
from loguru import logger

from app.models.schemas import VideoSearchRequest, VideoSearchResponse, VideoSearchResult

router = APIRouter()


@router.post("/search", response_model=VideoSearchResponse)
async def search_videos(request: VideoSearchRequest):
    """
    Search for video frames based on text query
    
    Returns a list of video frames with original_id, jpg_path, and frame_idx.
    """
    try:
        # Log the search queries
        logger.info(f"Searching for queries: {request.query_text}")
        
        # TODO: Implement actual text-to-vector search logic here
        # For now, return mock data based on the queries
        
        # Mock search results
        mock_results = [
            VideoSearchResult(
                original_id="video_001",
                jpg_path="/data/frames/video_001/frame_000123.jpg",
                frame_idx=123,
                similarity_score=0.95
            ),
            VideoSearchResult(
                original_id="video_002", 
                jpg_path="/data/frames/video_002/frame_000045.jpg",
                frame_idx=45,
                similarity_score=0.92
            ),
            VideoSearchResult(
                original_id="video_001",
                jpg_path="/data/frames/video_001/frame_000156.jpg", 
                frame_idx=156,
                similarity_score=0.90
            ),
            VideoSearchResult(
                original_id="video_003",
                jpg_path="/data/frames/video_003/frame_000078.jpg",
                frame_idx=78,
                similarity_score=0.88
            ),
            VideoSearchResult(
                original_id="video_002",
                jpg_path="/data/frames/video_002/frame_000234.jpg",
                frame_idx=234,
                similarity_score=0.85
            )
        ]
        
        return VideoSearchResponse(results=mock_results)
        
    except Exception as e:
        logger.error(f"Video search failed: {e}")
        raise HTTPException(status_code=500, detail="Video search failed")
