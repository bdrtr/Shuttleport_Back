import asyncio
from app.database import SessionLocal
from app.models.db_models import PricingConfig
from sqlalchemy.future import select

async def update_minimum_fare():
    db = SessionLocal()
    try:
        # Check if config exists
        config = db.query(PricingConfig).filter(PricingConfig.config_key == "minimum_fare").first()
        
        if config:
            print(f"Current minimum fare: {config.config_value}")
            config.config_value = 1200.00
            print("Updated to 1200.00")
        else:
            print("Config not found. Creating new...")
            new_config = PricingConfig(
                config_key="minimum_fare",
                config_value=1200.00,
                description="Global minimum fare floor",
                vehicle_type=None
            )
            db.add(new_config)
            print("Created minimum_fare = 1200.00")
            
        db.commit()
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Since SessionLocal is sync, we can just run it.
    # But wait, looking at my previous file view of database.py, SessionLocal is sync (sessionmaker).
    # Asyncpg usage in my check scripts was manual. The app uses Sync SQLAlchemy with psycopg2 (inferred from requirements having psycopg2-binary now).
    # app/database.py imports create_engine, not create_async_engine.
    update_minimum_fare()
    pass
