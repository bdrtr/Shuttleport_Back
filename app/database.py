"""
Database connection and session management
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://shuttleport_user:shuttleport_pass_2024@localhost:5432/shuttleport_db")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=True if os.getenv("DEBUG", "false").lower() == "true" else False,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,
    max_overflow=10
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


# Dependency for FastAPI
def get_db():
    """
    Database session dependency for FastAPI endpoints
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
