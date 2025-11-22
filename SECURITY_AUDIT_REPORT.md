# BIZTONSÁGI AUDIT JELENTÉS
**POS Projekt v1.4 - Memoria**
**Audit dátum:** 2025-11-22
**Ágens:** #9 - Security Audit
**Auditált komponensek:** JWT, RBAC, Input Validation, Env-vars, Adatvédelem, SQL Injection, XSS, CSRF

---

## EXECUTIVE SUMMARY

A POS rendszer biztonsági auditja során **8 kritikus/közepes biztonsági hibát** azonosítottunk, melyek azonnali javítást igényelnek production környezetben. A rendszer ugyanakkor **erős alapokat** mutat a RBAC implementációban, SQL injection védelem terén és input validation területén.

**Összesített kockázati értékelés:**
- 🔴 **KRITIKUS (HIGH):** 4 hiba
- 🟡 **KÖZEPES (MEDIUM):** 4 hiba
- 🟢 **ALACSONY (LOW):** 2 hiba
- ✅ **ERŐSSÉGEK:** 7 komponens

---

## 1. JWT KEZELÉS AUDIT

### 1.1 Implementáció Áttekintés

**Fájlok:**
- `backend/service_admin/services/auth_service.py` (125-220 sorok)
- `backend/service_admin/dependencies.py` (86-221 sorok)
- `backend/service_admin/config.py` (104-120 sorok)

**JWT Library:** PyJWT (auth_service.py) és python-jose (dependencies.py)

**Token Generálás:**
```python
# auth_service.py:170-176
token = jwt.encode(
    payload,        # {sub: employee_id, iat: timestamp, exp: timestamp}
    self.secret_key,
    algorithm=self.algorithm  # HS256
)
```

**Token Validáció:**
```python
# dependencies.py:183-196
payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
employee_id = int(payload.get("sub"))
```

### 1.2 Feltárt Hibák

#### 🔴 **HIBA #1: Nincs Refresh Token Mechanizmus**

**Fájl:** `backend/service_admin/services/auth_service.py`

**Probléma:**
- Csak access token van implementálva (60 perc lejárat)
- Nincs refresh token endpoint
- Kompromittált token-ek nem visszavonhatók lejárat előtt
- Nincs token blacklist/revocation list

**Miért veszélyes:**
- Ha egy token ellopják, 60 percig használható marad
- Nincs lehetőség távoli kijelentkeztetésre
- Session management hiányos (stateless JWT csak)

**Kockázati szint:** 🔴 **HIGH**

**Javítási terv:**
1. Implementáld refresh token mechanizmust (7 napos lejárat)
2. Adj hozzá refresh endpoint-ot: `POST /auth/refresh`
3. Használj Redis-t token blacklist tárolására
4. Implementálj logout endpoint-ot token revocation-nel

**Javasolt implementáció:**
```python
# auth_service.py - új metódusok
def create_refresh_token(self, employee_id: int) -> str:
    payload = {
        "sub": str(employee_id),
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

def revoke_token(self, token: str):
    # Redis blacklist tárolás
    redis_client.setex(
        f"blacklist:{token}",
        timedelta(minutes=60),
        "revoked"
    )
```

---

#### 🟡 **HIBA #2: JWT Secret Key Védelem Hiányos**

**Fájl:** `backend/service_admin/config.py:104-108`

**Probléma:**
```python
jwt_secret_key: str = Field(
    ...,
    description="Secret key for JWT token signing",
    min_length=32  # ✅ Jó: minimum 32 karakter
)
```

- Secret key `.env` fájlban plain text
- Nincs környezet-specifikus secret rotation
- Nincs HashiCorp Vault / AWS Secrets Manager integráció

**Példa `.env.example` fájlból:**
```bash
# .env.example:36
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
```

**Miért veszélyes:**
- `.env` fájl Git-ben (ha véletlenül commit-olják)
- Nincs automated secret rotation
- Developer gépen plain text tárolás

**Kockázati szint:** 🟡 **MEDIUM**

**Javítási terv:**
1. **Secrets Management Service:**
   - HashiCorp Vault (self-hosted)
   - AWS Secrets Manager (cloud)
   - Azure Key Vault (cloud)

2. **Secret Rotation Policy:**
   - 90 naponként automatikus rotation
   - Multi-version secret support (graceful rollover)

3. **Docker Secrets használata production-ben:**
```yaml
# docker-compose.prod.yml
services:
  service_admin:
    secrets:
      - jwt_secret_key
secrets:
  jwt_secret_key:
    external: true
```

---

#### 🟢 **ERŐSSÉG #1: HS256 Algoritmus + Expiration**

**Pozitívumok:**
- ✅ HS256 algoritmus (szimmetrikus, gyors)
- ✅ Token expiration enforcement (`exp` claim)
- ✅ Issued at timestamp (`iat` claim)
- ✅ Type checking (`type: "access"`)

**Config validáció:**
```python
# config.py:115-120
jwt_access_token_expire_minutes: int = Field(
    default=60,
    description="JWT access token expiration time in minutes",
    ge=5,    # Minimum 5 perc
    le=1440  # Maximum 24 óra
)
```

---

## 2. RBAC (ROLE-BASED ACCESS CONTROL) AUDIT

### 2.1 Implementáció Áttekintés

**Adatmodellek:**
- `backend/service_admin/models/employee.py` - Employee (Many-to-Many Role)
- `backend/service_admin/models/role.py` - Role (Many-to-Many Permission)
- `backend/service_admin/models/permission.py` - Permission (resource:action)

**RBAC Architektúra:**
```
Employee → [employee_roles] → Role → [role_permissions] → Permission
```

**Permission Formátum:** `resource:action`
- Példák: `orders:create`, `inventory:manage`, `admin:all`

**Authorization Dependency:**
```python
# dependencies.py:246-306
def require_permission(permission_name: str) -> Callable:
    async def permission_checker(current_user: Employee = Depends(get_current_user)):
        if not current_user.has_permission(permission_name):
            raise HTTPException(status_code=403, detail="Permission denied")
        return current_user
    return permission_checker
```

**Használat endpoint-okban:**
```python
@app.post("/orders", dependencies=[Depends(require_permission("orders:create"))])
async def create_order(...):
    ...
```

### 2.2 Feltárt Hibák

#### 🟢 **ERŐSSÉG #2: Granulált Permission Rendszer**

**Pozitívumok:**
- ✅ Resource-based permissions (`resource:action` formátum)
- ✅ Több permission ellenőrzés támogatása:
  - `require_permission()` - egyetlen permission
  - `require_any_permission()` - bármelyik a listából
  - `require_all_permissions()` - mindegyik szükséges
- ✅ System permissions védelem (`is_system` flag)
- ✅ Eager loading (SQLAlchemy `joinedload`) - nincs N+1 query probléma

**Permission példák seed_rbac.py-ból:**
```python
# Alapvető jogosultságok
"orders:manage", "orders:view", "orders:create"
"menu:manage", "menu:view"
"inventory:manage", "inventory:view"
"employees:manage"
"roles:manage"
"permissions:manage"
"reports:view"
"admin:all"
```

**Employee Permission Aggregáció:**
```python
# employee.py:92-103
@property
def permissions(self):
    """Összegyűjti az összes jogosultságot az alkalmazott szerepköreiből."""
    perms = set()
    for role in self.roles:
        perms.update(role.permissions)
    return perms
```

---

#### 🟡 **HIBA #3: Nincs Permission Audit Trail**

**Probléma:**
- Nincs logging amikor permission check fail-el
- Nincs tracking ki próbált milyen jogosultság nélküli műveletet végrehajtani
- AuditLog modell létezik (`backend/service_admin/models/audit_log.py`), de csak NTAK műveletek lógózva

**Miért veszélyes:**
- Nem észlelhető insider threat
- Nincs forensic trail permission abuse esetén
- SOC2/ISO27001 compliance problémák

**Kockázati szint:** 🟡 **MEDIUM**

**Javítási terv:**

1. **Bővítsd az AuditLog modellt:**
```python
# audit_log.py - új event típusok
class AuditEventType(str, Enum):
    NTAK_SEND = "NTAK_SEND"
    NTAK_CANCEL = "NTAK_CANCEL"
    # ÚJ:
    PERMISSION_DENIED = "PERMISSION_DENIED"
    PERMISSION_GRANTED = "PERMISSION_GRANTED"
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED"
```

2. **Logold permission failures-t:**
```python
# dependencies.py:296-303 - módosított
if not current_user.has_permission(permission_name):
    # Log permission denial
    audit_log = AuditLog(
        event_type="PERMISSION_DENIED",
        employee_id=current_user.id,
        details={
            "permission": permission_name,
            "endpoint": request.url.path,
            "method": request.method
        }
    )
    db.add(audit_log)
    db.commit()

    raise HTTPException(status_code=403, ...)
```

---

## 3. INPUT VALIDATION AUDIT

### 3.1 Implementáció Áttekintés

**Pydantic Schemas:** 62+ schema fájl
- `backend/service_admin/schemas/auth.py`
- `backend/service_admin/schemas/employee.py`
- `backend/service_orders/schemas/order.py`
- stb.

**Példa validációk:**

**Username validáció:**
```python
# schemas/employee.py:18-25
username: str = Field(
    ...,
    min_length=3,
    max_length=50,
    pattern=r"^[a-zA-Z0-9_\-]+$",  # ✅ Regex védelem special chars ellen
    description="Unique username for login"
)
```

**Email validáció:**
```python
# schemas/employee.py:26-30
email: EmailStr = Field(...)  # ✅ Pydantic EmailStr type
```

**Password validáció:**
```python
# schemas/auth.py:144-150
new_password: str = Field(
    ...,
    min_length=8,  # ✅ Minimum 8 karakter
    max_length=255,
    description="New password (minimum 8 characters)"
)
```

### 3.2 Feltárt Hibák

#### 🟢 **ERŐSSÉG #3: Átfogó Pydantic Validáció**

**Pozitívumok:**
- ✅ Minden API endpoint Pydantic schema-val védett
- ✅ Regex pattern validáció (username, email, stb.)
- ✅ Length constraints (min/max)
- ✅ Type safety (int, str, EmailStr, HttpUrl)
- ✅ Range validáció (ge=, le= constraints)

**Példa range validáció:**
```python
# config.py:26-31
port: int = Field(
    default=8008,
    ge=1024,   # >= 1024
    le=65535   # <= 65535
)
```

---

#### 🔴 **HIBA #4: PIN Kód Minimum Hossz Túl Rövid**

**Fájl:** `backend/service_admin/config.py:122-128`

**Probléma:**
```python
pin_code_min_length: int = Field(
    default=4,  # ❌ 4 digit = 10,000 kombináció
    description="Minimum PIN code length",
    ge=4,
    le=8
)
```

**Miért veszélyes:**
- 4 digit PIN: 10,000 kombináció (0000-9999)
- Brute force attack ~10 másodperc alatt (1000 req/sec)
- Rate limiting nélkül könnyen feltörhető

**Kockázati szint:** 🔴 **HIGH** (rate limiting nélkül)

**Javítási terv:**

1. **Növeld minimum PIN hosszt 6 digit-re:**
```python
pin_code_min_length: int = Field(
    default=6,  # ✅ 6 digit = 1,000,000 kombináció
    ge=6,       # Minimum 6
    le=8
)
```

2. **Implementálj Rate Limiting** (lásd HIBA #5)

---

## 4. ENVIRONMENT VARIABLES ÉS SECRETS MANAGEMENT AUDIT

### 4.1 Implementáció Áttekintés

**Config Management:**
- Pydantic Settings (`pydantic_settings.BaseSettings`)
- `.env` fájl betöltés automatikusan
- Type-safe configuration

**Kritikus secrets:**
```bash
# .env.example
POSTGRES_PASSWORD=pos_password_dev
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
NTAK_API_KEY=your-ntak-api-key
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/gcp-key.json
```

**Config validáció:**
```python
# config.py:104-108
jwt_secret_key: str = Field(
    ...,                # Required field
    min_length=32       # ✅ Minimum 32 karakter enforcement
)
```

### 4.2 Feltárt Hibák

#### 🟡 **HIBA #5: Hiányzik .env Fájl Védelem**

**Probléma:**
- `.env` fájl nincs `.gitignore`-ban explicit említve
- `.env.example` tartalmaz placeholder értékeket
- Nincs automated secret scanning (git hooks)

**Ellenőrzés:**
```bash
# .gitignore fájl
*.env  # ✅ Jó, ha ez benne van
.env   # ✅ Explicit említés ajánlott
```

**Miért veszélyes:**
- Developer véletlenül commit-olhatja `.env`-t
- Secrets leak GitHub-ra
- Credential harvesting bots automatikusan scannelik

**Kockázati szint:** 🟡 **MEDIUM**

**Javítási terv:**

1. **.gitignore megerősítés:**
```bash
# .gitignore
.env
.env.local
.env.*.local
*.env
credentials/
```

2. **Git Hooks telepítése:**
```bash
# .git/hooks/pre-commit
#!/bin/bash
if git diff --cached --name-only | grep -E '\.env$|credentials'; then
  echo "❌ HIBA: .env vagy credentials fájl commit-olva!"
  echo "Töröld a staged fájlokat: git reset HEAD .env"
  exit 1
fi
```

3. **GitHub Secret Scanning engedélyezése:**
   - GitHub repo Settings → Security → Secret scanning → Enable

4. **Trufflehog használata CI/CD-ben:**
```yaml
# .github/workflows/security.yml
- name: TruffleHog Secret Scan
  uses: trufflesecurity/trufflehog@main
  with:
    path: ./
```

---

## 5. ADATVÉDELEM (DATA PROTECTION) AUDIT

### 5.1 Implementáció Áttekintés

**Érzékeny adatok kezelése:**

1. **PIN kód tárolás:**
```python
# auth_service.py:336-338
def hash_pin_code(self, pin_code: str) -> str:
    return self.pwd_context.hash(pin_code)  # ✅ Bcrypt hash
```

2. **Password hash tárolás:**
```python
# employee.py:46-48
pin_code_hash = Column(String(255), nullable=False)
# ✅ Soha nem tárolja plain text password-öt
```

3. **API Response-ban password exclusion:**
```python
# schemas/employee.py:122-128
class EmployeeResponse(BaseModel):
    # ❌ password_hash NINCS ebben a schema-ban
    id: int
    username: str
    email: EmailStr
    # ...
```

### 5.2 Feltárt Hibák

#### 🟢 **ERŐSSÉG #4: Bcrypt Password Hashing**

**Pozitívumok:**
- ✅ Passlib CryptContext bcrypt scheme
- ✅ Automatikus salt generation
- ✅ Work factor konfiguráció lehetséges
- ✅ Password hash soha nem kerül API response-ba

**Implementáció:**
```python
# dependencies.py:44-46
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
```

**Hash verification:**
```python
# auth_service.py:111-118
if self.pwd_context.verify(pin_code, employee.pin_code_hash):
    return employee
else:
    return None
```

---

#### 🟢 **ERŐSSÉG #5: Inactive User Check**

**Pozitívumok:**
- ✅ `is_active` flag minden Employee-nál
- ✅ Login során ellenőrzés (`auth_service.py:104-106`)
- ✅ Token validáció során újra ellenőrzés (`dependencies.py:214-218`)

**Kétszeres védelem:**
```python
# 1. Login során
if not employee.is_active:
    return None  # Hitelesítés sikertelen

# 2. Token validáció során
if not employee.is_active:
    raise HTTPException(status_code=403, detail="Inactive user")
```

---

## 6. SQL INJECTION AUDIT

### 6.1 Implementáció Áttekintés

**ORM Használat:** SQLAlchemy (100% lefedettség)

**Query példák:**
```python
# Paraméterezett query (SAFE)
employee = db.query(Employee).filter(
    Employee.username == username  # ✅ Paraméterezett
).first()

# Eager loading (SAFE)
employee = db.query(Employee)\
    .options(joinedload(Employee.roles).joinedload(Role.permissions))\
    .filter(Employee.id == employee_id)\
    .first()
```

**Raw SQL ellenőrzés:**
```bash
# Grep keresés eredménye
grep -r "\.execute\(" backend/
# Találat: 0 fájl ❌ (nincs raw SQL!)
```

### 6.2 Feltárt Hibák

#### ✅ **ERŐSSÉG #6: 100% ORM Használat - SQL Injection Védelem**

**Pozitívumok:**
- ✅ **NINCS raw SQL** a teljes codebase-ben
- ✅ SQLAlchemy ORM 100% használat
- ✅ Paraméterezett query-k mindenhol
- ✅ Type-safe query construction

**Ellenőrzött minták:**
```python
# ❌ NINCS ilyen kód:
db.execute(f"SELECT * FROM users WHERE id = {user_id}")  # SQL Injection!
db.execute(text(f"SELECT * FROM users WHERE username = '{username}'"))

# ✅ CSAK ilyen van:
db.query(User).filter(User.id == user_id).first()
db.query(User).filter(User.username == username).first()
```

**Következtetés:** SQL Injection kockázat: **MINIMÁLIS** ✅

---

## 7. XSS (CROSS-SITE SCRIPTING) AUDIT

### 7.1 Implementáció Áttekintés

**Backend architektúra:** RESTful API (FastAPI)
- JSON request/response
- Nincs server-side HTML rendering
- Frontend (React/Vue/Angular) külön kezeli rendering-et

**Pydantic Response Serialization:**
```python
# FastAPI automatikusan JSON-t ad vissza
@app.get("/employees/{employee_id}", response_model=EmployeeResponse)
async def get_employee(employee_id: int):
    return employee  # ✅ Pydantic auto-serialize to JSON
```

### 7.2 Feltárt Hibák

#### 🟢 **ERŐSSÉG #7: JSON API - Beépített XSS Védelem**

**Pozitívumok:**
- ✅ RESTful JSON API (nincs HTML output backend-ből)
- ✅ Pydantic serialization (type-safe JSON)
- ✅ FastAPI automatikus escape-elés
- ✅ Content-Type: application/json minden response-ban

**XSS védelem mechanizmus:**
```
Backend (FastAPI) → JSON Response → Frontend (React)
                    ↑ Automatic escaping
```

**Frontend felelősség:**
- Frontend-nek kell kezelni user input sanitization-t
- React automatikusan escape-eli JSX-ben megjelenített szöveget
- Vue.js automatikusan escape-eli template-ben megjelenített szöveget

**Backend XSS kockázat:** **ALACSONY** ✅
*Megjegyzés: Frontend audit szükséges külön!*

---

#### 🟡 **HIBA #6: Hiányzó Security Header-ek**

**Probléma:**
- Nincs `X-Content-Type-Options` header
- Nincs `X-Frame-Options` header
- Nincs `Content-Security-Policy` header
- Nincs `X-XSS-Protection` header

**Miért veszélyes:**
- MIME type sniffing attack lehetséges
- Clickjacking attack lehetséges
- XSS attack kibővítése CSP nélkül

**Kockázati szint:** 🟡 **MEDIUM**

**Javítási terv:**

**Adj hozzá Security Headers middleware-t:**
```python
# main.py - minden service-ben
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

---

## 8. CSRF (CROSS-SITE REQUEST FORGERY) AUDIT

### 8.1 Implementáció Áttekintés

**CORS konfiguráció minden service-ben:**
```python
# main.py (service_admin, service_orders, service_menu, stb.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # ❌ KRITIKUS HIBA!
    allow_credentials=True,     # ❌ Veszélyes combination
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Fájlok (6 service):**
- `backend/service_admin/main.py:69`
- `backend/service_orders/main.py:39`
- `backend/service_menu/main.py:39`
- `backend/service_inventory/main.py:42`
- `backend/service_logistics/main.py:32`
- `backend/service_crm/main.py:29`

### 8.2 Feltárt Hibák

#### 🔴 **HIBA #7: CORS Wildcard Origins - CSRF Támadás Lehetséges**

**Fájl:** Minden service `main.py`

**Probléma:**
```python
allow_origins=["*"],         # ❌ Minden origin engedélyezve
allow_credentials=True,      # ❌ Credentials (cookies/JWT) küldése engedélyezve
```

**Miért KRITIKUSAN veszélyes:**

1. **CSRF Attack Scenario:**
```html
<!-- Támadó oldal: evil.com -->
<script>
fetch('https://pos-api.example.com/api/v1/orders', {
  method: 'POST',
  credentials: 'include',  // Küldi a JWT tokent
  headers: {
    'Authorization': 'Bearer ' + stolenToken,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({order_items: [...]})
});
</script>
```

2. **Credential Theft:**
- `allow_credentials=true` + `allow_origins=["*"]` kombináció lehetővé teszi credential küldést bármely origin-ről

3. **Production Exposure:**
- Komment szerint "Configure appropriately for production" de nincs enforcement
- Developer elfelejthet production config-ot beállítani

**Kockázati szint:** 🔴 **CRITICAL**

**Javítási terv:**

1. **Environment-based CORS config:**
```python
# config.py - új field
allowed_origins: list[str] = Field(
    default=["http://localhost:3000"],  # Development default
    description="Allowed CORS origins (comma-separated in .env)"
)
```

2. **main.py - dinamikus CORS:**
```python
# main.py - minden service
from backend.service_admin.config import settings

# PRODUCTION-ban strict CORS
if settings.environment == "production":
    allowed_origins = settings.allowed_origins
else:
    # Development-ben engedékeny (de NE *)
    allowed_origins = ["http://localhost:3000", "http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,      # ✅ Explicit origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],  # ✅ Explicit methods
    allow_headers=["Authorization", "Content-Type"],          # ✅ Explicit headers
)
```

3. **CSRF Token implementáció (opcionális, ha cookie-based auth):**
```python
# FastAPI CSRF middleware
from fastapi_csrf_protect import CsrfProtect

@app.post("/orders")
async def create_order(csrf_token: str = Depends(CsrfProtect.validate_csrf)):
    ...
```

---

#### 🔴 **HIBA #8: Internal API Endpoint-ok Védtelenek**

**Fájl:** `backend/service_inventory/routers/internal_router.py`

**Probléma:**
```python
# internal_router.py:5-7
"""
These endpoints are NOT meant to be called by external clients.
They do NOT have RBAC protection (service-to-service trust assumed).
"""

@internal_router.post("/deduct-stock")
def deduct_stock_for_order(...):
    # ❌ NINCS authentication
    # ❌ NINCS authorization
```

**Endpoints (védtelenek):**
- `POST /internal/deduct-stock` - Készletcsökkentés
- `GET /internal/health` - Internal health check

**Miért veszélyes:**
- Network-level security-re támaszkodik (Docker network isolation)
- Ha valaki hozzáfér a network-höz, hívhatja ezeket az endpoint-okat
- Nincs API key validáció
- Nincs IP whitelist

**Attack scenario:**
```bash
# Ha támadó hozzáfér a Docker network-höz vagy VPN-hez
curl -X POST http://service_inventory:8003/internal/deduct-stock \
  -H "Content-Type: application/json" \
  -d '{"order_id": 999, "malicious_data": "..."}'
```

**Kockázati szint:** 🔴 **HIGH**

**Javítási terv:**

1. **Service-to-Service API Key Authentication:**
```python
# config.py - új field
internal_api_key: str = Field(
    ...,
    description="API key for internal service-to-service communication",
    min_length=32
)
```

2. **Internal API Middleware:**
```python
# internal_router.py - új dependency
from fastapi import Header, HTTPException

async def verify_internal_api_key(
    x_internal_api_key: str = Header(..., alias="X-Internal-API-Key")
):
    if x_internal_api_key != settings.internal_api_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid internal API key"
        )
    return True

# Használat
@internal_router.post(
    "/deduct-stock",
    dependencies=[Depends(verify_internal_api_key)]
)
def deduct_stock_for_order(...):
    ...
```

3. **Mutual TLS (mTLS) implementáció (advanced):**
   - Service-to-service communication TLS certificate-tel
   - Kubernetes: Istio/Linkerd service mesh mTLS

---

#### 🔴 **HIBA #9: Nincs Rate Limiting**

**Probléma:**
- `/auth/login` endpoint nincs rate limit-elve
- Brute force attack lehetséges PIN kódokra
- DDoS protection hiányzik

**Attack scenario:**
```python
# Brute force script
for pin in range(0, 10000):  # 4 digit PIN-ek
    response = requests.post(
        "https://api.pos.com/auth/login",
        json={"username": "admin", "password": f"{pin:04d}"}
    )
    if response.status_code == 200:
        print(f"PIN found: {pin:04d}")
        break
```

**Kockázati szint:** 🔴 **HIGH**

**Javítási terv:**

1. **SlowAPI rate limiting middleware:**
```python
# requirements.txt
slowapi==0.1.9

# main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# auth.py
from slowapi import Limiter

@auth_router.post("/login")
@limiter.limit("5/minute")  # ✅ Max 5 login kísérlet / perc / IP
async def login(request: Request, credentials: LoginRequest):
    ...
```

2. **Redis-based distributed rate limiting:**
```python
# config.py
redis_url: str = Field(
    default="redis://localhost:6379",
    description="Redis URL for rate limiting"
)

# Rate limiter with Redis backend
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.redis_url
)
```

3. **Account lockout policy:**
```python
# Employee model - új field
failed_login_attempts: int = Column(Integer, default=0)
locked_until: datetime | None = Column(TIMESTAMP(timezone=True), nullable=True)

# auth_service.py
def authenticate_employee(self, username: str, pin_code: str):
    employee = self.db.query(Employee).filter(Employee.username == username).first()

    # Account lockout check
    if employee and employee.locked_until:
        if datetime.utcnow() < employee.locked_until:
            raise HTTPException(status_code=423, detail="Account locked. Try again later.")
        else:
            employee.locked_until = None
            employee.failed_login_attempts = 0

    # Password check
    if not self.pwd_context.verify(pin_code, employee.pin_code_hash):
        employee.failed_login_attempts += 1
        if employee.failed_login_attempts >= 5:
            employee.locked_until = datetime.utcnow() + timedelta(minutes=15)
        self.db.commit()
        return None

    # Successful login - reset attempts
    employee.failed_login_attempts = 0
    self.db.commit()
    return employee
```

---

## 9. TOVÁBBI BIZTONSÁGI MEGFIGYELÉSEK

### 9.1 Hiányzik HTTPS Enforcement

**Probléma:**
- Nincs HTTP → HTTPS redirect middleware
- Production-ben HTTPS használat nincs enforced

**Javítási terv:**
```python
# main.py
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if settings.environment == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

### 9.2 Nincs Request Logging

**Probléma:**
- Nincs centralized request/response logging
- Audit trail hiányos (csak NTAK műveletek)

**Javítási terv:**
```python
# middleware/logging.py
import logging
from starlette.middleware.base import BaseHTTPMiddleware

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        logger.info(f"{request.method} {request.url.path} - User: {request.state.user}")
        response = await call_next(request)
        logger.info(f"Response: {response.status_code}")
        return response

app.add_middleware(RequestLoggingMiddleware)
```

---

## 10. ÖSSZEFOGLALÁS ÉS PRIORITÁSOK

### 10.1 Kritikus Hibák (Azonnali javítás szükséges) 🔴

| # | Hiba | Fájl | Kockázat |
|---|------|------|----------|
| 7 | **CORS Wildcard Origins** | `*/main.py:69` | CSRF támadás |
| 8 | **Internal API védtelen** | `internal_router.py` | Unauthorized access |
| 9 | **Nincs Rate Limiting** | `auth.py:50` | Brute force |
| 4 | **PIN kód túl rövid** | `config.py:124` | Brute force |

### 10.2 Közepes Hibák (30 napon belül) 🟡

| # | Hiba | Fájl | Kockázat |
|---|------|------|----------|
| 2 | **JWT Secret plain text** | `.env` | Secret leak |
| 3 | **Nincs Permission Audit** | `audit_log.py` | Insider threat |
| 5 | **.env védelem hiányzik** | `.gitignore` | Credential leak |
| 6 | **Hiányzó Security Headers** | `main.py` | XSS/Clickjacking |

### 10.3 Alacsony Kockázatú 🟢

- Nincs HTTPS enforcement middleware
- Nincs centralized request logging

### 10.4 Erősségek ✅

1. ✅ **100% ORM használat** - SQL Injection védelem
2. ✅ **Bcrypt password hashing** - Erős kriptográfia
3. ✅ **Granulált RBAC** - Resource-based permissions
4. ✅ **Pydantic validáció** - Type-safe input validation
5. ✅ **JWT expiration** - Token lifecycle management
6. ✅ **Inactive user check** - Account management
7. ✅ **JSON API** - Beépített XSS védelem

---

## 11. JAVÍTÁSI ÜTEMTERV

### 11.1 Sprint 1 (Week 1-2) - Kritikus Hibák

**Feladat:**
1. ✅ CORS konfiguráció javítása (environment-based)
2. ✅ Rate limiting implementáció (SlowAPI)
3. ✅ Internal API key authentication
4. ✅ PIN kód minimum 6 digit

**Effort:** 2-3 nap development + 1 nap testing

### 11.2 Sprint 2 (Week 3-4) - Közepes Hibák

**Feladat:**
1. ✅ Secrets Management (HashiCorp Vault vagy AWS Secrets Manager)
2. ✅ Permission Audit Trail
3. ✅ Security Headers Middleware
4. ✅ Git hooks (pre-commit secret scanning)

**Effort:** 3-4 nap development + 1 nap testing

### 11.3 Sprint 3 (Week 5-6) - Fejlesztések

**Feladat:**
1. ✅ Refresh Token mechanizmus
2. ✅ Token revocation (Redis blacklist)
3. ✅ HTTPS enforcement
4. ✅ Centralized logging (ELK stack vagy Grafana Loki)

**Effort:** 4-5 nap development + 2 nap testing

---

## 12. DEVSECOPS JAVASLATOK

### 12.1 CI/CD Security Pipeline

**GitHub Actions Workflow:**
```yaml
# .github/workflows/security.yml
name: Security Checks

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      # 1. Secret Scanning
      - name: TruffleHog Secret Scan
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./

      # 2. Dependency Vulnerability Scan
      - name: Safety Check (Python)
        run: |
          pip install safety
          safety check --json

      # 3. SAST (Static Analysis)
      - name: Bandit Security Linter
        run: |
          pip install bandit
          bandit -r backend/ -f json -o bandit-report.json

      # 4. Container Scanning
      - name: Trivy Container Scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'pos-backend:latest'
          format: 'sarif'
          output: 'trivy-results.sarif'

      # 5. DAST (Dynamic Analysis) - optional
      - name: OWASP ZAP Scan
        uses: zaproxy/action-baseline@v0.7.0
        with:
          target: 'http://localhost:8000'
```

### 12.2 Security Tools Stack

**SAST (Static Analysis):**
- **Bandit** - Python security linter
- **Semgrep** - Multi-language security patterns
- **CodeQL** - GitHub Advanced Security

**Dependency Scanning:**
- **Safety** - Python dependency vulnerability scanner
- **pip-audit** - PyPI package vulnerability scanner
- **Dependabot** - GitHub automated dependency updates

**Secret Scanning:**
- **TruffleHog** - High entropy secret detection
- **GitGuardian** - Real-time secret detection
- **GitHub Secret Scanning** - Native GitHub feature

**Container Security:**
- **Trivy** - Container vulnerability scanner
- **Clair** - Container static analysis
- **Snyk** - Container and dependency scanning

**DAST (Dynamic Analysis):**
- **OWASP ZAP** - Web application security scanner
- **Burp Suite** - Professional penetration testing

### 12.3 Security Monitoring (Production)

**Runtime Security:**
```yaml
# Prometheus + Grafana monitoring
- name: Failed login attempts
  expr: rate(login_failed_total[5m]) > 10
  severity: warning

- name: Permission denied spike
  expr: rate(permission_denied_total[5m]) > 20
  severity: critical

- name: Internal API unauthorized access
  expr: rate(internal_api_unauthorized[1m]) > 0
  severity: critical
```

**Log Aggregation:**
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Grafana Loki** - Log aggregation for Kubernetes
- **Datadog** - Cloud-native monitoring

### 12.4 Penetration Testing Schedule

**Frequency:**
- **Quarterly:** Internal security audit
- **Bi-annually:** External penetration test (third-party)
- **Annually:** Full security assessment + compliance audit (ISO27001, SOC2)

**Scope:**
- API security testing (OWASP API Top 10)
- Authentication bypass attempts
- Authorization flaw testing
- SQL Injection / XSS / CSRF testing
- Business logic vulnerabilities

---

## 13. COMPLIANCE ÉS SZABVÁNYOK

### 13.1 OWASP Top 10 Compliance

| OWASP Risk | Status | Megjegyzés |
|------------|--------|------------|
| A01 - Broken Access Control | 🟡 **Partial** | RBAC jó, de internal API védtelen |
| A02 - Cryptographic Failures | ✅ **Good** | Bcrypt hashing, JWT encryption |
| A03 - Injection | ✅ **Good** | 100% ORM, SQL injection védelem |
| A04 - Insecure Design | 🟡 **Partial** | CORS wildcard, nincs rate limiting |
| A05 - Security Misconfiguration | 🔴 **Poor** | CORS *, missing headers, secrets in .env |
| A06 - Vulnerable Components | ⚠️ **Unknown** | Dependency scan szükséges |
| A07 - Authentication Failures | 🟡 **Partial** | Nincs rate limiting, account lockout |
| A08 - Software/Data Integrity | ✅ **Good** | Pydantic validation, type safety |
| A09 - Logging/Monitoring Failures | 🔴 **Poor** | Audit trail hiányos, nincs centralized logging |
| A10 - SSRF | ✅ **Good** | Nincs user-controlled URL fetch |

### 13.2 GDPR Compliance (ha alkalmazandó)

**Adatvédelmi követelmények:**
- ✅ Password hashing (bcrypt)
- ✅ PIN kód hash-elés
- ⚠️ Nincs data retention policy
- ⚠️ Nincs data deletion endpoint (right to be forgotten)
- ⚠️ Nincs encryption at rest (database level)

**Javaslatok:**
1. Adj hozzá `DELETE /employees/{id}/gdpr` endpoint (teljes adat törlés)
2. Implementálj data retention policy (automatikus törlés N nap után)
3. Engedélyezd PostgreSQL transparent data encryption (TDE)

---

## 14. KÖVETKEZTETÉS

A POS rendszer **erős alapokkal rendelkezik** a RBAC, input validation és SQL injection védelem terén. Ugyanakkor **4 kritikus biztonsági hiba** azonnali javítást igényel production használat előtt:

1. **CORS wildcard origins** → Environment-based CORS config
2. **Internal API védtelen** → API key authentication
3. **Nincs rate limiting** → SlowAPI middleware
4. **PIN kód túl rövid** → Minimum 6 digit

**Javasolt lépések:**
1. Implementáld a **Sprint 1 javításokat** (Week 1-2)
2. Telepítsd a **DevSecOps pipeline-t** (GitHub Actions)
3. Végezz **penetration testing-et** külső auditor-ral
4. Rendszeres **security monitoring** production-ben

**Biztonsági posture értékelés:**
- **Jelenlegi:** 🟡 **MEDIUM** (development-re alkalmas, production-re NEM)
- **Sprint 1 után:** 🟢 **GOOD** (production-ready alapszinten)
- **Sprint 2-3 után:** 🟢 **EXCELLENT** (enterprise-grade security)

---

**Készítette:** Ágens #9 - Security Audit
**Dátum:** 2025-11-22
**Verzió:** 1.0
**Következő audit:** 2025-12-22 (30 nap múlva)
