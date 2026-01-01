"""
Google Maps API client and utilities
"""
import httpx
from typing import Dict, Any, List, Tuple
from app.core.config import settings
from app.core.exceptions import GoogleMapsAPIError


class GoogleMapsClient:
    """Client for Google Maps API interactions"""
    
    BASE_URL = "https://maps.googleapis.com/maps/api"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.GOOGLE_MAPS_API_KEY
        if not self.api_key:
            raise ValueError("Google Maps API key is required")
    
    async def calculate_distance_matrix(
        self,
        origin_lat: float,
        origin_lng: float,
        destination_lat: float,
        destination_lng: float
    ) -> Dict[str, Any]:
        """
        Calculate distance and duration between two points
        
        Args:
            origin_lat: Origin latitude
            origin_lng: Origin longitude
            destination_lat: Destination latitude
            destination_lng: Destination longitude
            
        Returns:
            Dictionary with distance and duration information
            
        Raises:
            GoogleMapsAPIError: If API request fails
        """
        origin = f"{origin_lat},{origin_lng}"
        destination = f"{destination_lat},{destination_lng}"
        
        url = f"{self.BASE_URL}/distancematrix/json"
        params = {
            "origins": origin,
            "destinations": destination,
            "mode": "driving",
            "language": "tr",
            "key": self.api_key
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as e:
            raise GoogleMapsAPIError(
                f"Failed to connect to Google Maps API: {str(e)}"
            )
        
        if data.get("status") != "OK":
            raise GoogleMapsAPIError(
                f"Google Maps API error: {data.get('status')}",
                details={"response": data}
            )
        
        element = data["rows"][0]["elements"][0]
        
        if element.get("status") != "OK":
            raise GoogleMapsAPIError(
                f"Route not found: {element.get('status')}",
                details={"element": element}
            )
        
        return {
            "distance_meters": element["distance"]["value"],
            "distance_text": element["distance"]["text"],
            "duration_seconds": element["duration"]["value"],
            "duration_text": element["duration"]["text"],
            "origin_address": data["origin_addresses"][0],
            "destination_address": data["destination_addresses"][0]
        }
    
    async def search_places(
        self,
        query: str,
        location: Tuple[float, float] = None,
        radius: int = 50000
    ) -> List[Dict[str, Any]]:
        """
        Search for places using Google Places API
        
        Args:
            query: Search query
            location: Optional (lat, lng) tuple for proximity search
            radius: Search radius in meters (default 50km)
            
        Returns:
            List of place dictionaries
            
        Raises:
            GoogleMapsAPIError: If API request fails
        """
        url = f"{self.BASE_URL}/place/textsearch/json"
        params = {
            "query": query,
            "language": "tr",
            "key": self.api_key
        }
        
        if location:
            params["location"] = f"{location[0]},{location[1]}"
            params["radius"] = str(radius)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as e:
            raise GoogleMapsAPIError(
                f"Failed to connect to Google Maps API: {str(e)}"
            )
        
        if data.get("status") not in ["OK", "ZERO_RESULTS"]:
            raise GoogleMapsAPIError(
                f"Google Maps API error: {data.get('status')}",
                details={"response": data}
            )
        
        places = []
        for place in data.get("results", [])[:10]:  # Limit to 10 results
            places.append({
                "place_id": place.get("place_id"),
                "name": place.get("name"),
                "address": place.get("formatted_address"),
                "lat": place["geometry"]["location"]["lat"],
                "lng": place["geometry"]["location"]["lng"]
            })
        
        return places


# Singleton instance
google_maps_client = GoogleMapsClient()
