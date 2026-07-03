from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """Heartbeat check endpoint."""
    return {"status": "healthy"}

@router.get("/api/v1/health")
async def api_health_check():
    """Versioned API heartbeat check endpoint."""
    return {"status": "healthy"}
