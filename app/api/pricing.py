# Shuttleport Backend - Pricing API Endpoints (Database-driven)

from fastapi import APIRouter, HTTPException
from typing import List
from app.models.pricing import (
    VehicleType, VehicleInfo, PricingRequest, PricingResponse,
    VehiclePricing, get_vehicle_configs,
    check_fixed_route, calculate_vehicle_price
)
from app.database import SessionLocal
from app.models.db_models import FixedRoute, Vehicle

router = APIRouter(prefix="/api/pricing", tags=["pricing"])


@router.get("/vehicles", response_model=List[VehicleInfo])
async def get_vehicles():
    """Tüm araç tiplerini ve özelliklerini döndür (database'den)"""
    vehicle_configs = get_vehicle_configs()
    return list(vehicle_configs.values())


@router.post("/calculate", response_model=PricingResponse)
async def calculate_pricing(request: PricingRequest):
    """
    Transfer için fiyat hesapla (database-driven)
    - Mesafe bazlı hesaplama
    - Sabit rotalar için özel fiyatlar (database'den)
    - Round-trip indirimi (database config'den)
    - Havalimanı transferi ek ücreti
    """
    
    # Get vehicle configs from database
    vehicle_configs = get_vehicle_configs()
    
    # Sabit fiyatlı rota kontrolü (database'den)
    db = SessionLocal()
    try:
        fixed_route_prices = check_fixed_route(request.origin_name, request.destination_name, db)
    finally:
        db.close()
    
    vehicles_pricing = []
    
    for vehicle_type, vehicle_config in vehicle_configs.items():
        # Yolcu kapasitesi kontrolü
        if request.passenger_count > vehicle_config.capacity:
            continue  # Bu araç yolcu sayısını taşıyamaz
        
        # Sabit fiyat varsa kullan (database'den gelen)
        fixed_price = None
        if fixed_route_prices:
            fixed_price = fixed_route_prices.get(vehicle_type)
        
        # Fiyat hesapla
        pricing = calculate_vehicle_price(
            vehicle_config=vehicle_config,
            distance_km=request.distance_km,
            is_round_trip=request.is_round_trip,
            is_airport_transfer=request.is_airport_transfer,
            fixed_price=fixed_price
        )
        
        vehicles_pricing.append(pricing)
    
    if not vehicles_pricing:
        raise HTTPException(
            status_code=400,
            detail=f"Yolcu sayısı ({request.passenger_count}) için uygun araç bulunamadı"
        )
    
    # Fiyata göre sırala (en ucuzdan en pahalıya)
    vehicles_pricing.sort(key=lambda x: x.final_price)
    
    return PricingResponse(
        route_info={
            "origin": request.origin_name,
            "destination": request.destination_name,
            "distance_km": request.distance_km,
            "duration_minutes": request.duration_minutes,
            "is_round_trip": request.is_round_trip,
            "is_airport_transfer": request.is_airport_transfer,
            "is_fixed_route": fixed_route_prices is not None
        },
        vehicles=vehicles_pricing
    )


@router.get("/fixed-routes")
async def get_fixed_routes():
    """Sabit fiyatlı popüler rotaları döndür (database'den)"""
    db = SessionLocal()
    try:
        routes_dict = {}
        
        # Get all active fixed routes from database
        fixed_routes = db.query(FixedRoute).filter(FixedRoute.active == True).all()
        
        for route in fixed_routes:
            # Get vehicle info
            vehicle = db.query(Vehicle).filter(Vehicle.id == route.vehicle_id).first()
            if not vehicle:
                continue
            
            # Create route key
            route_key = (route.origin, route.destination)
            
            if route_key not in routes_dict:
                routes_dict[route_key] = {
                    "origin": route.origin.title(),
                    "destination": route.destination.title(),
                    "prices": {}
                }
            
            # Add price for this vehicle type
            final_price = float(route.price)
            if route.discount_percent and route.discount_percent > 0:
                final_price = final_price * (1 - float(route.discount_percent) / 100)
            
            routes_dict[route_key]["prices"][vehicle.vehicle_type] = final_price
        
        return {"routes": list(routes_dict.values())}
    finally:
        db.close()
