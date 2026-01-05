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
    
    # Fetch all vehicle types
    vehicles_map = {v.vehicle_type: v for v in db.query(Vehicle).all()}
    vito = vehicles_map.get("vito")
    
    if not vito:
        return

    # Use constants for locations to ensure match with Admin Panel
    loc_ist = ISTANBUL_LOCATIONS[0][0]
    loc_saw = ISTANBUL_LOCATIONS[1][0]
    loc_sultanahmet = ISTANBUL_LOCATIONS[2][0]
    loc_taksim = ISTANBUL_LOCATIONS[3][0]
    loc_besiktas = ISTANBUL_LOCATIONS[4][0]
    loc_kadikoy = ISTANBUL_LOCATIONS[5][0]

    from app.services.data_manager import DataManager
    
    # Try to load from Excel first
    excel_routes = DataManager.load_routes()
    base_routes = []
    
    if excel_routes:
        print(f"  -> Loaded {len(excel_routes)} routes from Excel file.")
        for r in excel_routes:
            # Only add if price is valid
            if r.get("price_vito"):
                base_routes.append({
                    "origin": r["origin"],
                    "destination": r["destination"],
                    "price": float(r["price_vito"]),
                    "active": True
                })
    
    if not base_routes:
        print("  -> No routes in Excel. Using defaults and saving to file...")
        base_routes = [
            # IST
            {"origin": loc_ist, "destination": loc_sultanahmet, "price": 1764, "active": True},
            {"origin": loc_ist, "destination": loc_taksim, "price": 1619, "active": True},
            {"origin": loc_ist, "destination": loc_besiktas, "price": 1690, "active": True},
            {"origin": loc_ist, "destination": loc_kadikoy, "price": 2050, "active": True},
            
            # SAW
            {"origin": loc_saw, "destination": loc_sultanahmet, "price": 1900, "active": True},
            {"origin": loc_saw, "destination": loc_taksim, "price": 1830, "active": True},
        ]
        
        # Save to Excel
        for r in base_routes:
            DataManager.save_route(r["origin"], r["destination"], r["price"])

    # Apply routes to Vito first
    final_routes = []
    for r in base_routes:
        r_copy = r.copy()
        r_copy["vehicle_id"] = vito.id
        final_routes.append(r_copy)

    # Generate routes for other vehicle types with specific multipliers
    # Goal: Avoid huge price gaps (like 9000 TL vs 3000 TL)
    multipliers = {
        "vito_vip": 1.25,      # ~2200 TL (Comfort Upgrade)
        "sprinter": 1.95,      # ~3440 TL (Capacity Upgrade - Matches Competitor - 50TL)
        "luxury_sedan": 2.5,   # ~4400 TL (Luxury Service)
    }

    for v_type, multiplier in multipliers.items():
        vehicle = vehicles_map.get(v_type)
        if vehicle:
            for r in base_routes:
                new_price = int(r["price"] * multiplier)
                final_routes.append({
                    "origin": r["origin"],
                    "destination": r["destination"],
                    "price": new_price,
                    "vehicle_id": vehicle.id,
                    "active": True
                })

    for r_data in final_routes:
        # Check by composite key using filter
        exists = db.query(FixedRoute).filter(
            FixedRoute.origin == r_data["origin"],
            FixedRoute.destination == r_data["destination"],
            FixedRoute.vehicle_id == r_data["vehicle_id"]
        ).first()
        
        if not exists:
            print(f"  -> Seeding route: {r_data['origin']} -> {r_data['destination']} ({r_data['price']}₺)")
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
