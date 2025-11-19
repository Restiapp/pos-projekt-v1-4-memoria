"""
Epic A: POS OnPrem - Service Menu Health Tests
Tests for menu service basic health and availability
"""
import pytest
from fastapi.testclient import TestClient


def test_health_endpoint():
    """Test the health check endpoint returns ok status"""
    # Import here to avoid circular dependencies
    from backend.service_menu.main import app

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "menu"


def test_root_endpoint():
    """Test the root endpoint returns service information"""
    from backend.service_menu.main import app

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert data["status"] == "running"


def test_service_metadata():
    """Test that service has correct metadata"""
    from backend.service_menu.main import app

    # Verify basic FastAPI app configuration
    assert hasattr(app, "title")
    assert hasattr(app, "version")
    assert app.docs_url is not None
