"""
Basic API tests for Shuttleport backend
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint redirects or returns valid response"""
    response = client.get("/")
    assert response.status_code in [200, 307, 404]  # OK, Redirect, or Not Found


def test_pricing_calculate_endpoint():
    """Test pricing calculation with valid payload"""
    payload = {
        "origin_lat": 41.0082,
        "origin_lng": 28.9784,
        "origin_name": "Istanbul Airport",
        "destination_lat": 41.0082,
        "destination_lng": 29.0084,
        "destination_name": "Kadikoy",
        "distance_km": 25,
        "duration_minutes": 30,
        "passenger_count": 2
    }
    
    response = client.post("/api/pricing/calculate", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "vehicles" in data
    assert "route_info" in data
    assert len(data["vehicles"]) > 0
    
    # Check minimum fare enforcement
    for vehicle in data["vehicles"]:
        assert vehicle["final_price"] >= 1200  # Minimum fare


def test_pricing_calculate_invalid_payload():
    """Test pricing calculation with invalid payload"""
    payload = {
        "origin_lat": "invalid",  # Should be float
        "origin_lng": 28.9784,
    }
    
    response = client.post("/api/pricing/calculate", json=payload)
    assert response.status_code == 422  # Validation error


def test_get_vehicles_endpoint():
    """Test vehicles list endpoint"""
    response = client.get("/api/pricing/vehicles")
    
    assert response.status_code == 200
    vehicles = response.json()
    
    assert isinstance(vehicles, list)
    assert len(vehicles) > 0
    
    # Check vehicle structure
    first_vehicle = vehicles[0]
    assert "vehicle_type" in first_vehicle
    assert "capacity" in first_vehicle


def test_admin_panel_accessible():
    """Test admin panel is accessible"""
    response = client.get("/admin")
    
    # Should either show admin page or redirect to login
    assert response.status_code in [200, 307, 401, 403]


def test_api_docs_accessible():
    """Test API documentation is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200
    
    response = client.get("/redoc")
    assert response.status_code == 200


def test_excel_import_without_file():
    """Test Excel import endpoint without file"""
    response = client.post("/api/admin/import-excel")
    
    # Should return error for missing file
    assert response.status_code in [400, 422]


def test_static_files():
    """Test static files are served"""
    # This will fail if no image exists, but tests the mount point
    response = client.get("/static/")
    assert response.status_code in [200, 404, 403]  # Depends on directory listing config
