#!/usr/bin/env python3
"""
Database initialization script
Creates all tables and populates with initial data
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base, SessionLocal
from app.models.db_models import Vehicle, FixedRoute, PricingConfig
from sqlalchemy.exc import IntegrityError


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully!")


def seed_vehicles(db):
    """Seed initial vehicle data"""
    print("\nSeeding vehicles...")
    
    vehicles = [
        Vehicle(
            vehicle_type="luxury_sedan",
            name_en="Luxury Sedan",
            name_tr="Lüks Sedan",
            capacity_min=1,
            capacity_max=3,
            baggage_capacity=3,
            features=[
                {"icon": "🧊", "text": "Soğuk İçecek"},
                {"icon": "📱", "text": "USB Şarj"},
                {"icon": "🌡️", "text": "Klima"},
                {"icon": "💺", "text": "Deri Koltuk"}
            ],
            base_multiplier=1.0,
            active=True
        ),
        Vehicle(
            vehicle_type="vito",
            name_en="Mercedes Vito",
            name_tr="Mercedes Vito",
            capacity_min=4,
            capacity_max=7,
            baggage_capacity=7,
            features=[
                {"icon": "🧊", "text": "Soğuk İçecek"},
                {"icon": "📱", "text": "USB Şarj"},
                {"icon": "🌡️", "text": "Klima"},
                {"icon": "📺", "text": "Eğlence Sistemi"}
            ],
            base_multiplier=1.5,
            active=True
        ),
        Vehicle(
            vehicle_type="sprinter",
            name_en="Mercedes Sprinter",
            name_tr="Mercedes Sprinter",
            capacity_min=8,
            capacity_max=15,
            baggage_capacity=15,
            features=[
                {"icon": "🧊", "text": "Soğuk İçecek"},
                {"icon": "📱", "text": "USB Şarj"},
                {"icon": "🌡️", "text": "Klima"},
                {"icon": "📺", "text": "Eğlence Sistemi"},
                {"icon": "🎵", "text": "Ses Sistemi"}
            ],
            base_multiplier=2.0,
            active=True
        )
    ]
    
    for vehicle in vehicles:
        try:
            existing = db.query(Vehicle).filter_by(vehicle_type=vehicle.vehicle_type).first()
            if not existing:
                db.add(vehicle)
                print(f"  ✓ Added vehicle: {vehicle.name_tr}")
            else:
                print(f"  - Vehicle already exists: {vehicle.name_tr}")
        except IntegrityError:
            db.rollback()
            print(f"  ! Skipped duplicate: {vehicle.name_tr}")
    
    db.commit()
    print("✓ Vehicles seeded!")


def seed_fixed_routes(db):
    """Seed popular fixed routes with pricing"""
    print("\nSeeding fixed routes...")
    
    # Get vehicle IDs
    sedan = db.query(Vehicle).filter_by(vehicle_type="luxury_sedan").first()
    vito = db.query(Vehicle).filter_by(vehicle_type="vito").first()
    sprinter = db.query(Vehicle).filter_by(vehicle_type="sprinter").first()
    
    if not all([sedan, vito, sprinter]):
        print("  ! Error: Vehicles not found. Seed vehicles first.")
        return
    
    routes = [
        # Istanbul Airport -> Sultanahmet
        FixedRoute(
            origin="istanbul airport",
            destination="sultanahmet",
            vehicle_id=sedan.id,
            price=2000.00,
            competitor_price=2050.00,
            notes="Rakip: 2050₺ | Bizim: 2000₺",
            active=True
        ),
        FixedRoute(
            origin="istanbul airport",
            destination="sultanahmet",
            vehicle_id=vito.id,
            price=2500.00,
            competitor_price=2600.00,
            notes="Rakip: 2600₺ | Bizim: 2500₺",
            active=True
        ),
        FixedRoute(
            origin="istanbul airport",
            destination="sultanahmet",
            vehicle_id=sprinter.id,
            price=3500.00,
            competitor_price=3700.00,
            notes="Rakip: 3700₺ | Bizim: 3500₺",
            active=True
        ),
        
        # Istanbul Airport -> Taksim
        FixedRoute(
            origin="istanbul airport",
            destination="taksim",
            vehicle_id=sedan.id,
            price=2200.00,
            competitor_price=2300.00,
            active=True
        ),
        FixedRoute(
            origin="istanbul airport",
            destination="taksim",
            vehicle_id=vito.id,
            price=2800.00,
            competitor_price=2900.00,
            active=True
        ),
        FixedRoute(
            origin="istanbul airport",
            destination="taksim",
            vehicle_id=sprinter.id,
            price=3800.00,
            competitor_price=4000.00,
            active=True
        ),
        
        # Sabiha Gokcen Airport -> Sultanahmet
        FixedRoute(
            origin="sabiha gokcen airport",
            destination="sultanahmet",
            vehicle_id=sedan.id,
            price=2800.00,
            competitor_price=2900.00,
            active=True
        ),
        FixedRoute(
            origin="sabiha gokcen airport",
            destination="sultanahmet",
            vehicle_id=vito.id,
            price=3500.00,
            competitor_price=3700.00,
            active=True
        ),
        FixedRoute(
            origin="sabiha gokcen airport",
            destination="sultanahmet",
            vehicle_id=sprinter.id,
            price=4500.00,
            competitor_price=4800.00,
            active=True
        ),
    ]
    
    for route in routes:
        try:
            existing = db.query(FixedRoute).filter_by(
                origin=route.origin,
                destination=route.destination,
                vehicle_id=route.vehicle_id
            ).first()
            
            if not existing:
                db.add(route)
                print(f"  ✓ Added route: {route.origin} → {route.destination} ({route.price}₺)")
            else:
                print(f"  - Route already exists: {route.origin} → {route.destination}")
        except IntegrityError:
            db.rollback()
            print(f"  ! Skipped duplicate route")
    
    db.commit()
    print("✓ Fixed routes seeded!")


def seed_pricing_config(db):
    """Seed pricing configuration"""
    print("\nSeeding pricing configuration...")
    
    configs = [
        PricingConfig(config_key="base_fare", config_value=500.00, description="Minimum fare for any trip"),
        PricingConfig(config_key="per_km_rate_sedan", config_value=25.00, description="Per km rate for luxury sedan", vehicle_type="luxury_sedan"),
        PricingConfig(config_key="per_km_rate_vito", config_value=35.00, description="Per km rate for Vito", vehicle_type="vito"),
        PricingConfig(config_key="per_km_rate_sprinter", config_value=45.00, description="Per km rate for Sprinter", vehicle_type="sprinter"),
        PricingConfig(config_key="airport_fee", config_value=200.00, description="Additional fee for airport transfers"),
        PricingConfig(config_key="round_trip_discount", config_value=15.00, description="Discount percentage for round trips"),
    ]
    
    for config in configs:
        try:
            existing = db.query(PricingConfig).filter_by(config_key=config.config_key).first()
            if not existing:
                db.add(config)
                print(f"  ✓ Added config: {config.config_key} = {config.config_value}")
            else:
                print(f"  - Config already exists: {config.config_key}")
        except IntegrityError:
            db.rollback()
            print(f"  ! Skipped duplicate config")
    
    db.commit()
    print("✓ Pricing configuration seeded!")


def main():
    """Main initialization function"""
    print("=" * 60)
    print("Shuttleport Database Initialization")
    print("=" * 60)
    
    # Create tables
    create_tables()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Seed data
        seed_vehicles(db)
        seed_fixed_routes(db)
        seed_pricing_config(db)
        
        print("\n" + "=" * 60)
        print("✓ Database initialization completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
