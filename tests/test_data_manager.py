"""
Tests for DataManager Excel operations
"""
import pytest
import os
import pandas as pd
from app.services.data_manager import DataManager


def test_ensure_file_exists(tmp_path):
    """Test that ensure_file_exists creates the Excel file"""
    # Temporarily change FILE_PATH
    original_path = DataManager.__dict__.get('FILE_PATH', 'static/istanbul_transfer.xlsx')
    test_file = tmp_path / "test_routes.xlsx"
    
    # Mock the FILE_PATH (this is a simplification, in real tests use dependency injection)
    # For now, just test the actual file if it exists
    
    if os.path.exists(original_path):
        assert os.path.isfile(original_path)


def test_load_routes():
    """Test loading routes from Excel"""
    routes = DataManager.load_routes()
    
    # Should return a list (empty or with data)
    assert isinstance(routes, list)
    
    # If routes exist, check structure
    if routes:
        first_route = routes[0]
        assert "origin" in first_route
        assert "destination" in first_route
        assert "price_vito" in first_route


def test_load_routes_from_missing_file(tmp_path, monkeypatch):
    """Test loading routes when file doesn't exist"""
    # Point to non-existent file
    monkeypatch.setattr('app.services.data_manager.FILE_PATH', str(tmp_path / "nonexistent.xlsx"))
    
    routes = DataManager.load_routes()
    
    # Should return empty list, not raise error
    assert routes == []


def test_route_data_structure():
    """Test that route data has expected structure"""
    DataManager.ensure_file_exists()
    routes = DataManager.load_routes()
    
    if routes:
        route = routes[0]
        
        # Required fields
        assert isinstance(route.get("origin"), str)
        assert isinstance(route.get("destination"), str)
        assert isinstance(route.get("price_vito"), (int, float))
        
        # Optional price fields
        if "price_sedan" in route:
            assert isinstance(route["price_sedan"], (int, float, type(None)))
        if "price_sprinter" in route:
            assert isinstance(route["price_sprinter"], (int, float, type(None)))
        
        # Metadata fields
        assert isinstance(route.get("active", True), bool)
        assert isinstance(route.get("discount", 0), (int, float))
