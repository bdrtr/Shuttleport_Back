"""
Maps API schemas for requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class DistanceRequest(BaseModel):
    """Request schema for distance calculation"""
    origin_lat: float = Field(..., description="Origin latitude")
    origin_lng: float = Field(..., description="Origin longitude")
    destination_lat: float = Field(..., description="Destination latitude")
    destination_lng: float = Field(..., description="Destination longitude")
    
    class Config:
        json_schema_extra = {
            "example": {
                "origin_lat": 41.0082,
                "origin_lng": 28.9784,
                "destination_lat": 40.9829,
                "destination_lng": 29.0208
            }
        }


class DistanceResponse(BaseModel):
    """Response schema for distance calculation"""
    distance_km: float = Field(..., description="Distance in kilometers")
    distance_text: str = Field(..., description="Formatted distance text")
    duration_minutes: int = Field(..., description="Duration in minutes")
    duration_text: str = Field(..., description="Formatted duration text")
    origin_address: str = Field(..., description="Origin address")
    destination_address: str = Field(..., description="Destination address")


class PlaceSearchRequest(BaseModel):
    """Request schema for place search"""
    query: str = Field(..., min_length=1, description="Search query")
    location_lat: Optional[float] = Field(None, description="User's latitude for proximity")
    location_lng: Optional[float] = Field(None, description="User's longitude for proximity")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Istanbul Airport",
                "location_lat": 41.0082,
                "location_lng": 28.9784
            }
        }


class Place(BaseModel):
    """Place information"""
    place_id: str
    name: str
    address: str
    lat: float
    lng: float


class PlaceSearchResponse(BaseModel):
    """Response schema for place search"""
    places: List[Place] = Field(default_factory=list)


class MapsKeyResponse(BaseModel):
    """Response schema for Google Maps API key"""
    api_key: str
