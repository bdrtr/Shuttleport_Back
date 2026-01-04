from sqlalchemy import create_engine
from app.models.db_models import Base, VehicleImage
from app.database import DATABASE_URL

def init_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print("Relational images tables created successfully.")

if __name__ == "__main__":
    init_db()
