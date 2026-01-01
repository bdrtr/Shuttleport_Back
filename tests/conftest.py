"""Test configurations and fixtures"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def sample_coordinates():
    """Sample coordinates for testing"""
    return {
        "origin_lat": 41.0082,
        "origin_lng": 28.9784,
        "destination_lat": 40.9829,
        "destination_lng": 29.0208
    }
