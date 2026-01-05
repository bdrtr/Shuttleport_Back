import os
import asyncio
import asyncpg
from dotenv import load_dotenv

load_dotenv()

async def list_tables():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL not found")
        return
        
    print(f"Connecting to: {db_url.split('@')[1]}")
    try:
        conn = await asyncpg.connect(db_url)
        rows = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        print("Tables found:")
        for row in rows:
            print(f"- {row['table_name']}")
            
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(list_tables())
