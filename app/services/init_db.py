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
    """
    Initialize fixed routes: STRICT LOAD from Excel.
    The Excel file (istanbul_transfer.xlsx) is the Single Source of Truth.
    Existing DB data is CLEARED and re-populated from Excel on startup.
    If Excel file doesn't exist, no routes are loaded.
    """
    import os
    from app.services.data_manager import DataManager
    
    excel_path = "static/istanbul_transfer.xlsx"
    
    # Check if Excel file exists
    if not os.path.exists(excel_path):
        print("⚠️  No Excel file found. Skipping route initialization.")
        return
    
    print("Initializing Routes from Excel (Strict Mode)...")
    
    # 1. Load Vehicles Map
    vehicles_map = {v.vehicle_type: v for v in db.query(Vehicle).all()}
    
    # Excel Column Key -> Vehicle Type Key
    type_map = {
        "price_vito": "vito",
        "price_sedan": "sedan",
        "price_sprinter": "sprinter",
        "price_vitovip": "vito_vip" 
    }
    
    # 2. Strict Sync: CLEAR existing routes first
    # This ensures if user removes a row in Excel, it's gone from DB.
    deleted_count = db.query(FixedRoute).delete()
    db.commit()
    print(f"  -> Cleared {deleted_count} existing routes from DB to sync with Excel.")
    
    # 3. Load Excel Data
    excel_routes = DataManager.load_routes()
    
    if not excel_routes:
        print("  -> Excel file is empty! Database routes will be empty.")
        return

    print(f"  -> Loading {len(excel_routes)} routes from Excel...")
    
    count = 0
    for r in excel_routes:
        origin = r["origin"]
        destination = r["destination"]
        
        for price_key, vehicle_type in type_map.items():
            price_val = r.get(price_key)
            
            # Ensure vehicle exists
            vehicle = vehicles_map.get(vehicle_type)
            if not vehicle:
                continue

            # Only add if price is valid (>1.0)
            if price_val and price_val > 1.0:
                 new_route = FixedRoute(
                    origin=origin,
                    destination=destination,
                    vehicle_id=vehicle.id,
                    price=price_val,
                    
                    # Extra Params from Excel
                    active=r.get("active", True),
                    discount_percent=r.get("discount", 0),
                    competitor_price=r.get("comp_price", None),
                    notes=r.get("notes", "")
                )
                 db.add(new_route)
                 count += 1
    
    db.commit()
    print(f"✅ Excel Sync Complete. Imported {count} price entries.")

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
