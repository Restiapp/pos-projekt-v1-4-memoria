# POS System Codebase Structure & Architecture Guide

## 1. OVERALL PROJECT STRUCTURE

This is a **monorepo with 6 distinct microservices** in the backend, following a microservices architecture pattern:

```
/home/user/pos-projekt-v1-4-memoria/
├── backend/                          # All microservices
│   ├── service_menu/                 # Module 0: Product Menu & Translation AI
│   ├── service_orders/               # Modules 1-2: Order & Table Management
│   ├── service_kds/                  # Module 3: Kitchen Display System
│   ├── service_billing/              # Module 4: Billing & Payments
│   ├── service_inventory/            # Module 5: Stock & Recipes (HAS EXTERNAL INTEGRATIONS)
│   ├── service_crm/                  # Module 7: Customer Relationship Management
│   └── service_admin/                # Module 8: RBAC, NTAK, Finance (HAS EXTERNAL INTEGRATIONS)
├── frontend/                         # React frontend
├── docker-compose.yml                # Local development setup
└── Documentation files
```

### Architecture Pattern
- **Synchronous**: REST APIs over HTTP for direct service-to-service calls
- **Asynchronous**: Google Pub/Sub for event-driven inter-service communication
- **API Gateway**: Handles authentication, rate limiting, and request routing
- **Database**: Shared PostgreSQL database with separate tables per service
- **Authentication**: JWT tokens + RBAC (Role-Based Access Control)

---

## 2. SERVICE_INVENTORY LOCATION & STRUCTURE

**Path**: `/home/user/pos-projekt-v1-4-memoria/backend/service_inventory/`

### Complete Directory Structure
```
service_inventory/
├── main.py                           # FastAPI application initialization
├── config.py                         # Settings (Pydantic BaseSettings)
├── requirements.txt                  # Python dependencies
├── Dockerfile                        # Container definition
├── .env.example                      # Environment variables template
├── models/                           # SQLAlchemy ORM Models
│   ├── database.py                   # SQLAlchemy engine, session factory
│   ├── inventory_item.py             # Core inventory items table
│   ├── supplier_invoice.py           # Supplier invoice documents
│   ├── recipe.py                     # Recipe definitions & ingredients
│   ├── waste_log.py                  # Waste tracking
│   └── daily_inventory_sheet.py      # Daily inventory counts
├── schemas/                          # Pydantic validation schemas
│   ├── inventory_item.py             # Request/response schemas for items
│   ├── supplier_invoice.py           # Invoice schemas
│   ├── recipe.py                     # Recipe schemas
│   ├── daily_inventory.py            # Daily inventory schemas
│   └── nav_osa_invoice.py            # NAV OSA invoice schemas
├── routers/                          # FastAPI route handlers
│   ├── inventory_items.py            # CRUD endpoints for items
│   ├── invoices.py                   # Supplier invoice management
│   ├── recipes.py                    # Recipe management
│   ├── daily_inventory.py            # Daily inventory endpoints
│   ├── internal_router.py            # Service-to-service API (no RBAC)
│   └── osa_integration_router.py     # NAV OSA integration (MOCK)
├── services/                         # Business logic layer
│   ├── inventory_service.py          # Item CRUD operations
│   ├── recipe_service.py             # Recipe management logic
│   ├── daily_inventory_service.py    # Daily inventory logic
│   ├── stock_deduction_service.py    # Perpetual inventory updates
│   ├── ocr_service.py                # Document AI OCR processing
│   └── nav_osa_service.py            # NAV OSA API integration (MOCK)
└── tests/                            # Unit tests (currently minimal)
    └── __init__.py
```

---

## 3. SERVICE_ADMIN LOCATION & STRUCTURE

**Path**: `/home/user/pos-projekt-v1-4-memoria/backend/service_admin/`

### Complete Directory Structure
```
service_admin/
├── main.py                           # FastAPI application + lifespan
├── config.py                         # Settings with NTAK config
├── dependencies.py                   # JWT, RBAC, auth utilities (CRITICAL)
├── requirements.txt                  # Python dependencies
├── Dockerfile                        # Container definition
├── .env.example                      # Environment template
├── seed_rbac.py                      # Seed initial roles/permissions
├── models/                           # SQLAlchemy ORM Models
│   ├── database.py                   # SQLAlchemy engine, session factory
│   ├── employee.py                   # Employee with many-to-many roles
│   ├── role.py                       # Role definitions
│   ├── permission.py                 # Permission definitions
│   ├── audit_log.py                  # Audit trail logging
│   ├── finance.py                    # Financial data (invoices, etc.)
│   ├── assets.py                     # Asset management
│   └── vehicles.py                   # Vehicle/delivery management
├── schemas/                          # Pydantic validation schemas
│   ├── employee.py                   # Employee request/response schemas
│   ├── role.py                       # Role schemas
│   ├── permission.py                 # Permission schemas
│   ├── auth.py                       # Login/token schemas
│   ├── ntak.py                       # NTAK reporting schemas
│   ├── finance.py                    # Financial schemas
│   ├── asset.py                      # Asset schemas
│   └── vehicle.py                    # Vehicle schemas
├── routers/                          # FastAPI route handlers
│   ├── auth.py                       # Login, token generation
│   ├── employees.py                  # Employee CRUD + role assignment
│   ├── roles.py                      # Role CRUD
│   ├── permissions.py                # Permission CRUD
│   ├── finance.py                    # Financial operations
│   ├── integrations.py               # Számlázz.hu API integration (MOCK)
│   ├── asset_router.py               # Asset management
│   ├── vehicle_router.py             # Vehicle management
│   ├── internal.py                   # Service-to-service API
│   └── __init__.py                   # Router exports
├── services/                         # Business logic layer
│   ├── auth_service.py               # JWT token creation/validation
│   ├── employee_service.py           # Employee CRUD
│   ├── role_service.py               # Role CRUD
│   ├── permission_service.py         # Permission CRUD
│   ├── ntak_service.py               # NTAK submission (REAL HTTP calls)
│   ├── audit_log_service.py          # Audit logging
│   ├── finance_service.py            # Financial operations
│   ├── szamlazz_hu_service.py        # Számlázz.hu integration (MOCK)
│   ├── asset_service.py              # Asset management
│   └── vehicle_service.py            # Vehicle management
├── migrations/                       # Alembic database migrations
└── __init__.py
```

---

## 4. DATABASE MODELS (SQLAlchemy)

### Key Pattern Used: SQLAlchemy 2.0 with declarative_base()

**Database Initialization** (`service_inventory/models/database.py`):
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
```

### Example Model: InventoryItem
**File**: `/home/user/pos-projekt-v1-4-memoria/backend/service_inventory/models/inventory_item.py`

```python
from sqlalchemy import Column, Integer, String, Numeric
from backend.service_inventory.models.database import Base

class InventoryItem(Base):
    __tablename__ = 'inventory_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    unit = Column(String(50), nullable=False)  # 'kg', 'liter', 'db'
    current_stock_perpetual = Column(Numeric(10, 3), default=0.000)
    last_cost_per_unit = Column(Numeric(10, 2), nullable=True)
    
    # Relationships
    recipes = relationship('Recipe', back_populates='inventory_item')
```

### Example Model: Employee (with RBAC)
**File**: `/home/user/pos-projekt-v1-4-memoria/backend/service_admin/models/employee.py`

```python
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Many-to-Many association table
employee_roles = Table(
    'employee_roles',
    Base.metadata,
    Column('employee_id', Integer, ForeignKey('employees.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('assigned_at', TIMESTAMP(timezone=True), server_default=func.now())
)

class Employee(Base):
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, unique=True, index=True)
    pin_code_hash = Column(String(255), nullable=False)  # bcrypt hash
    email = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
    
    # Many-to-Many relationship
    roles = relationship('Role', secondary=employee_roles, back_populates='employees')
    
    @property
    def permissions(self):
        """Collect all permissions from assigned roles"""
        perms = set()
        for role in self.roles:
            perms.update(role.permissions)
        return perms
    
    def has_permission(self, permission_name: str) -> bool:
        """Check if employee has a specific permission"""
        return any(perm.name == permission_name for perm in self.permissions)
```

### Key Features:
- **Database Agnostic**: Uses PostgreSQL but can work with other databases
- **Relationships**: Foreign keys, many-to-many tables (like `employee_roles`)
- **Indexes**: Strategic indexes for common queries (`index=True`)
- **Timestamps**: Automatic `created_at`, `updated_at` with server defaults
- **Constraints**: Unique constraints, nullable fields

---

## 5. PYDANTIC SCHEMAS (Request/Response Validation)

### Pattern: Base -> Create -> Update -> InDB -> Response

**File**: `/home/user/pos-projekt-v1-4-memoria/backend/service_inventory/schemas/inventory_item.py`

```python
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal

# Base schema with common fields
class InventoryItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    unit: str = Field(..., min_length=1, max_length=50)
    current_stock_perpetual: Decimal = Field(default=Decimal("0.000"), ge=0)
    last_cost_per_unit: Optional[Decimal] = Field(None, ge=0)

# Create schema (for POST requests)
class InventoryItemCreate(InventoryItemBase):
    pass

# Update schema (for PATCH requests - all fields optional)
class InventoryItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    unit: Optional[str] = Field(None, min_length=1, max_length=50)
    current_stock_perpetual: Optional[Decimal] = Field(None, ge=0)
    last_cost_per_unit: Optional[Decimal] = Field(None, ge=0)

# Database schema (includes ID)
class InventoryItemInDB(InventoryItemBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

# Response schema (public API response)
class InventoryItemResponse(InventoryItemInDB):
    pass

# List response (with pagination)
class InventoryItemListResponse(BaseModel):
    items: list[InventoryItemResponse]
    total: int
    page: int
    page_size: int
```

### Key Features:
- **Validation**: Min/max length, decimal places, regex patterns
- **Examples**: Field examples for API documentation
- **from_attributes=True**: Convert SQLAlchemy models to Pydantic (ORM mode)
- **Type Safety**: Full type hints with Pydantic v2

---

## 6. API ENDPOINTS (FastAPI Routers)

### Pattern: Router -> Dependency Injection -> Service Layer -> Database

**File**: `/home/user/pos-projekt-v1-4-memoria/backend/service_inventory/routers/inventory_items.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Create router
router = APIRouter(
    prefix="/inventory/items",
    tags=["Inventory Items"],
    responses={404: {"description": "Item not found"}}
)

# Dependency injection for service
def get_inventory_service(db: Session = Depends(get_db)) -> InventoryService:
    return InventoryService(db)

# GET endpoint with list
@router.get(
    "",
    response_model=InventoryItemListResponse,
    summary="List inventory items"
)
def list_inventory_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    name_filter: Optional[str] = Query(None),
    service: InventoryService = Depends(get_inventory_service)
):
    return service.list_items(skip=skip, limit=limit, name_filter=name_filter)

# POST endpoint
@router.post(
    "",
    response_model=InventoryItemResponse,
    status_code=status.HTTP_201_CREATED
)
def create_inventory_item(
    item_data: InventoryItemCreate,
    service: InventoryService = Depends(get_inventory_service)
):
    try:
        item = service.create_item(item_data)
        return InventoryItemResponse.model_validate(item)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# GET single item
@router.get("/{item_id}", response_model=InventoryItemResponse)
def get_inventory_item(
    item_id: int,
    service: InventoryService = Depends(get_inventory_service)
):
    item = service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return InventoryItemResponse.model_validate(item)

# PATCH endpoint
@router.patch("/{item_id}", response_model=InventoryItemResponse)
def update_inventory_item(
    item_id: int,
    item_data: InventoryItemUpdate,
    service: InventoryService = Depends(get_inventory_service)
):
    item = service.update_item(item_id, item_data)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return InventoryItemResponse.model_validate(item)

# DELETE endpoint
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inventory_item(
    item_id: int,
    service: InventoryService = Depends(get_inventory_service)
):
    service.delete_item(item_id)
```

### Router Registration in Main App
**File**: `/home/user/pos-projekt-v1-4-memoria/backend/service_inventory/main.py`

```python
from fastapi import FastAPI, Depends
from backend.service_inventory.routers import inventory_items_router
from backend.service_admin.dependencies import require_permission

app = FastAPI(title="Inventory Service")

# Register router with RBAC protection
app.include_router(
    inventory_items_router,
    dependencies=[Depends(require_permission("inventory:manage"))]
)
```

---

## 7. CONFIGURATION MANAGEMENT

### Pattern: Pydantic Settings from .env

#### Inventory Service Configuration
**File**: `/home/user/pos-projekt-v1-4-memoria/backend/service_inventory/config.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn

class Settings(BaseSettings):
    # Database
    database_url: PostgresDsn = Field(
        ...,
        description="PostgreSQL connection string"
    )
    
    # Google Cloud
    gcp_project_id: str = Field(...)
    documentai_processor_id: str = Field(...)
    documentai_location: str = Field(default="eu")
    gcs_bucket_name: str = Field(...)
    google_application_credentials: str = Field(...)
    
    # Service
    port: int = Field(default=8003, ge=1024, le=65535)
    menu_service_url: str = Field(default="http://localhost:8000")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

settings = Settings()  # Singleton instance
```

#### Admin Service Configuration
**File**: `/home/user/pos-projekt-v1-4-memoria/backend/service_admin/config.py`

```python
class Settings(BaseSettings):
    # Service
    port: int = Field(default=8008, ge=1024, le=65535)
    
    # NTAK (Hungarian Tax Authority)
    ntak_enabled: bool = Field(default=True)
    ntak_api_url: str = Field(default="https://ntak-test.gov.hu/api/v1")
    ntak_api_key: str = Field(...)
    ntak_restaurant_id: str = Field(default="REST12345")
    ntak_tax_number: str = Field(...)
    ntak_report_interval: int = Field(default=3600, ge=60, le=86400)
    
    # Inter-service URLs
    orders_service_url: str = Field(default="http://localhost:8002")
    menu_service_url: str = Field(default="http://localhost:8001")
    inventory_service_url: str = Field(default="http://localhost:8003")
    
    # JWT
    jwt_secret_key: str = Field(..., min_length=32)
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=60)
    
    # Logging
    log_level: str = Field(default="INFO")
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
```

#### Environment File Template
**File**: `/home/user/pos-projekt-v1-4-memoria/.env.example`

```bash
# PostgreSQL
POSTGRES_PASSWORD=pos_password_dev

# Google Cloud
GOOGLE_CREDENTIALS_PATH=./credentials
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/gcp-key.json
VERTEX_PROJECT_ID=your-gcp-project-id
DOCUMENTAI_LOCATION=us
DOCUMENTAI_PROCESSOR_ID=your-processor-id

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# NTAK
NTAK_API_URL=https://ntak-test.nav.gov.hu
NTAK_API_KEY=your-ntak-api-key
NTAK_MERCHANT_ID=your-ntak-merchant-id

# Environment
ENVIRONMENT=development
```

---

## 8. RBAC (Role-Based Access Control) PATTERN

### How Authentication & Authorization Works

**File**: `/home/user/pos-projekt-v1-4-memoria/backend/service_admin/dependencies.py`

```python
# 1. PASSWORD HASHING
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# 2. JWT TOKEN CREATION
from jose import jwt
from datetime import datetime, timedelta

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

# 3. GET CURRENT USER FROM JWT
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Employee:
    """Decode JWT token and load employee with roles/permissions"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        employee_id = int(payload.get("sub"))
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Load employee with eager loading of roles and permissions
    employee = db.query(Employee)\
        .options(joinedload(Employee.roles).joinedload(Role.permissions))\
        .filter(Employee.id == employee_id)\
        .first()
    
    if not employee or not employee.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    
    return employee

# 4. PERMISSION CHECKER
def require_permission(permission_name: str) -> Callable:
    """Create dependency that checks if user has permission"""
    async def permission_checker(
        current_user: Employee = Depends(get_current_user)
    ) -> Employee:
        if not current_user.has_permission(permission_name):
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied: '{permission_name}' required"
            )
        return current_user
    
    return permission_checker
```

### Usage in Endpoints
```python
@router.post(
    "",
    response_model=EmployeeResponse,
    dependencies=[Depends(require_permission("employees:manage"))]
)
async def create_employee(
    employee_data: EmployeeCreate,
    current_user: Employee = Depends(get_current_user),  # Get the authed user
    service: EmployeeService = Depends(get_employee_service)
) -> EmployeeResponse:
    # Only reaches here if user has 'employees:manage' permission
    employee = service.create_employee(...)
    return EmployeeResponse.model_validate(employee)
```

### Permission Naming Convention
```
Format: "resource:action"

Examples:
- "orders:view" - View orders
- "orders:create" - Create orders
- "inventory:manage" - Manage inventory
- "employees:manage" - Manage employees
- "reports:view" - View reports
- "admin:all" - Full admin access
```

---

## 9. EXTERNAL API INTEGRATIONS & MOCK CLIENTS

### 1. NAV OSA Service (Mock Implementation)
**File**: `/home/user/pos-projekt-v1-4-memoria/backend/service_inventory/services/nav_osa_service.py`

```python
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class NAVOSAService:
    """MOCK Service for NAV Online Számlázó API integration"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def send_invoice_to_nav(
        self,
        invoice_data: Dict[str, Any],
        test_mode: bool = True
    ) -> Dict[str, Any]:
        """
        MOCK: Send invoice to NAV Online Számlázó API
        
        TODO (Phase 4): Replace with real NAV API:
        - Generate invoiceData XML according to NAV schema
        - Sign request with technical user credentials
        - POST to https://api.onlineszamla.nav.gov.hu/invoiceService/v3/manageInvoice
        - Parse and validate NAV response
        - Handle NAV-specific error codes
        """
        logger.info(f"[MOCK NAV OSA] Sending invoice to NAV (test_mode={test_mode})")
        
        # MOCK: Simulate successful NAV response
        mock_transaction_id = f"MOCK_NAV_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        mock_response = {
            "success": True,
            "transactionId": mock_transaction_id,
            "processingStatus": "ACCEPTED",
            "timestamp": datetime.now().isoformat(),
            "technicalValidationMessages": [],
            "businessValidationMessages": []
        }
        
        return {
            "success": True,
            "transaction_id": mock_transaction_id,
            "status": "ACCEPTED",
            "message": "[MOCK] Invoice successfully sent to NAV",
            "nav_response": mock_response
        }
```

**Router Endpoint**:
```python
@osa_router.post(
    "/send-invoice",
    response_model=NAVSendInvoiceResponse,
    description="""
    **CURRENT STATUS: MOCK IMPLEMENTATION**
    
    TODO (Phase 4): Real NAV API Integration
    - Implement proper XML generation
    - Add cryptographic signing
    - Implement error handling for NAV responses
    - Add retry logic
    """
)
def send_invoice_to_nav(
    request: NAVSendInvoiceRequest,
    db: Session = Depends(get_db),
    service: NAVOSAService = Depends(get_nav_osa_service)
) -> NAVSendInvoiceResponse:
    result = service.send_invoice_to_nav(
        invoice_data={"invoice_id": request.invoice_id},
        test_mode=request.test_mode
    )
    return NAVSendInvoiceResponse(**result)
```

### 2. NTAK Service (Real HTTP Calls)
**File**: `/home/user/pos-projekt-v1-4-memoria/backend/service_admin/services/ntak_service.py`

```python
import httpx
from backend.service_admin.config import settings

class NtakService:
    """Service for NTAK data submission (National Tourism Data Service Center)"""
    
    def __init__(self):
        self.ntak_enabled = settings.ntak_enabled
        self.ntak_api_url = settings.ntak_api_url
        self.ntak_api_key = settings.ntak_api_key
        self.orders_service_url = settings.orders_service_url
    
    async def send_order_summary(self, order_id: int) -> NTAKResponse:
        """
        Send order summary to NTAK:
        1. Fetch order data from Orders Service
        2. Transform to NTAK-compliant format
        3. Submit to NTAK API
        4. Update order record with results
        """
        logger.info(f"Starting NTAK submission for order_id={order_id}")
        
        # Step 1: Fetch order from Orders Service
        try:
            order_data = await self._fetch_order_from_service(order_id)
            logger.debug(f"Fetched order data: {order_data}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to fetch order {order_id}: {e}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Network error fetching order: {e}")
            raise
        
        # Step 2: Transform order data to NTAK format
        ntak_data = self._transform_order_to_ntak(order_data)
        
        # Step 3: Submit to NTAK API
        ntak_response = await self._submit_to_ntak(ntak_data)
        
        return ntak_response
    
    async def _fetch_order_from_service(self, order_id: int) -> Dict:
        """Fetch order data from Orders Service via HTTP"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.orders_service_url}/api/v1/orders/{order_id}",
                headers={"Authorization": f"Bearer {self.ntak_api_key}"},
                timeout=30.0
            )
            response.raise_for_status()  # Raise on 4xx/5xx
            return response.json()
```

### 3. Számlázz.hu Integration (Mock)
**File**: `/home/user/pos-projekt-v1-4-memoria/backend/service_admin/services/szamlazz_hu_service.py`

```python
class SzamlazzHuService:
    """MOCK: Számlázz.hu invoicing API integration"""
    
    def __init__(self):
        self.api_url = "https://api.szamlazz.hu"  # Would be real in production
    
    def create_invoice(self, invoice_data: Dict) -> Dict:
        """
        MOCK: Create invoice in Számlázz.hu
        
        In production, would:
        - Call szamlazz.hu XML API
        - Submit invoice data
        - Return invoice number and PDF URL
        """
        logger.info(f"[MOCK] Creating invoice for order {invoice_data.get('order_id')}")
        
        return {
            "success": True,
            "invoice_number": f"MOCK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "pdf_url": "https://mock-pdf-url.example.com/invoice.pdf"
        }
```

---

## 10. TESTING STRUCTURE

### Current Status
- **Minimal testing** - Test files exist but are mostly empty stubs
- **Files**: 
  - `/home/user/pos-projekt-v1-4-memoria/backend/service_inventory/tests/__init__.py`
  - `/home/user/pos-projekt-v1-4-memoria/backend/service_orders/tests/__init__.py`

### Testing Dependencies (in requirements.txt)
```
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
```

### Example Test Structure (to implement)
```python
# backend/service_inventory/tests/test_inventory_items.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.service_inventory.main import app
from backend.service_inventory.models.database import Base, get_db
from backend.service_inventory.models.inventory_item import InventoryItem

# Test database setup
@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///test.db")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=engine)

# Tests
@pytest.fixture
def client(test_db):
    return TestClient(app)

def test_list_inventory_items(client):
    response = client.get("/inventory/items")
    assert response.status_code == 200
    assert "items" in response.json()

def test_create_inventory_item(client):
    response = client.post(
        "/inventory/items",
        json={"name": "Test Item", "unit": "kg", "current_stock_perpetual": 10}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Item"
```

---

## 11. KEY FILES SUMMARY TABLE

| Component | File Path | Purpose |
|-----------|-----------|---------|
| **Inventory Service** |
| Main App | `/backend/service_inventory/main.py` | FastAPI app, route registration, startup |
| Config | `/backend/service_inventory/config.py` | Settings from .env |
| Models | `/backend/service_inventory/models/` | SQLAlchemy ORM definitions |
| Schemas | `/backend/service_inventory/schemas/` | Pydantic validation schemas |
| Routes | `/backend/service_inventory/routers/` | FastAPI endpoints |
| Services | `/backend/service_inventory/services/` | Business logic |
| **Admin Service** |
| Main App | `/backend/service_admin/main.py` | FastAPI app with lifespan |
| Config | `/backend/service_admin/config.py` | Settings including NTAK |
| Dependencies | `/backend/service_admin/dependencies.py` | JWT, RBAC, auth utilities |
| Models | `/backend/service_admin/models/` | SQLAlchemy with RBAC tables |
| Schemas | `/backend/service_admin/schemas/` | Pydantic schemas for all features |
| Routes | `/backend/service_admin/routers/` | RBAC-protected endpoints |
| Services | `/backend/service_admin/services/` | Business logic & API integrations |
| **External Integrations** |
| NAV OSA | `/backend/service_inventory/services/nav_osa_service.py` | Mock NAV integration |
| NTAK | `/backend/service_admin/services/ntak_service.py` | Real NTAK HTTP calls |
| Számlázz.hu | `/backend/service_admin/services/szamlazz_hu_service.py` | Mock invoicing API |

---

## 12. TECHNOLOGY STACK

### Core Framework
- **FastAPI 0.104+** - Modern async web framework
- **Uvicorn** - ASGI server
- **Pydantic 2.9+** - Data validation & serialization
- **SQLAlchemy 2.0+** - ORM with async support

### Authentication & Security
- **python-jose** - JWT token handling
- **passlib[bcrypt]** - Password hashing
- **bcrypt** - Cryptographic hashing
- **PyJWT** - JWT encoding/decoding

### Data & Databases
- **psycopg2-binary** - PostgreSQL driver
- **asyncpg** - Async PostgreSQL
- **Alembic** - Database migrations

### External Services
- **httpx** - Async HTTP client for inter-service & API calls
- **google-cloud-documentai** - OCR for invoices
- **google-cloud-storage** - File storage

### Development & Testing
- **pytest** - Testing framework
- **pytest-asyncio** - Async test support
- **python-dotenv** - Environment variables

---

## 13. COMMON PATTERNS TO FOLLOW

### 1. Creating a New Endpoint
```python
# 1. Create schema (schemas/my_feature.py)
class MyFeatureCreate(BaseModel):
    field1: str
    field2: int

class MyFeatureResponse(MyFeatureCreate):
    id: int

# 2. Create router (routers/my_feature.py)
router = APIRouter(prefix="/my-feature", tags=["MyFeature"])

def get_my_service(db: Session = Depends(get_db)):
    return MyService(db)

@router.post("", response_model=MyFeatureResponse)
def create(data: MyFeatureCreate, service=Depends(get_my_service)):
    return service.create(data)

# 3. Register in main.py
from backend.service_x.routers import my_feature_router
app.include_router(my_feature_router)
```

### 2. Adding RBAC Protection
```python
@router.post(
    "",
    dependencies=[Depends(require_permission("feature:manage"))]
)
def protected_endpoint(
    current_user: Employee = Depends(get_current_user),
    ...
):
    # Only users with "feature:manage" permission reach here
    pass
```

### 3. Error Handling
```python
try:
    result = service.operation()
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

### 4. Inter-Service Communication
```python
import httpx

async def call_other_service(order_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8002/api/v1/orders/{order_id}",
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()
```

---

## 14. PORT ASSIGNMENTS
- **Service Menu**: 8000
- **Service Orders**: 8001
- **Service Orders (alternative)**: 8002
- **Service Inventory**: 8003
- **Service Billing**: 8004
- **Service CRM**: 8005
- **Service KDS**: 8006
- **Service Admin**: 8008
- **PostgreSQL**: 5432

---

## 15. DATABASE NAMING CONVENTIONS

### Tables
- Use `snake_case`: `inventory_items`, `employee_roles`
- Prefix with module: `inv_*, order_*, emp_*` (optional)

### Columns
- Primary key: `id` (Integer, autoincrement)
- Foreign keys: `{entity}_id`
- Timestamps: `created_at`, `updated_at`
- Booleans: `is_{adjective}` (e.g., `is_active`)

### Relationships
- Many-to-Many: `{entity1}_{entity2}` table
- Foreign key constraint: `ondelete='CASCADE'`

---

## QUICK START CHECKLIST FOR NEW FEATURES

1. **Create Model** (`models/my_model.py`)
   - Define SQLAlchemy class inheriting from Base
   - Add relationships and indexes

2. **Create Schema** (`schemas/my_schema.py`)
   - Create Base, Create, Update, InDB, Response, List classes

3. **Create Service** (`services/my_service.py`)
   - Implement CRUD operations
   - Add business logic

4. **Create Router** (`routers/my_router.py`)
   - Define endpoints with schemas
   - Add RBAC decorators if needed
   - Inject service and db dependencies

5. **Register Router** (`main.py`)
   - Import router
   - Include with prefix and tags

6. **Add Tests** (`tests/test_my_feature.py`)
   - Create test fixtures
   - Test CRUD operations
   - Test error handling

7. **Update .env.example**
   - Add any new environment variables

---

