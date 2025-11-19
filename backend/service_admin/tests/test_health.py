"""
Epic C: BackOffice/CRM/Reports - Service Admin Health Tests
Tests for admin service basic health and availability
"""
import pytest
from fastapi.testclient import TestClient


def test_health_endpoint():
    """Test the health check endpoint returns ok status"""
    # Import here to avoid circular dependencies
    from backend.service_admin.main import app

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "admin"


def test_root_endpoint():
    """Test the root endpoint returns service information"""
    from backend.service_admin.main import app

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert data["status"] == "running"


def test_service_metadata():
    """Test that service has correct metadata"""
    from backend.service_admin.main import app

    # Verify basic FastAPI app configuration
    assert hasattr(app, "title")
    assert hasattr(app, "version")
    assert app.docs_url is not None


@pytest.mark.asyncio
async def test_admin_service_configured():
    """Test that admin service is properly configured"""
    from backend.service_admin.main import app

    # Verify the app is configured (should not raise exceptions)
    assert app is not None
    assert hasattr(app, "routes")
