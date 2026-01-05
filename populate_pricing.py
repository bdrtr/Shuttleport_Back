from app.database import SessionLocal
from app.models.db_models import PricingConfig

def populate_configs():
    db = SessionLocal()
    
    # Defaults
    configs = [
        # Global Settings
        {"key": "base_fare", "value": 50.00, "desc": "Baaslangic ucreti"},
        {"key": "airport_fee", "value": 150.00, "desc": "Havalimani karsilama/ekstra ucreti"},
        {"key": "round_trip_discount", "value": 10.00, "desc": "Gidis-donus indirim yuzdesi"},
        
        # Vehicle Specific Rates (Per KM)
        {"key": "per_km_rate_vito", "value": 25.00, "desc": "Vito KM basi ucret", "vehicle": "vito"},
        {"key": "per_km_rate_sprinter", "value": 35.00, "desc": "Sprinter KM basi ucret", "vehicle": "sprinter"},
        {"key": "per_km_rate_luxury_sedan", "value": 40.00, "desc": "Luks Sedan KM basi ucret", "vehicle": "luxury_sedan"},
        
        # Minimum Fares (Ensure 1200 is set globally, can override per vehicle)
        {"key": "minimum_fare", "value": 1200.00, "desc": "Minimum tasima ucreti (Global)"},
    ]

    print("Populating Pricing Configurations...")
    
    try:
        for conf in configs:
            # Check existing
            existing = db.query(PricingConfig).filter(PricingConfig.config_key == conf["key"]).first()
            
            if existing:
                print(f"Updating {conf['key']}: {existing.config_value} -> {conf['value']}")
                existing.config_value = conf['value']
                existing.description = conf.get("desc")
                existing.vehicle_type = conf.get("vehicle")
            else:
                print(f"Creating {conf['key']} = {conf['value']}")
                new_conf = PricingConfig(
                    config_key=conf["key"],
                    config_value=conf["value"],
                    description=conf.get("desc"),
                    vehicle_type=conf.get("vehicle")
                )
                db.add(new_conf)
        
        db.commit()
        print("Successfully populated pricing configurations.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_configs()
