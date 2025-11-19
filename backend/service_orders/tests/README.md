# Service Orders - Integration Tests

## Overview

This directory contains integration tests for the Order + CRM integration feature (Task A2).

## Test Coverage

The tests validate three main scenarios:

1. **Create order with valid customer_uid** - Order is created successfully after validating the customer exists in CRM
2. **Create order without customer_uid** - Order is created successfully without CRM validation
3. **Create order with invalid customer_uid** - Order creation fails with 404 error when customer doesn't exist in CRM

Additionally, tests cover:
- Guest count validation (must be between 1 and 100)
- CRM service unavailability handling (503 error)

## Test Files

- `test_order_crm_integration.py` - Full FastAPI integration tests (requires all dependencies)
- `test_order_crm_integration_simple.py` - Simplified tests that mock HTTP calls (recommended)

## Requirements

The tests require a **PostgreSQL database** because the Order model uses JSONB fields, which are PostgreSQL-specific.

### Dependencies

```bash
pytest==8.3.3
pytest-asyncio==0.24.0
pytest-mock==3.14.0
httpx==0.27.0
fastapi==0.115.0
sqlalchemy==2.0.35
psycopg2-binary==2.9.9
```

## Running Tests

### Option 1: Docker Environment (Recommended)

Run tests inside the Docker container where PostgreSQL is available:

```bash
# Enter the service_orders container
docker-compose exec service_orders bash

# Run all integration tests
pytest backend/service_orders/tests/test_order_crm_integration_simple.py -v

# Run specific test
pytest backend/service_orders/tests/test_order_crm_integration_simple.py::test_create_order_with_valid_customer_uid -v
```

### Option 2: Local Environment

If running locally, ensure you have:

1. PostgreSQL installed and running
2. Environment variables set:
   ```bash
   export DATABASE_URL="postgresql://pos_user:password@localhost:5432/pos_db_test"
   export CRM_SERVICE_URL="http://localhost:8004"
   ```
3. Run tests:
   ```bash
   pytest backend/service_orders/tests/test_order_crm_integration_simple.py -v
   ```

## Test Implementation Details

### Mocking Strategy

The tests use `unittest.mock` to mock HTTP calls to the CRM service:

```python
@patch("backend.service_orders.services.order_service.httpx.Client")
def test_create_order_with_valid_customer_uid(mock_client_class, db_session):
    # Mock CRM response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "customer_uid": "CUST-123456",
        "first_name": "János",
        "last_name": "Kovács"
    }
    # ... test logic
```

### Database Setup

Tests use an in-memory SQLite database for fast execution:

```python
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
```

**Note:** Due to PostgreSQL-specific types (JSONB), tests may require PostgreSQL instead of SQLite.

## Expected Test Results

When all tests pass, you should see:

```
============================= test session starts ==============================
collected 5 items

test_order_crm_integration_simple.py::test_create_order_with_valid_customer_uid PASSED [ 20%]
test_order_crm_integration_simple.py::test_create_order_without_customer_uid PASSED [ 40%]
test_order_crm_integration_simple.py::test_create_order_with_invalid_customer_uid PASSED [ 60%]
test_order_crm_integration_simple.py::test_guest_count_validation PASSED [ 80%]
test_order_crm_integration_simple.py::test_create_order_crm_service_unavailable PASSED [100%]

============================== 5 passed in 1.23s ===============================
```

## Troubleshooting

### SQLite compatibility issues

If you see errors like `AttributeError: 'SQLiteTypeCompiler' object has no attribute 'visit_JSONB'`, this means SQLite cannot handle PostgreSQL JSONB types. **Solution**: Run tests in Docker with PostgreSQL.

### Missing dependencies

If you see `ModuleNotFoundError`, install missing dependencies:

```bash
pip install -r backend/service_orders/requirements.txt
```

### CRM service not found

Tests mock the CRM service, so the actual service doesn't need to be running. If you see connection errors, verify that mocking is properly configured.

## CI/CD Integration

For CI/CD pipelines, use a PostgreSQL service container:

```yaml
# Example GitHub Actions configuration
services:
  postgres:
    image: postgres:15
    env:
      POSTGRES_USER: pos_user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: pos_db_test
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
```

## Contact

For issues or questions about these tests, please refer to the project documentation or contact the development team.
