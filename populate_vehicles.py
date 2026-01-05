from app.database import SessionLocal
from app.models.db_models import Vehicle

def populate_vehicles():
    db = SessionLocal()
    
    vehicles = [
        {
            "vehicle_type": "vito",
            "name_en": "Mercedes Vito",
            "name_tr": "Mercedes Vito",
            "capacity_min": 1,
            "capacity_max": 7,
            "baggage_capacity": 5,
            "base_multiplier": 1.0,
            "features": [
                {"icon": "❄️", "text": "Klima"},
                {"icon": "💺", "text": "Deri Koltuk"},
                {"icon": "🔌", "text": "USB Şarj"},
                {"icon": "💧", "text": "Ücretsiz Su"}
            ],
            "image_path": "images/vito.jpg"
        },
        {
            "vehicle_type": "sprinter",
            "name_en": "Mercedes Sprinter",
            "name_tr": "Mercedes Sprinter",
            "capacity_min": 1,
            "capacity_max": 16,
            "baggage_capacity": 15,
            "base_multiplier": 1.5,
            "features": [
                {"icon": "❄️", "text": "Klima"},
                {"icon": "👥", "text": "Geniş İç Hacim"},
                {"icon": "🎤", "text": "Mikrofon"},
                {"icon": "📺", "text": "TV Ünitesi"}
            ],
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
            "features": [
                {"icon": "🌟", "text": "VIP Hizmet"},
                {"icon": "📶", "text": "Wi-Fi"},
                {"icon": "❄️", "text": "Klima"},
                {"icon": "👔", "text": "Özel Şoför"}
            ],
            "image_path": "images/sedan.jpg"
        }
    ]

    print("Populating Vehicles...")
    
    try:
        for v_data in vehicles:
            existing = db.query(Vehicle).filter(Vehicle.vehicle_type == v_data["vehicle_type"]).first()
            
            if existing:
                print(f"Updating {v_data['name_en']}...")
                for key, value in v_data.items():
                    setattr(existing, key, value)
            else:
                print(f"Creating {v_data['name_en']}...")
                new_vehicle = Vehicle(**v_data)
                db.add(new_vehicle)
        
        db.commit()
        print("Successfully populated vehicles.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_vehicles()
