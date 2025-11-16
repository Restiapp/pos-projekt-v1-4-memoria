"""
EmployeeService - Munkatárs (Employee) kezelés
Module 6: RBAC (Role-Based Access Control) - Employee Management

Ez a service felelős a munkatársak (employees) CRUD műveleteiért,
valamint a szerepkör (role) és jogosultság (permission) kezelésért.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from passlib.context import CryptContext

from backend.service_admin.models.employee import Employee
from backend.service_admin.models.role import Role
from backend.service_admin.models.permission import Permission


# Password/PIN hashing context
# TODO: Később kiszervezhető az AuthService-be
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class EmployeeService:
    """
    Service osztály a munkatársak (employees) kezeléséhez.

    Felelősségek:
    - Munkatárs létrehozása, módosítása, törlése (CRUD)
    - PIN kód hashelés és validáció
    - Szerepkör (role) hozzárendelés
    - Jogosultság (permission) lekérdezés
    - Munkatársak listázása szűrési és lapozási lehetőségekkel
    """

    def __init__(self, db: Session):
        """
        Inicializálja az EmployeeService-t.

        Args:
            db: SQLAlchemy Session objektum dependency injectionből
        """
        self.db = db

    def _hash_pin(self, pin_code: str) -> str:
        """
        PIN kód hashelése bcrypt algoritmussal.

        Args:
            pin_code: Nyers PIN kód (pl. "1234")

        Returns:
            str: Hashelt PIN kód

        Note:
            TODO: Később kiszervezhető az AuthService.hash_pin() metódusba
        """
        return pwd_context.hash(pin_code)

    def _verify_pin(self, plain_pin: str, hashed_pin: str) -> bool:
        """
        PIN kód validálása hash-elt verzióval szemben.

        Args:
            plain_pin: Nyers PIN kód
            hashed_pin: Hash-elt PIN kód

        Returns:
            bool: True ha egyezik, False ha nem

        Note:
            TODO: Később kiszervezhető az AuthService.verify_pin() metódusba
        """
        return pwd_context.verify(plain_pin, hashed_pin)

    # ========================================================================
    # CRUD Operations
    # ========================================================================

    def create_employee(
        self,
        username: str,
        name: str,
        pin_code: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        is_active: bool = True
    ) -> Employee:
        """
        Létrehoz egy új munkatársat.

        Args:
            username: Egyedi felhasználónév (bejelentkezéshez)
            name: Teljes név
            pin_code: Nyers PIN kód (pl. "1234") - hash-elve lesz tárolva
            email: Email cím (opcionális)
            phone: Telefonszám (opcionális)
            is_active: Aktív státusz (alapértelmezett: True)

        Returns:
            Employee: A létrehozott munkatárs objektum

        Raises:
            ValueError: Ha a felhasználónév már létezik

        Example:
            >>> service.create_employee(
            ...     username='jkovacs',
            ...     name='Kovács János',
            ...     pin_code='1234',
            ...     email='janos.kovacs@example.com'
            ... )
        """
        # Ellenőrizzük, hogy létezik-e már ilyen username
        existing = self.db.query(Employee).filter(
            Employee.username == username
        ).first()

        if existing:
            raise ValueError(f"Username '{username}' already exists")

        # PIN kód hashelése
        pin_code_hash = self._hash_pin(pin_code)

        # Új Employee objektum létrehozása
        employee = Employee(
            username=username,
            name=name,
            pin_code_hash=pin_code_hash,
            email=email,
            phone=phone,
            is_active=is_active
        )

        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)

        return employee

    def get_employee_by_id(self, employee_id: int) -> Optional[Employee]:
        """
        Lekér egy munkatársat ID alapján.

        Args:
            employee_id: Munkatárs egyedi azonosítója

        Returns:
            Optional[Employee]: Munkatárs objektum vagy None ha nem található
        """
        return self.db.query(Employee).filter(
            Employee.id == employee_id
        ).first()

    def get_employee_by_username(self, username: str) -> Optional[Employee]:
        """
        Lekér egy munkatársat felhasználónév alapján.

        Args:
            username: Felhasználónév

        Returns:
            Optional[Employee]: Munkatárs objektum vagy None ha nem található

        Note:
            Hasznos az autentikációnál (PIN-kód alapú bejelentkezés)
        """
        return self.db.query(Employee).filter(
            Employee.username == username
        ).first()

    def update_employee(
        self,
        employee_id: int,
        name: Optional[str] = None,
        username: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        pin_code: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Optional[Employee]:
        """
        Frissít egy meglévő munkatársat.

        Args:
            employee_id: Munkatárs egyedi azonosítója
            name: Új név (opcionális)
            username: Új felhasználónév (opcionális)
            email: Új email (opcionális)
            phone: Új telefonszám (opcionális)
            pin_code: Új PIN kód (opcionális, hash-elve lesz tárolva)
            is_active: Új aktív státusz (opcionális)

        Returns:
            Optional[Employee]: Frissített munkatárs objektum vagy None ha nem található

        Raises:
            ValueError: Ha az új username már létezik (másik munkatársnál)

        Example:
            >>> service.update_employee(
            ...     employee_id=1,
            ...     email='uj.email@example.com',
            ...     is_active=False
            ... )
        """
        employee = self.get_employee_by_id(employee_id)

        if not employee:
            return None

        # Username ellenőrzés (ha változik)
        if username and username != employee.username:
            existing = self.db.query(Employee).filter(
                Employee.username == username,
                Employee.id != employee_id
            ).first()

            if existing:
                raise ValueError(f"Username '{username}' already exists")

            employee.username = username

        # Mezők frissítése (csak ha meg vannak adva)
        if name is not None:
            employee.name = name
        if email is not None:
            employee.email = email
        if phone is not None:
            employee.phone = phone
        if is_active is not None:
            employee.is_active = is_active
        if pin_code is not None:
            employee.pin_code_hash = self._hash_pin(pin_code)

        self.db.commit()
        self.db.refresh(employee)

        return employee

    def delete_employee(self, employee_id: int) -> bool:
        """
        Töröl egy munkatársat.

        Args:
            employee_id: Munkatárs egyedi azonosítója

        Returns:
            bool: True ha sikeres a törlés, False ha nem található

        Note:
            Ez hard delete (fizikai törlés). Soft delete esetén használd
            az update_employee(employee_id, is_active=False) metódust.
        """
        employee = self.get_employee_by_id(employee_id)

        if not employee:
            return False

        self.db.delete(employee)
        self.db.commit()

        return True

    def list_employees(
        self,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Employee]:
        """
        Lekéri a munkatársak listáját szűrési és lapozási lehetőségekkel.

        Args:
            is_active: Szűrés aktív státuszra (None = mind)
            search: Keresési kifejezés (név vagy username részlet)
            limit: Max visszaadott rekordok száma (default: 100)
            offset: Lapozás offset (default: 0)

        Returns:
            List[Employee]: Munkatársak listája

        Example:
            >>> # Aktív munkatársak keresése 'kovács' névvel
            >>> service.list_employees(is_active=True, search='kovács')
        """
        query = self.db.query(Employee)

        # Szűrés aktív státuszra
        if is_active is not None:
            query = query.filter(Employee.is_active == is_active)

        # Keresés név vagy username alapján
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Employee.name.ilike(search_pattern),
                    Employee.username.ilike(search_pattern)
                )
            )

        # Rendezés név szerint növekvő sorrendben
        query = query.order_by(Employee.name)

        # Lapozás
        query = query.limit(limit).offset(offset)

        return query.all()

    def count_employees(
        self,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> int:
        """
        Megszámolja a munkatársakat szűrési feltételekkel.

        Args:
            is_active: Szűrés aktív státuszra (None = mind)
            search: Keresési kifejezés (név vagy username részlet)

        Returns:
            int: Munkatársak száma
        """
        query = self.db.query(Employee)

        if is_active is not None:
            query = query.filter(Employee.is_active == is_active)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Employee.name.ilike(search_pattern),
                    Employee.username.ilike(search_pattern)
                )
            )

        return query.count()

    # ========================================================================
    # RBAC Operations
    # ========================================================================

    def get_employee_permissions(self, employee_id: int) -> set[Permission]:
        """
        Lekéri egy munkatárs összes jogosultságát (permissions).

        A jogosultságokat a munkatárs szerepköreiből (roles) gyűjti össze.

        Args:
            employee_id: Munkatárs egyedi azonosítója

        Returns:
            set[Permission]: Egyedi jogosultságok halmaza

        Example:
            >>> permissions = service.get_employee_permissions(1)
            >>> for perm in permissions:
            ...     print(perm.name)  # pl. 'orders:create', 'reports:view'
        """
        employee = self.get_employee_by_id(employee_id)

        if not employee:
            return set()

        # Employee.permissions property használata (model-ben definiálva)
        return employee.permissions

    def has_permission(
        self,
        employee_id: int,
        permission_name: str
    ) -> bool:
        """
        Ellenőrzi, hogy egy munkatársnak van-e adott jogosultsága.

        Args:
            employee_id: Munkatárs egyedi azonosítója
            permission_name: Jogosultság neve (pl. 'orders:create')

        Returns:
            bool: True ha van jogosultsága, False ha nincs

        Example:
            >>> if service.has_permission(1, 'orders:create'):
            ...     print("Jogosult rendelés létrehozására")
        """
        employee = self.get_employee_by_id(employee_id)

        if not employee:
            return False

        # Employee.has_permission() metódus használata
        return employee.has_permission(permission_name)

    def assign_roles(
        self,
        employee_id: int,
        role_ids: List[int]
    ) -> Optional[Employee]:
        """
        Szerepkörök (roles) hozzárendelése egy munkatárshoz.

        Ez a metódus felülírja a munkatárs meglévő szerepköreit.

        Args:
            employee_id: Munkatárs egyedi azonosítója
            role_ids: Szerepkör ID-k listája

        Returns:
            Optional[Employee]: Frissített munkatárs objektum vagy None ha nem található

        Raises:
            ValueError: Ha valamelyik role_id nem létezik

        Example:
            >>> # Admin és Manager szerepkörök hozzárendelése
            >>> service.assign_roles(employee_id=1, role_ids=[1, 2])
        """
        employee = self.get_employee_by_id(employee_id)

        if not employee:
            return None

        # Szerepkörök lekérdezése
        roles = self.db.query(Role).filter(Role.id.in_(role_ids)).all()

        # Ellenőrizzük, hogy minden szerepkör létezik-e
        if len(roles) != len(role_ids):
            found_ids = {role.id for role in roles}
            missing_ids = set(role_ids) - found_ids
            raise ValueError(f"Role IDs not found: {missing_ids}")

        # Szerepkörök hozzárendelése (felülírja a meglévőket)
        employee.roles = roles

        self.db.commit()
        self.db.refresh(employee)

        return employee

    def add_roles(
        self,
        employee_id: int,
        role_ids: List[int]
    ) -> Optional[Employee]:
        """
        Szerepkörök (roles) hozzáadása egy munkatárshoz.

        Ez a metódus megtartja a meglévő szerepköröket és újakat ad hozzá.

        Args:
            employee_id: Munkatárs egyedi azonosítója
            role_ids: Hozzáadandó szerepkör ID-k listája

        Returns:
            Optional[Employee]: Frissített munkatárs objektum vagy None ha nem található

        Raises:
            ValueError: Ha valamelyik role_id nem létezik
        """
        employee = self.get_employee_by_id(employee_id)

        if not employee:
            return None

        # Szerepkörök lekérdezése
        roles = self.db.query(Role).filter(Role.id.in_(role_ids)).all()

        # Ellenőrizzük, hogy minden szerepkör létezik-e
        if len(roles) != len(role_ids):
            found_ids = {role.id for role in roles}
            missing_ids = set(role_ids) - found_ids
            raise ValueError(f"Role IDs not found: {missing_ids}")

        # Szerepkörök hozzáadása (csak az újak)
        existing_role_ids = {role.id for role in employee.roles}
        for role in roles:
            if role.id not in existing_role_ids:
                employee.roles.append(role)

        self.db.commit()
        self.db.refresh(employee)

        return employee

    def remove_roles(
        self,
        employee_id: int,
        role_ids: List[int]
    ) -> Optional[Employee]:
        """
        Szerepkörök (roles) eltávolítása egy munkatárstól.

        Args:
            employee_id: Munkatárs egyedi azonosítója
            role_ids: Eltávolítandó szerepkör ID-k listája

        Returns:
            Optional[Employee]: Frissített munkatárs objektum vagy None ha nem található
        """
        employee = self.get_employee_by_id(employee_id)

        if not employee:
            return None

        # Szerepkörök eltávolítása
        employee.roles = [
            role for role in employee.roles
            if role.id not in role_ids
        ]

        self.db.commit()
        self.db.refresh(employee)

        return employee

    def get_employee_roles(self, employee_id: int) -> List[Role]:
        """
        Lekéri egy munkatárs összes szerepkörét (roles).

        Args:
            employee_id: Munkatárs egyedi azonosítója

        Returns:
            List[Role]: Szerepkörök listája
        """
        employee = self.get_employee_by_id(employee_id)

        if not employee:
            return []

        return employee.roles

    # ========================================================================
    # Authentication Helper
    # ========================================================================

    def authenticate(self, username: str, pin_code: str) -> Optional[Employee]:
        """
        Autentikálja a munkatársat felhasználónév és PIN kód alapján.

        Args:
            username: Felhasználónév
            pin_code: Nyers PIN kód

        Returns:
            Optional[Employee]: Munkatárs objektum ha sikeres, None ha sikertelen

        Note:
            TODO: Később kiszervezhető az AuthService-be

        Example:
            >>> employee = service.authenticate('jkovacs', '1234')
            >>> if employee:
            ...     print(f"Sikeres bejelentkezés: {employee.name}")
        """
        employee = self.get_employee_by_username(username)

        if not employee:
            return None

        # Inaktív munkatársak nem jelentkezhetnek be
        if not employee.is_active:
            return None

        # PIN kód ellenőrzése
        if not self._verify_pin(pin_code, employee.pin_code_hash):
            return None

        return employee
