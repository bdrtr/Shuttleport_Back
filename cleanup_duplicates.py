import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def cleanup_duplicates():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL not found")
        return

    print(f"Connecting to DB to cleanup duplicates...")
    try:
        conn = await asyncpg.connect(db_url)
        
        # Query to find duplicates (same origin, destination, vehicle_id)
        # We want to keep the LATEST one (highest ID or max created_at)
        query = """
            DELETE FROM fixed_routes a USING fixed_routes b
            WHERE a.id < b.id
            AND a.origin = b.origin
            AND a.destination = b.destination
            AND a.vehicle_id = b.vehicle_id;
        """
        
        result = await conn.execute(query)
        print(f"✅ Cleanup executed. Result: {result}")
        
        await conn.close()
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    asyncio.run(cleanup_duplicates())
