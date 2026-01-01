"""
Health check endpoints
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@router.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Shuttleport API'ye hoş geldiniz!"}
