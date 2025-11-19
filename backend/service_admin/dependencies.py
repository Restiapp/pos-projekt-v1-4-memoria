"""
FastAPI Dependencies - Module 6: RBAC & Authentication
Modul 6 - FastAPI Függőségek (Middleware Alap)

Ez a modul tartalmazza az összes kritikus FastAPI dependency-t:
- JWT token kezelés (create, decode)
- Felhasználó autentikáció (get_current_user)
- RBAC jogosultság-ellenőrzés (require_permission)
- Service dependency factories

Használat:
    @app.get("/orders", dependencies=[Depends(require_permission("orders:view"))])
    async def get_orders(current_user: Employee = Depends(get_current_user)):
        ...
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session, joinedload

from backend.service_admin.models.database import get_db
from backend.service_admin.models.employee import Employee
from backend.service_admin.models.role import Role
from backend.service_admin.models.permission import Permission


# ============================================================================
# JWT & Password Configuration
# ============================================================================

# JWT Secret Key (load from settings - CRITICAL: No insecure default)
from backend.service_admin.config import settings

SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_access_token_expire_minutes

# Password hashing context (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme for FastAPI
security = HTTPBearer()


# ============================================================================
# Password Utilities
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Ellenőrzi, hogy a nyílt szövegű jelszó megegyezik-e a hash-elt jelszóval.

    Args:
        plain_password: Nyílt szövegű jelszó (PIN kód)
        hashed_password: Hash-elt jelszó (adatbázisból)

    Returns:
        bool: True ha egyezik, False ha nem
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash-eli a nyílt szövegű jelszót bcrypt használatával.

    Args:
        password: Nyílt szövegű jelszó (PIN kód)

    Returns:
        str: Hash-elt jelszó
    """
    return pwd_context.hash(password)


# ============================================================================
# JWT Token Utilities
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT access token létrehozása.

    Args:
        data: Token payload (pl. {"sub": "username", "employee_id": 123})
        expires_delta: Token lejárati idő (opcionális)

    Returns:
        str: Kódolt JWT token

    Example:
        token = create_access_token(
            data={"sub": employee.username, "employee_id": employee.id},
            expires_delta=timedelta(minutes=60)
        )
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),  # Issued at
        "type": "access"
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    JWT access token dekódolása.

    Args:
        token: JWT token string

    Returns:
        dict: Token payload

    Raises:
        JWTError: Ha a token érvénytelen vagy lejárt
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================================================
# Authentication Dependencies
# ============================================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Employee:
    """
    JWT token alapján lekéri a jelenlegi felhasználót.

    Ez a függőség minden védett endpoint-nál használható a felhasználó
    azonosításához és autentikációjához.

    Args:
        credentials: HTTP Bearer token (Authorization header)
        db: Database session (dependency injection)

    Returns:
        Employee: Autentikált Employee objektum (roles és permissions betöltve)

    Raises:
        HTTPException 401: Ha a token érvénytelen, lejárt, vagy a felhasználó nem található
        HTTPException 403: Ha a felhasználó inaktív

    Example:
        @app.get("/protected")
        async def protected_route(
            current_user: Employee = Depends(get_current_user)
        ):
            return {"user": current_user.username}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Token dekódolása
        token = credentials.credentials
        payload = decode_access_token(token)

        # Employee ID kinyerése a token-ből
        employee_id_str = payload.get("sub")
        if employee_id_str is None:
            raise credentials_exception

        # Convert to int (sub field is a string in JWT standard)
        try:
            employee_id = int(employee_id_str)
        except (ValueError, TypeError):
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Employee lekérése az adatbázisból (roles és permissions eager loading)
    # Használjunk explicit joinedload-ot a roles és permissions betöltésére
    employee = db.query(Employee)\
        .options(
            joinedload(Employee.roles).joinedload(Role.permissions)
        )\
        .filter(Employee.id == employee_id)\
        .first()

    if employee is None:
        raise credentials_exception

    # Inaktív felhasználó ellenőrzése
    if not employee.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )

    return employee


async def get_current_active_user(
    current_user: Employee = Depends(get_current_user)
) -> Employee:
    """
    Aktív felhasználó lekérése (alias get_current_user-hez).

    Args:
        current_user: Employee (get_current_user dependency)

    Returns:
        Employee: Aktív Employee objektum

    Note:
        Ez a függőség redundáns, mivel a get_current_user már ellenőrzi
        az is_active státuszt. Megtartva kompatibilitás céljából.
    """
    return current_user


# ============================================================================
# RBAC Permission Dependencies
# ============================================================================

def require_permission(permission_name: str) -> Callable:
    """
    RBAC jogosultság-ellenőrző dependency factory.

    Létrehoz egy FastAPI dependency-t, ami ellenőrzi, hogy a jelenlegi
    felhasználónak van-e adott jogosultsága.

    Args:
        permission_name: Jogosultság neve (pl. "orders:create", "admin:all")

    Returns:
        Callable: FastAPI dependency függvény

    Raises:
        HTTPException 403: Ha a felhasználónak nincs meg a jogosultsága

    Example:
        @app.post("/orders", dependencies=[Depends(require_permission("orders:create"))])
        async def create_order(order_data: OrderCreate):
            ...

        @app.get("/admin/users", dependencies=[Depends(require_permission("admin:all"))])
        async def get_all_users():
            ...

    Permission Naming Convention:
        - Format: "resource:action"
        - Examples:
            - "orders:view" - Rendelések megtekintése
            - "orders:create" - Rendelés létrehozása
            - "orders:update" - Rendelés módosítása
            - "orders:delete" - Rendelés törlése
            - "inventory:manage" - Készletkezelés
            - "reports:view" - Riportok megtekintése
            - "admin:all" - Teljes admin hozzáférés
    """
    async def permission_checker(
        current_user: Employee = Depends(get_current_user)
    ) -> Employee:
        """
        Ellenőrzi, hogy a felhasználónak van-e adott jogosultsága.

        Args:
            current_user: Autentikált Employee (get_current_user dependency)

        Returns:
            Employee: Autentikált és jogosult Employee objektum

        Raises:
            HTTPException 403: Ha nincs jogosultsága
        """
        # Jogosultság ellenőrzése az Employee.has_permission() metódussal
        if not current_user.has_permission(permission_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: '{permission_name}' required"
            )

        return current_user

    return permission_checker


def require_any_permission(*permission_names: str) -> Callable:
    """
    RBAC jogosultság-ellenőrző dependency factory (bármelyik jogosultság).

    Létrehoz egy FastAPI dependency-t, ami ellenőrzi, hogy a jelenlegi
    felhasználónak van-e legalább egy a megadott jogosultságok közül.

    Args:
        *permission_names: Jogosultság nevek listája

    Returns:
        Callable: FastAPI dependency függvény

    Raises:
        HTTPException 403: Ha a felhasználónak nincs meg egyetlen jogosultsága sem

    Example:
        @app.get(
            "/reports",
            dependencies=[Depends(require_any_permission("reports:view", "admin:all"))]
        )
        async def get_reports():
            ...
    """
    async def permission_checker(
        current_user: Employee = Depends(get_current_user)
    ) -> Employee:
        """Ellenőrzi, hogy a felhasználónak van-e bármelyik jogosultsága."""
        has_any = any(
            current_user.has_permission(perm)
            for perm in permission_names
        )

        if not has_any:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: One of {permission_names} required"
            )

        return current_user

    return permission_checker


def require_all_permissions(*permission_names: str) -> Callable:
    """
    RBAC jogosultság-ellenőrző dependency factory (összes jogosultság).

    Létrehoz egy FastAPI dependency-t, ami ellenőrzi, hogy a jelenlegi
    felhasználónak van-e mindegyik megadott jogosultsága.

    Args:
        *permission_names: Jogosultság nevek listája

    Returns:
        Callable: FastAPI dependency függvény

    Raises:
        HTTPException 403: Ha a felhasználónak nincs meg minden jogosultsága

    Example:
        @app.delete(
            "/admin/users/{user_id}",
            dependencies=[Depends(require_all_permissions("admin:all", "users:delete"))]
        )
        async def delete_user(user_id: int):
            ...
    """
    async def permission_checker(
        current_user: Employee = Depends(get_current_user)
    ) -> Employee:
        """Ellenőrzi, hogy a felhasználónak van-e minden jogosultsága."""
        missing_permissions = [
            perm for perm in permission_names
            if not current_user.has_permission(perm)
        ]

        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: Missing {missing_permissions}"
            )

        return current_user

    return permission_checker


# ============================================================================
# Service Dependency Factories
# ============================================================================

# Employee Service Dependency
async def get_employee_service(db: Session = Depends(get_db)):
    """
    Employee Service dependency factory.

    Provides database session for employee-related operations.
    Lehet később egy dedikált EmployeeService class, most egyszerűen
    a database session-t adja vissza.

    Args:
        db: Database session (dependency injection)

    Returns:
        Session: Database session for employee operations

    Example:
        @app.get("/employees/{employee_id}")
        async def get_employee(
            employee_id: int,
            db: Session = Depends(get_employee_service)
        ):
            employee = db.query(Employee).filter(Employee.id == employee_id).first()
            return employee
    """
    return db


# Role Service Dependency
async def get_role_service(db: Session = Depends(get_db)):
    """
    Role Service dependency factory.

    Provides database session for role-related operations.

    Args:
        db: Database session (dependency injection)

    Returns:
        Session: Database session for role operations

    Example:
        @app.get("/roles/{role_id}")
        async def get_role(
            role_id: int,
            db: Session = Depends(get_role_service)
        ):
            role = db.query(Role).filter(Role.id == role_id).first()
            return role
    """
    return db


# Permission Service Dependency
async def get_permission_service(db: Session = Depends(get_db)):
    """
    Permission Service dependency factory.

    Provides database session for permission-related operations.

    Args:
        db: Database session (dependency injection)

    Returns:
        Session: Database session for permission operations

    Example:
        @app.get("/permissions/{permission_id}")
        async def get_permission(
            permission_id: int,
            db: Session = Depends(get_permission_service)
        ):
            permission = db.query(Permission).filter(Permission.id == permission_id).first()
            return permission
    """
    return db


# Auth Service Dependency
async def get_auth_service(db: Session = Depends(get_db)):
    """
    Authentication Service dependency factory.

    Provides database session for authentication-related operations
    (login, token generation, password management).

    Args:
        db: Database session (dependency injection)

    Returns:
        Session: Database session for auth operations

    Example:
        @app.post("/auth/login")
        async def login(
            credentials: LoginRequest,
            db: Session = Depends(get_auth_service)
        ):
            employee = db.query(Employee).filter(
                Employee.username == credentials.username
            ).first()
            ...
    """
    return db


# ============================================================================
# Helper Functions
# ============================================================================

def authenticate_employee(db: Session, username: str, password: str) -> Optional[Employee]:
    """
    Felhasználó autentikálása username és password alapján.

    Args:
        db: Database session
        username: Felhasználónév
        password: Nyílt szövegű jelszó (PIN kód)

    Returns:
        Employee or None: Employee objektum ha sikeres, None ha sikertelen

    Example:
        employee = authenticate_employee(db, "jkovacs", "1234")
        if employee:
            token = create_access_token({"employee_id": employee.id})
    """
    # Employee lekérése username alapján
    employee = db.query(Employee).filter(Employee.username == username).first()

    if not employee:
        return None

    # Jelszó ellenőrzése (pin_code_hash mező)
    if not verify_password(password, employee.pin_code_hash):
        return None

    # Inaktív felhasználó ellenőrzése
    if not employee.is_active:
        return None

    return employee


def get_employee_permissions(employee: Employee) -> list[str]:
    """
    Employee összes jogosultságának listázása.

    Args:
        employee: Employee objektum

    Returns:
        list[str]: Jogosultság nevek listája

    Example:
        permissions = get_employee_permissions(current_user)
        # ["orders:view", "orders:create", "inventory:view"]
    """
    permission_names = [perm.name for perm in employee.permissions]
    return permission_names
