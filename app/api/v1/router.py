"""
API v1 router - aggregates all v1 endpoints
"""
from fastapi import APIRouter
from app.api.v1.endpoints import health, maps

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(maps.router, tags=["maps"])
