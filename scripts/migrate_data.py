"""
Data migration script - Populate database with existing pricing data
Run this once to migrate hardcoded data to database
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal, engine, Base
from app.models.db_models import Vehicle, FixedRoute, PricingConfig
from app.models.pricing import VehicleType, FIXED_ROUTES

def migrate_vehicles():
    """Migrate vehicle data to database"""
    db = SessionLocal()
    
    vehicles_data = [
        {
            "vehicle_type": VehicleType.LUXURY_SEDAN.value,
            "name_en": "Luxury Sedan",
            "name_tr": "Lüks Sedan",
            "capacity_min": 1,
            "capacity_max": 3,
            "baggage_capacity": 3,
            "features": [
                {"icon": "🧊", "text": "Soğuk İçecek"},
                {"icon": "✈️", "text": "Havalimanı Karşılama"},
                {"icon": "❌", "text": "Ücretsiz İptal"}
            ],
            "base_multiplier": 1.0,
            "active": True
        },
        {
            "vehicle_type": VehicleType.VITO.value,
            "name_en": "Mercedes Vito VIP",
            "name_tr": "Mercedes Vito VIP",
            "capacity_min": 1,
            "capacity_max": 7,
            "baggage_capacity": 7,
            "features": [
                {"icon": "🧊", "text": "Soğuk İçecek"},
                {"icon": "✈️", "text": "Havalimanı Karşılama"},
                {"icon": "❌", "text": "Ücretsiz İptal"}
            ],
            "base_multiplier": 1.05,
            "active": True
        },
        {
            "vehicle_type": VehicleType.SPRINTER.value,
            "name_en": "Mercedes Sprinter",
            "name_tr": "Mercedes Sprinter",
            "capacity_min": 1,
            "capacity_max": 15,
            "baggage_capacity": 15,
            "features": [
                {"icon": "🧊", "text": "Soğuk İçecek"},
                {"icon": "✈️", "text": "Havalimanı Karşılama"},
                {"icon": "❌", "text": "Ücretsiz İptal"}
            ],
            "base_multiplier": 1.45,
            "active": True
        }
    ]
    
    for vehicle_data in vehicles_data:
        # Check if vehicle already exists
        existing = db.query(Vehicle).filter(Vehicle.vehicle_type == vehicle_data["vehicle_type"]).first()
        if not existing:
            vehicle = Vehicle(**vehicle_data)
            db.add(vehicle)
            print(f"✅ Added vehicle: {vehicle_data['name_en']}")
        else:
            print(f"ℹ️  Vehicle already exists: {vehicle_data['name_en']}")
    
    db.commit()
    db.close()
    print("✅ Vehicles migration complete!")


def migrate_fixed_routes():
    """Migrate fixed routes from FIXED_ROUTES dict to database"""
    db = SessionLocal()
    
    # Get vehicle IDs
    vehicles = {v.vehicle_type: v.id for v in db.query(Vehicle).all()}
    
    # Map VehicleType enum to vehicle IDs
    vehicle_type_map = {
        VehicleType.LUXURY_SEDAN: vehicles.get(VehicleType.LUXURY_SEDAN.value),
        VehicleType.VITO: vehicles.get(VehicleType.VITO.value),
        VehicleType.SPRINTER: vehicles.get(VehicleType.SPRINTER.value)
    }
    
    # Competitor notes for reference
    route_notes = {
        ("istanbul airport", "sultanahmet"): {
            VehicleType.LUXURY_SEDAN: "Rakip: 2050₺ | Bizim: 2000₺ (50₺ ucuz)",
            VehicleType.VITO: "Rakip: 2136₺ | Bizim: 2086₺ (50₺ ucuz)",
            VehicleType.SPRINTER: "Rakip: 2948₺ | Bizim: 2898₺ (50₺ ucuz)"
        },
        ("istanbul airport", "taksim"): {
            VehicleType.LUXURY_SEDAN: "Rakip: 1880₺ | Bizim: 1830₺ (50₺ ucuz)",
            VehicleType.VITO: "Rakip: 1965₺ | Bizim: 1915₺ (50₺ ucuz)",
            VehicleType.SPRINTER: "Rakip: 2948₺ | Bizim: 2898₺ (50₺ ucuz)"
        },
        ("istanbul airport", "avcılar"): {
            VehicleType.LUXURY_SEDAN: "Rakip: 2435₺ | Bizim: 2385₺ (50₺ ucuz)",
            VehicleType.VITO: "Rakip: 2564₺ | Bizim: 2514₺ (50₺ ucuz)",
            VehicleType.SPRINTER: "Rakip: 3333₺ | Bizim: 3283₺ (50₺ ucuz)"
        }
    }
    
    count = 0
    for (origin, destination), prices in FIXED_ROUTES.items():
        for vehicle_type, price in prices.items():
            vehicle_id = vehicle_type_map.get(vehicle_type)
            if not vehicle_id:
                continue
            
            # Check if route already exists
            existing = db.query(FixedRoute).filter(
                FixedRoute.origin == origin,
                FixedRoute.destination == destination,
                FixedRoute.vehicle_id == vehicle_id
            ).first()
            
            if not existing:
                notes = route_notes.get((origin, destination), {}).get(vehicle_type, "")
                route = FixedRoute(
                    origin=origin,
                    destination=destination,
                    vehicle_id=vehicle_id,
                    price=float(price),
                    notes=notes,
                    active=True
                )
                db.add(route)
                count += 1
                print(f"✅ Added route: {origin} → {destination} ({vehicle_type.value}): {price}₺")
    
    db.commit()
    db.close()
    print(f"✅ Fixed routes migration complete! Added {count} routes.")


def migrate_pricing_config():
    """Migrate pricing configuration parameters"""
    db = SessionLocal()
    
    config_data = [
        {"config_key": "base_fare", "config_value": 50.0, "description": "Base fare for all trips"},
        {"config_key": "per_km_rate_sedan", "config_value": 12.0, "description": "Per km rate for Luxury Sedan"},
        {"config_key": "per_km_rate_vito", "config_value": 15.0, "description": "Per km rate for Mercedes Vito"},
        {"config_key": "per_km_rate_sprinter", "config_value": 20.0, "description": "Per km rate for Mercedes Sprinter"},
        {"config_key": "airport_fee", "config_value": 100.0, "description": "Additional fee for airport transfers"},
        {"config_key": "round_trip_discount", "config_value": 10.0, "description": "Discount percentage for round trips"},
    ]
    
    for config in config_data:
        existing = db.query(PricingConfig).filter(PricingConfig.config_key == config["config_key"]).first()
        if not existing:
            pricing_config = PricingConfig(**config)
            db.add(pricing_config)
            print(f"✅ Added config: {config['config_key']} = {config['config_value']}")
        else:
            print(f"ℹ️  Config already exists: {config['config_key']}")
    
    db.commit()
    db.close()
    print("✅ Pricing config migration complete!")


if __name__ == "__main__":
    print("🚀 Starting data migration...")
    print("")
    
    print("📊 Migrating vehicles...")
    migrate_vehicles()
    print("")
    
    print("🛣️ Migrating fixed routes...")
    migrate_fixed_routes()
    print("")
    
    print("⚙️ Migrating pricing config...")
    migrate_pricing_config()
    print("")
    
    print("🎉 Data migration complete!")
    print("")
    print("You can now use the database instead of hardcoded values!")
