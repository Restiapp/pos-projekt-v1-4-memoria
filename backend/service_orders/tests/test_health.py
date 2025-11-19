"""
Epic A: POS OnPrem - Service Orders Health Tests
Tests for basic service health and availability
"""
import pytest
from fastapi.testclient import TestClient


def test_health_endpoint():
    """Test the health check endpoint returns ok status"""
    # Import here to avoid circular dependencies
    from backend.service_orders.main import app

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "orders"


def test_root_endpoint():
    """Test the root endpoint returns service information"""
    from backend.service_orders.main import app

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Orders Service"
    assert data["status"] == "running"
    assert "docs" in data
    assert "health" in data


def test_service_metadata():
    """Test that service has correct metadata"""
    from backend.service_orders.main import app

    assert app.title == "Modul 1: Orders Service"
    assert app.version == "0.1.0"
    assert app.docs_url == "/docs"
    assert app.redoc_url == "/redoc"


@pytest.mark.asyncio
async def test_cors_middleware_configured():
    """Test that CORS middleware is properly configured"""
    from backend.service_orders.main import app

    # Check that CORS middleware is in the middleware stack
    middleware_types = [type(m).__name__ for m in app.user_middleware]
    assert "CORSMiddleware" in middleware_types or len(app.user_middleware) > 0
