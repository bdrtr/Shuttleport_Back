"""
Database models for shuttleport application
"""
from sqlalchemy import Column, Integer, String, Numeric, Boolean, TIMESTAMP, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Vehicle(Base):
    """Vehicle types table"""
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_type = Column(String(50), unique=True, nullable=False, index=True)  # 'luxury_sedan', 'vito', 'sprinter'
    name_en = Column(String(100), nullable=False)  # 'Luxury Sedan'
    name_tr = Column(String(100), nullable=False)  # 'Lüks Sedan'
    capacity_min = Column(Integer, nullable=False)
    capacity_max = Column(Integer, nullable=False)
    baggage_capacity = Column(Integer, nullable=False)
    features = Column(JSON)  # [{"icon": "🧊", "text": "Soğuk İçecek"}, ...]
    base_multiplier = Column(Numeric(5, 2), default=1.0)  # For pricing calculations
    active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    fixed_routes = relationship("FixedRoute", back_populates="vehicle")

    def __repr__(self):
        return f"<Vehicle(type={self.vehicle_type}, name={self.name_en})>"


class FixedRoute(Base):
    """Fixed routes with pre-defined pricing"""
    __tablename__ = "fixed_routes"

    id = Column(Integer, primary_key=True, index=True)
    origin = Column(String(100), nullable=False, index=True)  # 'istanbul airport'
    destination = Column(String(100), nullable=False, index=True)  # 'sultanahmet'
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)  # 2000.00
    discount_percent = Column(Numeric(5, 2), default=0)  # For special promotions
    competitor_price = Column(Numeric(10, 2))  # For reference
    notes = Column(Text)  # 'Rakip: 2050₺ | Bizim: 2000₺ (50₺ ucuz)'
    active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    vehicle = relationship("Vehicle", back_populates="fixed_routes")

    def __repr__(self):
        return f"<FixedRoute({self.origin} → {self.destination}, {self.price}₺)>"


class PricingConfig(Base):
    """Global pricing configuration parameters"""
    __tablename__ = "pricing_config"

    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, nullable=False, index=True)  # 'base_fare', 'per_km_rate'
    config_value = Column(Numeric(10, 2), nullable=False)
    description = Column(Text)
    vehicle_type = Column(String(50))  # NULL for global configs, specific for vehicle-specific
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<PricingConfig({self.config_key}={self.config_value})>"
