from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://shuttleport_user:shuttleport_pass_2024@localhost:5432/shuttleport_db")

def add_images_column():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        try:
            # Add JSON columns support for images
            conn.execute(text("ALTER TABLE vehicles ADD COLUMN images JSON DEFAULT '[]'"))
            conn.commit()
            print("Successfully added images JSON column to vehicles table.")
        except Exception as e:
            if "duplicate column" in str(e).lower():
                print("Column images already exists.")
            else:
                print(f"Error adding column: {e}")

if __name__ == "__main__":
    add_images_column()
