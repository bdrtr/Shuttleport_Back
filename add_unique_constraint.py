import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def add_constraint():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL not found")
        return

    print(f"Connecting to DB to add unique constraint...")
    try:
        conn = await asyncpg.connect(db_url)
        
        # Add constraint
        await conn.execute("""
            ALTER TABLE fixed_routes
            ADD CONSTRAINT uq_fixed_route_vehicle
            UNIQUE (origin, destination, vehicle_id);
        """)
        
        print(f"✅ Unique Constraint added: uq_fixed_route_vehicle")
        
        await conn.close()
    except Exception as e:
        print(f"❌ Error adding constraint: {e}")

if __name__ == "__main__":
    asyncio.run(add_constraint())
