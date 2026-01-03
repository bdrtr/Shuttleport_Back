# Shuttleport Backend - Pricing API Endpoints

from fastapi import APIRouter, HTTPException
from typing import List
from app.models.pricing import (
    VehicleType, VehicleInfo, PricingRequest, PricingResponse,
    VehiclePricing, VEHICLE_CONFIGS, FIXED_ROUTES,
    check_fixed_route, calculate_vehicle_price
)

router = APIRouter(prefix="/api/pricing", tags=["pricing"])


@router.get("/vehicles", response_model=List[VehicleInfo])
async def get_vehicles():
    """Tüm araç tiplerini ve özelliklerini döndür"""
    return list(VEHICLE_CONFIGS.values())


@router.post("/calculate", response_model=PricingResponse)
async def calculate_pricing(request: PricingRequest):
    """
    Transfer için fiyat hesapla
    - Mesafe bazlı hesaplama
    - Sabit rotalar için özel fiyatlar
    - Round-trip indirimi
    - Havalimanı transferi ek ücreti
    """
    
    # Sabit fiyatlı rota kontrolü
    fixed_route_key = check_fixed_route(request.origin_name, request.destination_name)
    
    vehicles_pricing = []
    
    for vehicle_type, vehicle_config in VEHICLE_CONFIGS.items():
        # Yolcu kapasitesi kontrolü
        if request.passenger_count > vehicle_config.capacity:
            continue  # Bu araç yolcu sayısını taşıyamaz
        
        # Sabit fiyat varsa kullan
        fixed_price = None
        if fixed_route_key and fixed_route_key in FIXED_ROUTES:
            fixed_price = FIXED_ROUTES[fixed_route_key].get(vehicle_type)
        
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
            "is_fixed_route": fixed_route_key is not None
        },
        vehicles=vehicles_pricing
    )


@router.get("/fixed-routes")
async def get_fixed_routes():
    """Sabit fiyatlı popüler rotaları döndür"""
    routes = []
    for (origin, destination), prices in FIXED_ROUTES.items():
        routes.append({
            "origin": origin.title(),
            "destination": destination.title(),
            "prices": {
                vehicle_type.value: price
                for vehicle_type, price in prices.items()
            }
        })
    return {"routes": routes}
