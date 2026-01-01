"""
Maps API endpoints
"""
from fastapi import APIRouter, HTTPException
from app.schemas.maps import (
    DistanceRequest,
    DistanceResponse,
    PlaceSearchRequest,
    PlaceSearchResponse,
    MapsKeyResponse
)
from app.services.maps_service import maps_service
from app.core.exceptions import GoogleMapsAPIError

router = APIRouter()


@router.get("/maps-key", response_model=MapsKeyResponse)
async def get_maps_key():
    """
    Get Google Maps API key for frontend
    """
    try:
        return maps_service.get_api_key()
    except GoogleMapsAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/calculate-distance", response_model=DistanceResponse)
async def calculate_distance(request: DistanceRequest):
    """
    Calculate distance and duration between two points
    
    Uses Google Distance Matrix API to calculate driving distance and time.
    """
    try:
        return await maps_service.calculate_distance(request)
    except GoogleMapsAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/search-places", response_model=PlaceSearchResponse)
async def search_places(request: PlaceSearchRequest):
    """
    Search for places using Google Places API
    
    Optionally provide user location for proximity-based results.
    """
    try:
        return await maps_service.search_places(request)
    except GoogleMapsAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
