"""
Health check endpoints
"""
from fastapi import APIRouter, HTTPException
from loguru import logger

from app.models.schemas import HealthResponse
from app.database.qdrant_client import qdrant_manager

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check Qdrant connection
        qdrant_healthy = await qdrant_manager.health_check()
        
        if not qdrant_healthy:
            raise HTTPException(status_code=503, detail="Qdrant connection failed")
        
        return HealthResponse(
            status="healthy",
            version="1.0.0"
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@router.get("/health/qdrant")
async def qdrant_health_check():
    """Qdrant specific health check"""
    try:
        is_healthy = await qdrant_manager.health_check()
        
        if is_healthy:
            return {"status": "healthy", "service": "qdrant"}
        else:
            raise HTTPException(status_code=503, detail="Qdrant is not healthy")
            
    except Exception as e:
        logger.error(f"Qdrant health check failed: {e}")
        raise HTTPException(status_code=503, detail="Qdrant health check failed")
