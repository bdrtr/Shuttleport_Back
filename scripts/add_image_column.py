from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://shuttleport_user:shuttleport_pass_2024@localhost:5432/shuttleport_db")

def add_image_path_column():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE vehicles ADD COLUMN image_path VARCHAR(255)"))
            conn.commit()
            print("Successfully added image_path column to vehicles table.")
        except Exception as e:
            if "duplicate column" in str(e).lower():
                print("Column image_path already exists.")
            else:
                print(f"Error adding column: {e}")

if __name__ == "__main__":
    add_image_path_column()
