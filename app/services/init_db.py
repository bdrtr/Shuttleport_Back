from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.db_models import PricingConfig, Vehicle, FixedRoute

def init_pricing_data(db: Session):
    """Initialize default pricing configuration if empty"""
    print("Checking Pricing Configurations...")
    
    configs = [
        # Global Settings
        {"key": "base_fare", "value": 50.00, "desc": "Baaslangic ucreti"},
        {"key": "airport_fee", "value": 150.00, "desc": "Havalimani karsilama/ekstra ucreti"},
        {"key": "round_trip_discount", "value": 10.00, "desc": "Gidis-donus indirim yuzdesi"},
        
        # Vehicle Specific Rates (Per KM)
        {"key": "per_km_rate_vito", "value": 25.00, "desc": "Vito KM basi ucret", "vehicle": "vito"},
        {"key": "per_km_rate_sprinter", "value": 35.00, "desc": "Sprinter KM basi ucret", "vehicle": "sprinter"},
        {"key": "per_km_rate_luxury_sedan", "value": 40.00, "desc": "Luks Sedan KM basi ucret", "vehicle": "luxury_sedan"},
        
        # Minimum Fares
        {"key": "minimum_fare", "value": 1200.00, "desc": "Minimum tasima ucreti (Global)"},
    ]

    for conf in configs:
        exists = db.query(PricingConfig).filter(PricingConfig.config_key == conf["key"]).first()
        if not exists:
            print(f"  -> Seeding {conf['key']} = {conf['value']}")
            new_conf = PricingConfig(
                config_key=conf["key"],
                config_value=conf["value"],
                description=conf.get("desc"),
                vehicle_type=conf.get("vehicle")
            )
            db.add(new_conf)
    db.commit()

def init_vehicle_data(db: Session):
    """Initialize default vehicles if empty"""
    print("Checking Vehicle Data...")
    
    from app.core.constants import FEATURE_DEFINITIONS
    
    def get_feat(key):
        if key in FEATURE_DEFINITIONS:
            icon, text = FEATURE_DEFINITIONS[key]
            return {"icon": icon, "text": text}
        return {"icon": "❓", "text": key}
    
    # Collections
    features_base = [get_feat("ac"), get_feat("water"), get_feat("usb"), get_feat("disinfection")]
    features_comfort = features_base + [get_feat("wifi"), get_feat("bluetooth")]
    features_vip = features_comfort + [get_feat("leather"), get_feat("meeting"), get_feat("table")]
    features_bus = [get_feat("ac"), get_feat("water"), get_feat("usb"), get_feat("tv"), get_feat("disinfection")]

    vehicles = [
        {
            "vehicle_type": "vito",
            "name_en": "Mercedes Vito",
            "name_tr": "Mercedes Vito",
            "capacity_min": 1,
            "capacity_max": 7,
            "baggage_capacity": 5,
            "base_multiplier": 1.0,
            "features": features_comfort,
            "image_path": "images/vito.jpg"
        },
        {
            "vehicle_type": "vito_vip",
            "name_en": "Mercedes Vito VIP",
            "name_tr": "Mercedes Vito VIP",
            "capacity_min": 1,
            "capacity_max": 6,
            "baggage_capacity": 5,
            "base_multiplier": 1.4,
            "features": features_vip,
            "image_path": "images/vito_vip.jpg"
        },
        {
            "vehicle_type": "sprinter",
            "name_en": "Mercedes Sprinter",
            "name_tr": "Mercedes Sprinter",
            "capacity_min": 1,
            "capacity_max": 16,
            "baggage_capacity": 15,
            "base_multiplier": 1.5,
            "features": features_bus,
            "image_path": "images/sprinter.jpg"
        },
        {
            "vehicle_type": "luxury_sedan",
            "name_en": "Luxury Sedan",
            "name_tr": "Lüks Sedan",
            "capacity_min": 1,
            "capacity_max": 3,
            "baggage_capacity": 3,
            "base_multiplier": 2.0,
            "features": features_vip + [get_feat("tv"), get_feat("fridge")],
            "image_path": "images/sedan.jpg"
        }
    ]

    for v_data in vehicles:
        exists = db.query(Vehicle).filter(Vehicle.vehicle_type == v_data["vehicle_type"]).first()
        if not exists:
            print(f"  -> Seeding vehicle: {v_data['name_en']}")
            new_vehicle = Vehicle(**v_data)
            db.add(new_vehicle)
    db.commit()

def init_routes_data(db: Session):
    """Initialize sample fixed routes"""
    print("Checking Fixed Routes...")
    
    from app.core.constants import ISTANBUL_LOCATIONS
    
    # Valid vehicle types must exist first
    vito = db.query(Vehicle).filter(Vehicle.vehicle_type == "vito").first()
    sprinter = db.query(Vehicle).filter(Vehicle.vehicle_type == "sprinter").first()
    
    if not vito:
        return

    # Use constants for locations to ensure match with Admin Panel
    loc_ist = ISTANBUL_LOCATIONS[0][0]
    loc_saw = ISTANBUL_LOCATIONS[1][0]
    loc_sultanahmet = ISTANBUL_LOCATIONS[2][0]
    loc_taksim = ISTANBUL_LOCATIONS[3][0]
    loc_besiktas = ISTANBUL_LOCATIONS[4][0]
    loc_kadikoy = ISTANBUL_LOCATIONS[5][0]

    routes = [
        # IST (Prices based on competitor - 50 TL)
        {"origin": loc_ist, "destination": loc_sultanahmet, "price": 1764, "vehicle_id": vito.id, "active": True},
        {"origin": loc_ist, "destination": loc_taksim, "price": 1619, "vehicle_id": vito.id, "active": True},
        {"origin": loc_ist, "destination": loc_besiktas, "price": 1690, "vehicle_id": vito.id, "active": True},
        {"origin": loc_ist, "destination": loc_kadikoy, "price": 2050, "vehicle_id": vito.id, "active": True},
        
        # SAW
        {"origin": loc_saw, "destination": loc_sultanahmet, "price": 1900, "vehicle_id": vito.id, "active": True},
        {"origin": loc_saw, "destination": loc_taksim, "price": 1830, "vehicle_id": vito.id, "active": True},
    ]
    
    # Add sprinter routes (approx 1.5x price)
    if sprinter:
        for r in routes[:4]: # First 4 routes for Sprinter too
            routes.append({
                "origin": r["origin"],
                "destination": r["destination"],
                "price": int(r["price"] * 1.5),
                "vehicle_id": sprinter.id,
                "active": True
            })

    for r_data in routes:
        # Check by composite key using filter
        exists = db.query(FixedRoute).filter(
            FixedRoute.origin == r_data["origin"],
            FixedRoute.destination == r_data["destination"],
            FixedRoute.vehicle_id == r_data["vehicle_id"]
        ).first()
        
        if not exists:
            print(f"  -> Seeding route: {r_data['origin']} -> {r_data['destination']}")
            new_route = FixedRoute(**r_data)
            db.add(new_route)
    
    db.commit()

def init_db_data():
    """Main initialization entry point"""
    db = SessionLocal()
    try:
        init_pricing_data(db)
        init_vehicle_data(db)
        init_routes_data(db)
        print("✅ Database data initialization executed.")
    except Exception as e:
        print(f"❌ Error initializing data: {e}")
        db.rollback()
    finally:
        db.close()
