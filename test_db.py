import os
import asyncio
import asyncpg
from dotenv import load_dotenv

load_dotenv()

async def test_connection():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL not found in .env")
        return

    print(f"Testing connection to: {db_url.split('@')[1]}") # Hide credentials
    
    try:
        conn = await asyncpg.connect(db_url)
        print("Success: Connected to the database!")
        version = await conn.fetchval('SELECT version()')
        print(f"Database version: {version}")
        await conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
