"""
Script to create template routes for Istanbul shuttleport service
Run this script to populate common routes with suggested pricing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.db_models import Vehicle, FixedRoute
from decimal import Decimal

# Popular locations in Istanbul
AIRPORTS = [
    "Istanbul Airport",
    "Sabiha Gökçen Airport"
]

POPULAR_DESTINATIONS = [
    "Sultanahmet",
    "Taksim Square",
    "Besiktas",
    "Kadıköy",
    "Fatih",
    "Beyoğlu",
    "Üsküdar",
    "Galata Tower",
    "Ortaköy",
    "Bebek"
]

# Distance-based pricing (approximate km from Istanbul Airport)
DISTANCE_PRICING = {
    "Sultanahmet": {"km": 45, "base_price": 2500},
    "Taksim Square": {"km": 40, "base_price": 2300},
    "Besiktas": {"km": 38, "base_price": 2200},
    "Kadıköy": {"km": 50, "base_price": 2800},
    "Fatih": {"km": 42, "base_price": 2400},
    "Beyoğlu": {"km": 39, "base_price": 2250},
    "Üsküdar": {"km": 48, "base_price": 2700},
    "Galata Tower": {"km": 41, "base_price": 2350},
    "Ortaköy": {"km": 35, "base_price": 2000},
    "Bebek": {"km": 33, "base_price": 1900},
}

# Sabiha to destinations (different distances)
SABIHA_DISTANCE_PRICING = {
    "Sultanahmet": {"km": 55, "base_price": 3000},
    "Taksim Square": {"km": 50, "base_price": 2800},
    "Besiktas": {"km": 48, "base_price": 2700},
    "Kadıköy": {"km": 25, "base_price": 1500},
    "Fatih": {"km": 52, "base_price": 2900},
    "Beyoğlu": {"km": 49, "base_price": 2750},
    "Üsküdar": {"km": 30, "base_price": 1700},
    "Galata Tower": {"km": 51, "base_price": 2850},
    "Ortaköy": {"km": 45, "base_price": 2500},
    "Bebek": {"km": 43, "base_price": 2400},
}


def create_template_routes(vehicle_type="vito", dry_run=False):
    """
    Create template routes for a specific vehicle type
    
    Args:
        vehicle_type: Vehicle type code (vito, sprinter, luxury_sedan)
        dry_run: If True, only print what would be created
    """
    db = SessionLocal()
    
    try:
        # Get vehicle
        vehicle = db.query(Vehicle).filter(Vehicle.vehicle_type == vehicle_type).first()
        
        if not vehicle:
            print(f"❌ Vehicle type '{vehicle_type}' not found!")
            print("Available vehicles:")
            for v in db.query(Vehicle).all():
                print(f"  - {v.vehicle_type}: {v.name_en}")
            return
        
        print(f"\n🚗 Creating routes for: {vehicle.name_en} ({vehicle_type})")
        print("=" * 60)
        
        created_count = 0
        skipped_count = 0
        
        # Istanbul Airport routes
        for destination, info in DISTANCE_PRICING.items():
            origin = "Istanbul Airport"
            
            # Check if route already exists
            existing = db.query(FixedRoute).filter(
                FixedRoute.origin == origin,
                FixedRoute.destination == destination,
                FixedRoute.vehicle_id == vehicle.id
            ).first()
            
            if existing:
                print(f"⏭️  SKIP: {origin} → {destination} (already exists)")
                skipped_count += 1
                continue
            
            # Calculate price based on vehicle multiplier
            base_price = Decimal(str(info["base_price"]))
            final_price = base_price * vehicle.base_multiplier
            
            if dry_run:
                print(f"🔍 DRY RUN: Would create {origin} → {destination}: {final_price:.2f} ₺")
            else:
                route = FixedRoute(
                    origin=origin,
                    destination=destination,
                    vehicle_id=vehicle.id,
                    price=final_price,
                    active=True,
                    notes=f"Auto-generated template route ({info['km']} km)"
                )
                db.add(route)
                print(f"✅ CREATE: {origin} → {destination}: {final_price:.2f} ₺")
                created_count += 1
        
        # Sabiha Gökçen routes
        for destination, info in SABIHA_DISTANCE_PRICING.items():
            origin = "Sabiha Gökçen Airport"
            
            existing = db.query(FixedRoute).filter(
                FixedRoute.origin == origin,
                FixedRoute.destination == destination,
                FixedRoute.vehicle_id == vehicle.id
            ).first()
            
            if existing:
                print(f"⏭️  SKIP: {origin} → {destination} (already exists)")
                skipped_count += 1
                continue
            
            base_price = Decimal(str(info["base_price"]))
            final_price = base_price * vehicle.base_multiplier
            
            if dry_run:
                print(f"🔍 DRY RUN: Would create {origin} → {destination}: {final_price:.2f} ₺")
            else:
                route = FixedRoute(
                    origin=origin,
                    destination=destination,
                    vehicle_id=vehicle.id,
                    price=final_price,
                    active=True,
                    notes=f"Auto-generated template route ({info['km']} km)"
                )
                db.add(route)
                print(f"✅ CREATE: {origin} → {destination}: {final_price:.2f} ₺")
                created_count += 1
        
        if not dry_run:
            db.commit()
            print("\n" + "=" * 60)
            print(f"✨ Summary:")
            print(f"   Created: {created_count} routes")
            print(f"   Skipped: {skipped_count} routes (already exist)")
            print(f"   Total: {created_count + skipped_count} routes processed")
        else:
            print("\n🔍 DRY RUN MODE - No changes made to database")
            
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def create_all_vehicle_routes(dry_run=False):
    """Create template routes for all active vehicles"""
    db = SessionLocal()
    
    try:
        vehicles = db.query(Vehicle).filter(Vehicle.active == True).all()
        
        print(f"\n🚗 Found {len(vehicles)} active vehicles")
        print("=" * 60)
        
        for vehicle in vehicles:
            print(f"\nProcessing: {vehicle.name_en} ({vehicle.vehicle_type})")
            create_template_routes(vehicle.vehicle_type, dry_run=dry_run)
            
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Create template routes for shuttleport')
    parser.add_argument('--vehicle', type=str, help='Vehicle type (vito, sprinter, luxury_sedan)')
    parser.add_argument('--all', action='store_true', help='Create routes for all vehicles')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be created without making changes')
    
    args = parser.parse_args()
    
    if args.all:
        create_all_vehicle_routes(dry_run=args.dry_run)
    elif args.vehicle:
        create_template_routes(args.vehicle, dry_run=args.dry_run)
    else:
        print("Usage:")
        print("  python create_template_routes.py --vehicle vito")
        print("  python create_template_routes.py --all")
        print("  python create_template_routes.py --all --dry-run")
