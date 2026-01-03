from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx
import os
from app.api import pricing
from app.admin.admin_panel import setup_admin

# .env dosyasını yükle
load_dotenv()

app = FastAPI(
    title="Shuttleport API",
    description="Backend API for Shuttleport - Transfer Booking Platform",
    version="0.1.0"
)

# CORS ayarları - Frontend ile iletişim için
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(pricing.router)

# Admin Panel (accessible at /admin)
setup_admin(app)

# Google Maps API Key
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


# Pydantic modelleri
class DistanceRequest(BaseModel):
    origin_lat: float
    origin_lng: float
    destination_lat: float
    destination_lng: float


class DistanceResponse(BaseModel):
    distance_km: float
    distance_text: str
    duration_minutes: int
    duration_text: str
    origin_address: str
    destination_address: str


class PlaceSearchRequest(BaseModel):
    query: str
    location_lat: float | None = None
    location_lng: float | None = None


@app.get("/")
async def root():
    return {"message": "Shuttleport API'ye hoş geldiniz!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/maps-key")
async def get_maps_key():
    """Frontend için Google Maps API key'i döndür"""
    if not GOOGLE_MAPS_API_KEY:
        raise HTTPException(status_code=500, detail="Google Maps API key yapılandırılmamış")
    return {"api_key": GOOGLE_MAPS_API_KEY}


@app.post("/api/calculate-distance", response_model=DistanceResponse)
async def calculate_distance(request: DistanceRequest):
    """
    İki konum arasındaki mesafeyi ve süreyi hesaplar
    Google Distance Matrix API kullanır
    """
    if not GOOGLE_MAPS_API_KEY:
        raise HTTPException(status_code=500, detail="Google Maps API key yapılandırılmamış")
    
    origin = f"{request.origin_lat},{request.origin_lng}"
    destination = f"{request.destination_lat},{request.destination_lng}"
    
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": origin,
        "destinations": destination,
        "mode": "driving",
        "language": "tr",
        "key": GOOGLE_MAPS_API_KEY
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()
    
    if data.get("status") != "OK":
        raise HTTPException(status_code=400, detail=f"Google API hatası: {data.get('status')}")
    
    element = data["rows"][0]["elements"][0]
    
    if element.get("status") != "OK":
        raise HTTPException(status_code=400, detail=f"Rota bulunamadı: {element.get('status')}")
    
    # Mesafeyi km'ye çevir (metre olarak gelir)
    distance_meters = element["distance"]["value"]
    distance_km = round(distance_meters / 1000, 1)
    
    # Süreyi dakikaya çevir (saniye olarak gelir)
    duration_seconds = element["duration"]["value"]
    duration_minutes = round(duration_seconds / 60)
    
    return DistanceResponse(
        distance_km=distance_km,
        distance_text=element["distance"]["text"],
        duration_minutes=duration_minutes,
        duration_text=element["duration"]["text"],
        origin_address=data["origin_addresses"][0],
        destination_address=data["destination_addresses"][0]
    )


@app.post("/api/search-places")
async def search_places(request: PlaceSearchRequest):
    """
    Google Places API ile konum arama
    """
    if not GOOGLE_MAPS_API_KEY:
        raise HTTPException(status_code=500, detail="Google Maps API key yapılandırılmamış")
    
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": request.query,
        "language": "tr",
        "key": GOOGLE_MAPS_API_KEY
    }
    
    # Eğer konum verilmişse, yakın sonuçları tercih et
    if request.location_lat and request.location_lng:
        params["location"] = f"{request.location_lat},{request.location_lng}"
        params["radius"] = "50000"  # 50km yarıçap
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()
    
    if data.get("status") not in ["OK", "ZERO_RESULTS"]:
        raise HTTPException(status_code=400, detail=f"Google API hatası: {data.get('status')}")
    
    places = []
    for place in data.get("results", [])[:10]:  # En fazla 10 sonuç
        places.append({
            "place_id": place.get("place_id"),
            "name": place.get("name"),
            "address": place.get("formatted_address"),
            "lat": place["geometry"]["location"]["lat"],
            "lng": place["geometry"]["location"]["lng"]
        })
    
    return {"places": places}
