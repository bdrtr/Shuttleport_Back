import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def upgrade_db_precision():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL not found")
        return

    print(f"Connecting to DB...")
    try:
        conn = await asyncpg.connect(db_url)
        
        # List of columns to upgrade
        # table, column, new_type
        alterations = [
            ("fixed_routes", "price", "NUMERIC(15, 2)"),
            ("fixed_routes", "competitor_price", "NUMERIC(15, 2)"),
            ("pricing_config", "config_value", "NUMERIC(15, 2)")
        ]
        
        for table, col, new_type in alterations:
            print(f"Altering {table}.{col} to {new_type}...")
            await conn.execute(f"ALTER TABLE {table} ALTER COLUMN {col} TYPE {new_type};")
            
        print("✅ Database schema updated successfully.")
        await conn.close()
    except Exception as e:
        print(f"❌ Error updating schema: {e}")

if __name__ == "__main__":
    asyncio.run(upgrade_db_precision())
