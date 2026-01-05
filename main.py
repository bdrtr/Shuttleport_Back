from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx
import os
from contextlib import asynccontextmanager
import time
from sqlalchemy.exc import OperationalError
from app.database import engine, Base
from app.models import db_models # Ensure models are loaded
from app.api import pricing, exchange_rates
from app.admin.admin_panel import setup_admin
from app.services.init_db import init_db_data

# Load environment variables
load_dotenv()

# Google Maps API Key
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Static files with caching headers
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response

class CacheStaticFiles(StaticFiles):
    def file_response(self, *args, **kwargs):
        response = super().file_response(*args, **kwargs)
        # Cache for 1 year (31536000 seconds)
        response.headers["Cache-Control"] = "public, max-age=31536000"
        return response

# Ensure static directory exists
os.makedirs("static/images", exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events - startup and shutdown logic
    """
    # Startup: Check DB and create tables
    print("🚀 Starting up: Checking database connection...")
    retries = 5
    while retries > 0:
        try:
            # Try to create tables (this checks connection implicitly)
            Base.metadata.create_all(bind=engine)
            print("✅ Database connection successful. Tables verified/created.")
            
            # Seed initial data
            try:
                print("🌱 Checking/Seeding initial data...")
                init_db_data()
            except Exception as e:
                print(f"⚠️ Data seeding warning: {e}")
                
            break
        except OperationalError as e:
            retries -= 1
            print(f"⚠️ Database connection failed. Retrying in 2s... ({retries} left)")
            print(f"Error: {e}")
            time.sleep(2)
    
    if retries == 0:
        print("❌ CRITICAL: Could not connect to database after retries.")
    
    yield
    
    # Shutdown logic
    print("👋 Shutting down...")


def create_application() -> FastAPI:
    """
    Create and configure FastAPI application
    """
    app = FastAPI(
        title="Shuttleport API",
        description="API for Shuttleport transfer booking system",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify exact domains
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Static Files
    app.mount("/static", CacheStaticFiles(directory="static"), name="static")

    # Include routers
    app.include_router(pricing.router)
    app.include_router(exchange_rates.router)
    
    # Setup Admin
    setup_admin(app)
    
    return app

# Create app instance
app = create_application()

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
