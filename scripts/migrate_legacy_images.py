from app.models.db_models import VehicleImage, Vehicle
from app.database import SessionLocal

def migrate_images():
    db = SessionLocal()
    try:
        vehicles = db.query(Vehicle).all()
        print(f"Checking {len(vehicles)} vehicles for legacy images...")
        
        for v in vehicles:
            # Check deprecated image_path
            if v.image_path:
                print(f"Migrating image_path for Vehicle {v.id}: {v.image_path}")
                # Create VehicleImage
                new_img = VehicleImage(vehicle_id=v.id, image_path=v.image_path)
                db.add(new_img)
            
            # Check deprecated images_json
            if v.images_json and isinstance(v.images_json, list):
                print(f"Migrating images_json for Vehicle {v.id}: {v.images_json}")
                for img_path in v.images_json:
                    if isinstance(img_path, str):
                        new_img = VehicleImage(vehicle_id=v.id, image_path=img_path)
                        db.add(new_img)
        
        db.commit()
        print("Migration complete!")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_images()
