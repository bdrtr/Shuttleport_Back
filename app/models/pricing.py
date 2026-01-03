# Shuttleport Backend - Pricing Models and Configuration

from enum import Enum
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field


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
    image_url: str
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
    currency: str = "TRY"
    price_breakdown: Dict[str, float]


class PricingResponse(BaseModel):
    """Fiyat hesaplama response"""
    route_info: Dict[str, Any]
    vehicles: List[VehiclePricing]


# Araç konfigürasyonu
VEHICLE_CONFIGS = {
    VehicleType.VITO: VehicleInfo(
        type=VehicleType.VITO,
        name="Mercedes Vito VIP",
        name_tr="Mercedes Vito VIP",
        capacity=7,
        luggage_capacity=7,
        image_url="/images/mercedes-vito.jpg",
        features=["VIP İç Donanım", "Klima", "Wi-Fi", "Su İkramı"],
        base_fare=200.0,
        per_km_rate=15.0,
        airport_fee=50.0
    ),
    VehicleType.SPRINTER: VehicleInfo(
        type=VehicleType.SPRINTER,
        name="Mercedes Sprinter",
        name_tr="Mercedes Sprinter",
        capacity=15,
        luggage_capacity=15,
        image_url="/images/mercedes-sprinter-front-1.jpg",
        features=["Geniş İç Mekan", "Klima", "Wi-Fi", "TV", "Su İkramı"],
        base_fare=300.0,
        per_km_rate=20.0,
        airport_fee=75.0
    ),
    VehicleType.LUXURY_SEDAN: VehicleInfo(
        type=VehicleType.LUXURY_SEDAN,
        name="Luxury Sedan",
        name_tr="Lüks Sedan",
        capacity=3,
        luggage_capacity=3,
        image_url="/images/luxury-sedan.jpg",
        features=["Lüks Konfor", "Klima", "Wi-Fi"],
        base_fare=250.0,
        per_km_rate=18.0,
        airport_fee=60.0
    )
}

# Popüler rotalar için sabit fiyatlar (Zone-based pricing)
# Fiyatlar rakip siteden (istanbulshuttleport.com) ~50₺ daha düşük (rekabetçi strateji)
# Son güncelleme: 2026-01-03 (Rakip site fiyatları kontrol edildi)
FIXED_ROUTES = {
    # İstanbul Havalimanı - Merkez rotaları
    # Rakip fiyatları: Sultanahmet (Sedan: 2050₺, Vito: 2136₺, Sprinter: 2948₺)
    ("istanbul airport", "sultanahmet"): {
        VehicleType.LUXURY_SEDAN: 2000.0,  # Rakip: 2050₺ | Bizim: 2000₺ (50₺ ucuz)
        VehicleType.VITO: 2086.0,          # Rakip: 2136₺ | Bizim: 2086₺ (50₺ ucuz)
        VehicleType.SPRINTER: 2898.0       # Rakip: 2948₺ | Bizim: 2898₺ (50₺ ucuz)
    },
    # Rakip fiyatları: Taksim (Sedan: 1880₺, Vito: 1965₺, Sprinter: 2948₺)
    ("istanbul airport", "taksim"): {
        VehicleType.LUXURY_SEDAN: 1830.0,  # Rakip: 1880₺ | Bizim: 1830₺ (50₺ ucuz)
        VehicleType.VITO: 1915.0,          # Rakip: 1965₺ | Bizim: 1915₺ (50₺ ucuz)
        VehicleType.SPRINTER: 2898.0       # Rakip: 2948₺ | Bizim: 2898₺ (50₺ ucuz)
    },
    # Kadıköy için tahmini fiyatlar (mesafe daha uzun)
    ("istanbul airport", "kadıköy"): {
        VehicleType.LUXURY_SEDAN: 2100.0,
        VehicleType.VITO: 2200.0,
        VehicleType.SPRINTER: 3100.0
    },
    # Beşiktaş için tahmini fiyatlar
    ("istanbul airport", "beşiktaş"): {
        VehicleType.LUXURY_SEDAN: 1800.0,
        VehicleType.VITO: 1900.0,
        VehicleType.SPRINTER: 2800.0
    },
    # Rakip fiyatları: Avcılar (Sedan: 2435₺, Vito: 2564₺, Sprinter: 3333₺)
    ("istanbul airport", "avcılar"): {
        VehicleType.LUXURY_SEDAN: 2385.0,  # Rakip: 2435₺ | Bizim: 2385₺ (50₺ ucuz)
        VehicleType.VITO: 2514.0,          # Rakip: 2564₺ | Bizim: 2514₺ (50₺ ucuz)
        VehicleType.SPRINTER: 3283.0       # Rakip: 3333₺ | Bizim: 3283₺ (50₺ ucuz)
    },
    # Sabiha Gökçen Havalimanı rotaları (tahmini, genelde daha pahalı)
    ("sabiha gokcen airport", "sultanahmet"): {
        VehicleType.LUXURY_SEDAN: 2700.0,
        VehicleType.VITO: 2800.0,
        VehicleType.SPRINTER: 3900.0
    },
    ("sabiha gokcen airport", "taksim"): {
        VehicleType.LUXURY_SEDAN: 2600.0,
        VehicleType.VITO: 2700.0,
        VehicleType.SPRINTER: 3800.0
    },
    ("sabiha gokcen airport", "kadıköy"): {
        VehicleType.LUXURY_SEDAN: 2300.0,
        VehicleType.VITO: 2400.0,
        VehicleType.SPRINTER: 3300.0
    }
}


def normalize_location_name(name: str) -> str:
    """Konum adını normalize et (karşılaştırma için)"""
    return name.lower().replace("ı", "i").replace("ğ", "g").replace("ş", "s").replace("ç", "c").replace("ü", "u").replace("ö", "o")


def check_fixed_route(origin: str, destination: str) -> Optional[str]:
    """Sabit fiyatlı rota varsa route key döndür"""
    origin_norm = normalize_location_name(origin)
    destination_norm = normalize_location_name(destination)
    
    for (route_origin, route_dest) in FIXED_ROUTES.keys():
        # Route key'lerini de normalize et (Türkçe karakterler için)
        route_origin_norm = normalize_location_name(route_origin)
        route_dest_norm = normalize_location_name(route_dest)
        
        # Normalize edilmiş versiyonlarla kontrol et
        if route_origin_norm in origin_norm and route_dest_norm in destination_norm:
            return (route_origin, route_dest)
        # Ters yön kontrolü
        if route_dest_norm in origin_norm and route_origin_norm in destination_norm:
            return (route_dest, route_origin)
    
    return None


def calculate_vehicle_price(
    vehicle_config: VehicleInfo,
    distance_km: float,
    is_round_trip: bool,
    is_airport_transfer: bool,
    fixed_price: Optional[float] = None
) -> VehiclePricing:
    """Tek bir araç için fiyat hesapla"""
    
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
    
    # Round-trip indirimi (%10)
    round_trip_discount = subtotal * 0.10 if is_round_trip else 0
    
    final_price = subtotal - round_trip_discount
    
    # Round-trip ise çift yön hesapla
    if is_round_trip and not fixed_price:
        final_price = final_price * 2 - round_trip_discount
    
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
        price_breakdown={
            "base_fare": base_price,
            "distance_charge": distance_price,
            "airport_fee": airport_fee,
            "subtotal": subtotal,
            "discount": round_trip_discount,
            "final": round(final_price, 2)
        }
    )
