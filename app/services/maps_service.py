"""
Maps service - Business logic for maps operations
"""
from app.schemas.maps import (
    DistanceRequest,
    DistanceResponse,
    PlaceSearchRequest,
    PlaceSearchResponse,
    Place,
    MapsKeyResponse
)
from app.utils.google_maps import google_maps_client
from app.core.config import settings
from app.core.exceptions import GoogleMapsAPIError


class MapsService:
    """Service for maps-related business logic"""
    
    def __init__(self):
        self.maps_client = google_maps_client
    
    async def calculate_distance(self, request: DistanceRequest) -> DistanceResponse:
        """
        Calculate distance and duration between two points
        
        Args:
            request: Distance calculation request
            
        Returns:
            Distance calculation response
        """
        result = await self.maps_client.calculate_distance_matrix(
            origin_lat=request.origin_lat,
            origin_lng=request.origin_lng,
            destination_lat=request.destination_lat,
            destination_lng=request.destination_lng
        )
        
        # Convert to response format
        distance_km = round(result["distance_meters"] / 1000, 1)
        duration_minutes = round(result["duration_seconds"] / 60)
        
        return DistanceResponse(
            distance_km=distance_km,
            distance_text=result["distance_text"],
            duration_minutes=duration_minutes,
            duration_text=result["duration_text"],
            origin_address=result["origin_address"],
            destination_address=result["destination_address"]
        )
    
    async def search_places(self, request: PlaceSearchRequest) -> PlaceSearchResponse:
        """
        Search for places
        
        Args:
            request: Place search request
            
        Returns:
            Place search response with list of places
        """
        location = None
        if request.location_lat and request.location_lng:
            location = (request.location_lat, request.location_lng)
        
        places_data = await self.maps_client.search_places(
            query=request.query,
            location=location
        )
        
        places = [Place(**place) for place in places_data]
        
        return PlaceSearchResponse(places=places)
    
    def get_api_key(self) -> MapsKeyResponse:
        """
        Get Google Maps API key for frontend
        
        Returns:
            API key response
        """
        if not settings.GOOGLE_MAPS_API_KEY:
            raise GoogleMapsAPIError("Google Maps API key not configured")
        
        return MapsKeyResponse(api_key=settings.GOOGLE_MAPS_API_KEY)


# Singleton instance
maps_service = MapsService()
