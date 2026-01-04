# Shuttleport Backend - Pricing Models and Configuration (Database-driven)

from enum import Enum
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.db_models import Vehicle, FixedRoute, PricingConfig


class VehicleType(str, Enum):
    """Araç tipleri"""
    VITO = "vito"
    SPRINTER = "sprinter"
    LUXURY_SEDAN = "luxury_sedan"


class VehicleInfo(BaseModel):
    """Araç bilgileri"""
    type: VehicleType
    name: str
    name_tr: str
    capacity: int
    luggage_capacity: int
    capacity: int
    luggage_capacity: int
    image_url: str  # Kept for backward compatibility
    images: List[str] = []
    features: List[str]
    base_fare: float = Field(description="Başlangıç ücreti (TL)")
    per_km_rate: float = Field(description="KM başına ücret (TL)")
    airport_fee: float = Field(default=0, description="Havalimanı ek ücreti (TL)")


class PricingRequest(BaseModel):
    """Fiyat hesaplama request"""
    origin_lat: float
    origin_lng: float
    origin_name: str
    destination_lat: float
    destination_lng: float
    destination_name: str
    distance_km: float
    duration_minutes: int
    passenger_count: int = 1
    is_round_trip: bool = False
    is_airport_transfer: bool = False


class VehiclePricing(BaseModel):
    """Araç fiyatlandırma response"""
    vehicle_type: VehicleType
    vehicle_name: str
    vehicle_name_tr: str
    capacity: int
    base_price: float
    distance_price: float
    airport_fee: float
    subtotal: float
    round_trip_discount: float
    final_price: float
    final_price: float
    currency: str = "TRY"
    image_url: Optional[str] = None
    images: List[str] = []
    price_breakdown: Dict[str, float]


class PricingResponse(BaseModel):
    """Fiyat hesaplama response"""
    route_info: Dict[str, Any]
    vehicles: List[VehiclePricing]


def get_vehicle_configs() -> Dict[VehicleType, VehicleInfo]:
    """Get vehicle configurations from database"""
    db = SessionLocal()
    try:
        vehicles = db.query(Vehicle).filter(Vehicle.active == True).all()
        
        configs = {}
        for vehicle in vehicles:
            # Get pricing config for this vehicle type
            per_km_config = db.query(PricingConfig).filter(
                PricingConfig.config_key == f"per_km_rate_{vehicle.vehicle_type}"
            ).first()
            
            per_km_rate = float(per_km_config.config_value) if per_km_config else 12.0
            
            # Get base fare and airport fee from global configs
            base_fare_config = db.query(PricingConfig).filter(
                PricingConfig.config_key == "base_fare"
            ).first()
            airport_fee_config = db.query(PricingConfig).filter(
                PricingConfig.config_key == "airport_fee"
            ).first()
            
            base_fare = float(base_fare_config.config_value) if base_fare_config else 50.0
            airport_fee = float(airport_fee_config.config_value) if airport_fee_config else 100.0
            
            # Convert features JSON to list of strings
            features_list = []
            if vehicle.features and isinstance(vehicle.features, list):
                features_list = [f.get("text", "") for f in vehicle.features if isinstance(f, dict)]
            
            try:
                vehicle_type_enum = VehicleType(vehicle.vehicle_type)
            except ValueError:
                continue  # Skip unknown vehicle types
            
            # Determine images list
            images_list = []
            
            # Relation handling (vehicle.images is now a list of VehicleImage objects)
            if vehicle.images:
                for img_obj in vehicle.images:
                    # VehicleImage object has image_path attribute
                    path = img_obj.image_path
                    if path.startswith("http"):
                        images_list.append(path)
                    else:
                        images_list.append(f"http://localhost:8000/static/{path}")
            
            # Fallback to single image path if no list
            if not images_list and vehicle.image_path:
                 if vehicle.image_path.startswith("http"):
                    images_list.append(vehicle.image_path)
                 else:
                    images_list.append(f"http://localhost:8000/static/{vehicle.image_path}")
            
            # Fallback to default if nothing else
            if not images_list:
                images_list.append(f"/images/{vehicle.vehicle_type}.jpg")
            
            # Primary image for backward compatibility
            image_url = images_list[0] if images_list else ""

            configs[vehicle_type_enum] = VehicleInfo(
                type=vehicle_type_enum,
                name=vehicle.name_en,
                name_tr=vehicle.name_tr,
                capacity=vehicle.capacity_max,
                luggage_capacity=vehicle.baggage_capacity,
                image_url=image_url,
                images=images_list,
                features=features_list,
                base_fare=base_fare,
                per_km_rate=per_km_rate,
                airport_fee=airport_fee
            )
        
        return configs
    finally:
        db.close()


def normalize_location_name(name: str) -> str:
    """Konum adını normalize et (karşılaştırma için)"""
    return name.lower().replace("ı", "i").replace("ğ", "g").replace("ş", "s").replace("ç", "c").replace("ü", "u").replace("ö", "o")


def check_fixed_route(origin: str, destination: str, db: Session = None) -> Optional[Dict[VehicleType, float]]:
    """Check if there's a fixed price route in database"""
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True
    
    try:
        origin_norm = normalize_location_name(origin)
        destination_norm = normalize_location_name(destination)
        
        # Query all fixed routes
        routes = db.query(FixedRoute).filter(FixedRoute.active == True).all()
        
        # Find matching route
        for route in routes:
            route_origin_norm = normalize_location_name(route.origin)
            route_dest_norm = normalize_location_name(route.destination)
            
            # Check forward direction
            if route_origin_norm in origin_norm and route_dest_norm in destination_norm:
                # Get all vehicle prices for this route
                all_routes = db.query(FixedRoute).filter(
                    FixedRoute.origin == route.origin,
                    FixedRoute.destination == route.destination,
                    FixedRoute.active == True
                ).all()
                
                prices = {}
                for r in all_routes:
                    vehicle = db.query(Vehicle).filter(Vehicle.id == r.vehicle_id).first()
                    if vehicle:
                        try:
                            vehicle_type = VehicleType(vehicle.vehicle_type)
                            # Apply discount if any
                            final_price = float(r.price)
                            if r.discount_percent and r.discount_percent > 0:
                                final_price = final_price * (1 - float(r.discount_percent) / 100)
                            prices[vehicle_type] = final_price
                        except ValueError:
                            continue
                
                return prices if prices else None
            
            # Check reverse direction
            if route_dest_norm in origin_norm and route_origin_norm in destination_norm:
                # Same logic for reverse
                all_routes = db.query(FixedRoute).filter(
                    FixedRoute.origin == route.origin,
                    FixedRoute.destination == route.destination,
                    FixedRoute.active == True
                ).all()
                
                prices = {}
                for r in all_routes:
                    vehicle = db.query(Vehicle).filter(Vehicle.id == r.vehicle_id).first()
                    if vehicle:
                        try:
                            vehicle_type = VehicleType(vehicle.vehicle_type)
                            final_price = float(r.price)
                            if r.discount_percent and r.discount_percent > 0:
                                final_price = final_price * (1 - float(r.discount_percent) / 100)
                            prices[vehicle_type] = final_price
                        except ValueError:
                            continue
                
                return prices if prices else None
        
        return None
    finally:
        if should_close:
            db.close()


def calculate_vehicle_price(
    vehicle_config: VehicleInfo,
    distance_km: float,
    is_round_trip: bool,
    is_airport_transfer: bool,
    fixed_price: Optional[float] = None
) -> VehiclePricing:
    """Tek bir araç için fiyat hesapla (minimum fiyat kontrolü ile)"""
    
    if fixed_price:
        # Sabit fiyatlı rota
        base_price = 0
        distance_price = fixed_price
        airport_fee = 0  # Sabit fiyata dahil
    else:
        # Mesafe bazlı fiyatlandırma
        base_price = vehicle_config.base_fare
        distance_price = distance_km * vehicle_config.per_km_rate
        airport_fee = vehicle_config.airport_fee if is_airport_transfer else 0
    
    subtotal = base_price + distance_price + airport_fee
    
    # Round-trip indirimi ve minimum fiyat (database'den al)
    db = SessionLocal()
    try:
        discount_config = db.query(PricingConfig).filter(
            PricingConfig.config_key == "round_trip_discount"
        ).first()
        discount_percent = float(discount_config.config_value) if discount_config else 10.0
        
        # Minimum fare kontrolü (araç tipine göre)
        vehicle_type_str = vehicle_config.type.value
        minimum_fare_config = db.query(PricingConfig).filter(
            PricingConfig.config_key == f"minimum_fare_{vehicle_type_str}"
        ).first()
        minimum_fare = float(minimum_fare_config.config_value) if minimum_fare_config else 0
    finally:
        db.close()
    
    round_trip_discount = subtotal * (discount_percent / 100) if is_round_trip else 0
    
    final_price = subtotal - round_trip_discount
    
    # Round-trip ise çift yön hesapla
    if is_round_trip and not fixed_price:
        final_price = final_price * 2 - round_trip_discount
    
    # Minimum fiyat kontrolü (sadece dinamik fiyatlandırmada)
    minimum_applied = False
    if not fixed_price and minimum_fare > 0:
        if final_price < minimum_fare:
            final_price = minimum_fare
            minimum_applied = True
    
    return VehiclePricing(
        vehicle_type=vehicle_config.type,
        vehicle_name=vehicle_config.name,
        vehicle_name_tr=vehicle_config.name_tr,
        capacity=vehicle_config.capacity,
        base_price=base_price,
        distance_price=distance_price,
        airport_fee=airport_fee,
        subtotal=subtotal,
        round_trip_discount=round_trip_discount,
        final_price=round(final_price, 2),
        image_url=vehicle_config.image_url,
        images=vehicle_config.images,
        price_breakdown={
            "base_fare": base_price,
            "distance_charge": distance_price,
            "airport_fee": airport_fee,
            "subtotal": subtotal,
            "discount": round_trip_discount,
            "minimum_applied": minimum_fare if minimum_applied else 0,
            "final": round(final_price, 2)
        }
    )
