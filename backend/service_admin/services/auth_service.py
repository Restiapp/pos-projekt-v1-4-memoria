"""
AuthService - Hitelesítési és Jogosultság-kezelő Szolgáltatás
Module 6: RBAC (Role-Based Access Control) - Authentication & Authorization

Ez a modul kezeli:
- Alkalmazotti bejelentkezés PIN kóddal (bcrypt hash ellenőrzés)
- JWT token generálás és validáció (PyJWT)
- Jogosultság-ellenőrzés (Permission checking)
- RBAC (Role-Based Access Control) integráció
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# CRITICAL FIX (C4.2): Use passlib instead of bcrypt for consistency with dependencies.py
from passlib.context import CryptContext
import jwt
from sqlalchemy.orm import Session

from backend.service_admin.models.employee import Employee
from backend.service_admin.models.permission import Permission
from backend.service_admin.config import settings


class AuthService:
    """
    AuthService osztály - Hitelesítés és Jogosultság-kezelés.

    Felelősségek:
    - PIN kód alapú bejelentkezés (bcrypt hash ellenőrzés)
    - JWT token létrehozás és validáció
    - Alkalmazotti jogosultságok ellenőrzése
    - Token payload kezelés

    Használat:
        auth_service = AuthService(db_session)
        employee = auth_service.authenticate_employee("jkovacs", "1234")
        if employee:
            token = auth_service.create_access_token(employee.id)
            # Token használat API hívásoknál
    """

    def __init__(self, db: Session):
        """
        Initialize AuthService with database session and password context.
        """
        self.db = db
        # CRITICAL FIX (C4.2): Use passlib CryptContext for password hashing
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        # HOTFIX (H2.1): Initialize JWT settings from config
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.jwt_access_token_expire_minutes

    def _original_init_docstring(self):
        """
        AuthService inicializálás.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.jwt_access_token_expire_minutes

    def authenticate_employee(
        self,
        username: str,
        pin_code: str
    ) -> Optional[Employee]:
        """
        Alkalmazott hitelesítése felhasználónév és PIN kód alapján.

        1. Megkeresi az alkalmazottat felhasználónév alapján
        2. Ellenőrzi, hogy aktív-e az alkalmazott
        3. Bcrypt-tel validálja a PIN kódot

        Args:
            username: Alkalmazott felhasználóneve
            pin_code: Alkalmazott PIN kódja (plain text, 4-6 digit)

        Returns:
            Employee objektum ha sikeres, None ha sikertelen

        Example:
            employee = auth_service.authenticate_employee("jkovacs", "1234")
            if employee:
                print(f"Sikeres bejelentkezés: {employee.name}")
            else:
                print("Hibás felhasználónév vagy PIN kód")
        """
        # 1. Alkalmazott keresése felhasználónév alapján
        employee = self.db.query(Employee).filter(
            Employee.username == username
        ).first()

        if not employee:
            # Nem található alkalmazott
            return None

        # 2. Aktív státusz ellenőrzés
        if not employee.is_active:
            # Inaktív alkalmazott nem jelentkezhet be
            return None

        # 3. PIN kód validáció passlib-bel
        # A pin_code_hash mező bcrypt hash formátumban van tárolva
        # CRITICAL FIX (C4.2): Use passlib.verify() instead of bcrypt.checkpw()
        try:
            # Passlib ellenőrzés
            if self.pwd_context.verify(pin_code, employee.pin_code_hash):
                # Sikeres hitelesítés
                return employee
            else:
                # Hibás PIN kód
                return None

        except Exception as e:
            # Hiba a PIN validáció során (pl. invalid hash formátum)
            print(f"PIN validációs hiba: {e}")
            return None

    def create_access_token(
        self,
        employee_id: int,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        JWT access token generálás PyJWT-vel.

        Token payload tartalmaz:
        - sub (subject): employee_id
        - iat (issued at): token kiállítás időpontja
        - exp (expiration): lejárati idő
        - További custom claim-ek (opcionális)

        Args:
            employee_id: Alkalmazott ID (subject)
            additional_claims: További custom claim-ek dictionary-ként

        Returns:
            JWT token string (base64 encoded)

        Example:
            token = auth_service.create_access_token(
                employee_id=42,
                additional_claims={"role": "Admin", "permissions": ["orders:create"]}
            )
        """
        # Jelenlegi időpont
        now = datetime.utcnow()

        # Lejárati idő számítás
        expire = now + timedelta(minutes=self.access_token_expire_minutes)

        # Token payload összeállítás
        payload = {
            "sub": str(employee_id),  # Subject: employee ID
            "iat": now,  # Issued At: token kiállítás időpontja
            "exp": expire,  # Expiration: lejárati idő
        }

        # További claim-ek hozzáadása (ha vannak)
        if additional_claims:
            payload.update(additional_claims)

        # JWT token kódolás PyJWT-vel
        token = jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm
        )

        return token

    def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        JWT token validáció és dekódolás.

        Ellenőrzi:
        - Token formátum helyességét
        - Aláírás validitását (secret key)
        - Lejárati időt (exp claim)

        Args:
            token: JWT token string

        Returns:
            Token payload dictionary ha valid, None ha invalid

        Example:
            payload = auth_service.verify_access_token(token)
            if payload:
                employee_id = int(payload["sub"])
                print(f"Valid token, employee ID: {employee_id}")
            else:
                print("Invalid vagy lejárt token")
        """
        try:
            # JWT token dekódolás és validáció
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )

            # Token valid, visszaadjuk a payload-ot
            return payload

        except jwt.ExpiredSignatureError:
            # Token lejárt
            print("Token lejárt (expired)")
            return None

        except jwt.InvalidTokenError as e:
            # Invalid token (hibás formátum, aláírás, stb.)
            print(f"Invalid token: {e}")
            return None

    def get_employee_from_token(self, token: str) -> Optional[Employee]:
        """
        Alkalmazott lekérdezés JWT token alapján.

        1. Token validáció
        2. Employee ID kinyerés a payload-ból
        3. Employee lekérdezés adatbázisból

        Args:
            token: JWT access token

        Returns:
            Employee objektum ha valid token és létezik az employee, None egyébként

        Example:
            employee = auth_service.get_employee_from_token(token)
            if employee:
                print(f"Bejelentkezett felhasználó: {employee.name}")
        """
        # Token validáció
        payload = self.verify_access_token(token)

        if not payload:
            return None

        # Employee ID kinyerés
        try:
            employee_id = int(payload.get("sub"))
        except (ValueError, TypeError):
            return None

        # Employee lekérdezés adatbázisból
        employee = self.db.query(Employee).filter(
            Employee.id == employee_id,
            Employee.is_active == True
        ).first()

        return employee

    def check_permission(
        self,
        employee: Employee,
        permission_name: str
    ) -> bool:
        """
        Jogosultság ellenőrzés az alkalmazott szerepkörei alapján.

        Az Employee modell has_permission() metódusát használja,
        amely végigmegy az összes szerepkörön és azok jogosultságain.

        Args:
            employee: Employee objektum
            permission_name: Jogosultság neve (pl. "orders:create", "admin:all")

        Returns:
            True ha van jogosultsága, False ha nincs

        Example:
            if auth_service.check_permission(employee, "orders:create"):
                print("Jogosult rendelés létrehozására")
            else:
                print("Nincs jogosultsága")
        """
        # Employee modell has_permission() metódusát használjuk
        return employee.has_permission(permission_name)

    def check_permission_by_id(
        self,
        employee_id: int,
        permission_name: str
    ) -> bool:
        """
        Jogosultság ellenőrzés employee ID alapján.

        Kényelmi metódus, amikor csak az employee ID áll rendelkezésre.

        Args:
            employee_id: Alkalmazott ID
            permission_name: Jogosultság neve

        Returns:
            True ha van jogosultsága, False ha nincs vagy nem létezik az employee

        Example:
            if auth_service.check_permission_by_id(42, "reports:view"):
                print("Jogosult riportok megtekintésére")
        """
        # Employee lekérdezés
        employee = self.db.query(Employee).filter(
            Employee.id == employee_id,
            Employee.is_active == True
        ).first()

        if not employee:
            return False

        return self.check_permission(employee, permission_name)

    def hash_pin_code(self, pin_code: str) -> str:
        """
        PIN kód hash-elés bcrypt-tel.

        Segéd metódus új alkalmazott létrehozásához vagy PIN kód módosításához.

        Args:
            pin_code: PIN kód plain text formában (4-6 digit)

        Returns:
            Bcrypt hash string

        Example:
            pin_hash = auth_service.hash_pin_code("1234")
            # Tárolás adatbázisban: employee.pin_code_hash = pin_hash
        """
        # CRITICAL FIX (C4.2): Use passlib.hash() instead of bcrypt.hashpw()
        # Passlib automatically handles salt generation and encoding
        return self.pwd_context.hash(pin_code)

    def get_employee_permissions(self, employee: Employee) -> list[str]:
        """
        Alkalmazott összes jogosultságának listázása.

        Args:
            employee: Employee objektum

        Returns:
            Jogosultság nevek listája

        Example:
            permissions = auth_service.get_employee_permissions(employee)
            # ["orders:create", "orders:view", "reports:view"]
        """
        # Employee.permissions property-t használjuk (set of Permission objects)
        return [perm.name for perm in employee.permissions]

    def create_token_with_permissions(self, employee: Employee) -> str:
        """
        JWT token generálás az alkalmazott jogosultságaival.

        Token payload-ban szerepelnek:
        - Employee ID (sub)
        - Username (username)
        - Roles (roles)
        - Permissions (permissions)

        Args:
            employee: Employee objektum

        Returns:
            JWT token string

        Example:
            token = auth_service.create_token_with_permissions(employee)
            # Token tartalmaz: employee_id, username, roles, permissions
        """
        # Jogosultságok összegyűjtése
        permissions = self.get_employee_permissions(employee)

        # Szerepkörök összegyűjtése
        roles = [role.name for role in employee.roles]

        # Additional claims összeállítás
        additional_claims = {
            "username": employee.username,
            "roles": roles,
            "permissions": permissions,
        }

        # Token generálás
        return self.create_access_token(
            employee_id=employee.id,
            additional_claims=additional_claims
        )


# Singleton instance létrehozása (opcionális)
# Használat dependency injection-nel FastAPI-ban
def get_auth_service(db: Session) -> AuthService:
    """
    AuthService factory függvény FastAPI dependency injection-höz.

    Args:
        db: Database session (Depends(get_db) FastAPI-ban)

    Returns:
        AuthService instance

    Example (FastAPI route):
        @app.post("/login")
        async def login(
            credentials: LoginRequest,
            auth_service: AuthService = Depends(get_auth_service),
            db: Session = Depends(get_db)
        ):
            employee = auth_service.authenticate_employee(
                credentials.username,
                credentials.password
            )
            if not employee:
                raise HTTPException(status_code=401, detail="Invalid credentials")

            token = auth_service.create_token_with_permissions(employee)
            return {"access_token": token, "token_type": "bearer"}
    """
    return AuthService(db)
