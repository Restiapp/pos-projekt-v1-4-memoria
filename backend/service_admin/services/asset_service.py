"""
AssetService - Tárgyi Eszközök (Assets) kezelés
Module 8: Admin - Asset Management (V3.0 Phase 3.2)

Ez a service felelős az eszközök és szervizek kezeléséért:
- Eszközcsoportok (AssetGroup) CRUD műveletek
- Eszközök (Asset) CRUD műveletek
- Eszköz szervizek (AssetService) kezelése
- Szerviz előzmények nyomon követése
"""

from typing import Optional, List
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func

from backend.service_admin.models.assets import (
    AssetGroup,
    Asset,
    AssetService,
    AssetStatus,
    ServiceType
)


class AssetManagementService:
    """
    Service osztály a tárgyi eszközök kezeléséhez.

    Felelősségek:
    - Eszközcsoportok kezelése
    - Eszközök kezelése (CRUD)
    - Szerviz bejegyzések kezelése
    - Eszköz előzmények lekérdezése
    """

    def __init__(self, db: Session):
        """
        Inicializálja az AssetManagementService-t.

        Args:
            db: SQLAlchemy Session objektum dependency injectionből
        """
        self.db = db

    # ========================================================================
    # Asset Group Operations (Eszközcsoportok)
    # ========================================================================

    def create_asset_group(
        self,
        name: str,
        description: Optional[str] = None,
        depreciation_rate: Optional[Decimal] = None,
        expected_lifetime_years: Optional[int] = None,
        is_active: bool = True
    ) -> AssetGroup:
        """
        Új eszközcsoport létrehozása.

        Args:
            name: Eszközcsoport neve
            description: Leírás
            depreciation_rate: Amortizációs ráta (százalék/év)
            expected_lifetime_years: Várható élettartam (év)
            is_active: Aktív státusz

        Returns:
            AssetGroup: Létrehozott eszközcsoport rekord

        Raises:
            ValueError: Ha a név már létezik
        """
        # Ellenőrizzük hogy a név egyedi-e
        existing = self.db.query(AssetGroup).filter(
            AssetGroup.name == name
        ).first()

        if existing:
            raise ValueError(f"Az eszközcsoport név már létezik: {name}")

        asset_group = AssetGroup(
            name=name,
            description=description,
            depreciation_rate=depreciation_rate,
            expected_lifetime_years=expected_lifetime_years,
            is_active=is_active
        )

        self.db.add(asset_group)
        self.db.commit()
        self.db.refresh(asset_group)

        return asset_group

    def get_asset_group_by_id(self, group_id: int) -> Optional[AssetGroup]:
        """
        Eszközcsoport lekérdezése azonosító alapján.

        Args:
            group_id: Eszközcsoport azonosító

        Returns:
            Optional[AssetGroup]: Eszközcsoport vagy None
        """
        return self.db.query(AssetGroup).filter(
            AssetGroup.id == group_id
        ).first()

    def get_asset_groups(
        self,
        is_active: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AssetGroup]:
        """
        Eszközcsoportok listázása.

        Args:
            is_active: Aktív státusz szűrő (opcionális)
            limit: Maximum eredmények száma
            offset: Lapozási eltolás

        Returns:
            List[AssetGroup]: Eszközcsoportok listája
        """
        query = self.db.query(AssetGroup)

        if is_active is not None:
            query = query.filter(AssetGroup.is_active == is_active)

        query = query.order_by(AssetGroup.name)
        query = query.limit(limit).offset(offset)

        return query.all()

    def update_asset_group(
        self,
        group_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        depreciation_rate: Optional[Decimal] = None,
        expected_lifetime_years: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> AssetGroup:
        """
        Eszközcsoport frissítése.

        Args:
            group_id: Eszközcsoport azonosító
            name: Új név (opcionális)
            description: Új leírás (opcionális)
            depreciation_rate: Új amortizációs ráta (opcionális)
            expected_lifetime_years: Új várható élettartam (opcionális)
            is_active: Új aktív státusz (opcionális)

        Returns:
            AssetGroup: Frissített eszközcsoport rekord

        Raises:
            ValueError: Ha az eszközcsoport nem található
        """
        asset_group = self.get_asset_group_by_id(group_id)

        if not asset_group:
            raise ValueError(f"Eszközcsoport nem található: {group_id}")

        # Név egyediség ellenőrzése ha módosítva van
        if name and name != asset_group.name:
            existing = self.db.query(AssetGroup).filter(
                and_(
                    AssetGroup.name == name,
                    AssetGroup.id != group_id
                )
            ).first()

            if existing:
                raise ValueError(f"Az eszközcsoport név már létezik: {name}")

            asset_group.name = name

        if description is not None:
            asset_group.description = description

        if depreciation_rate is not None:
            asset_group.depreciation_rate = depreciation_rate

        if expected_lifetime_years is not None:
            asset_group.expected_lifetime_years = expected_lifetime_years

        if is_active is not None:
            asset_group.is_active = is_active

        self.db.commit()
        self.db.refresh(asset_group)

        return asset_group

    def delete_asset_group(self, group_id: int) -> bool:
        """
        Eszközcsoport törlése (soft delete).

        Args:
            group_id: Eszközcsoport azonosító

        Returns:
            bool: True ha sikeres volt a törlés

        Raises:
            ValueError: Ha az eszközcsoport nem található vagy még vannak hozzárendelt eszközök
        """
        asset_group = self.get_asset_group_by_id(group_id)

        if not asset_group:
            raise ValueError(f"Eszközcsoport nem található: {group_id}")

        # Ellenőrizzük hogy vannak-e hozzárendelt aktív eszközök
        active_assets_count = self.db.query(Asset).filter(
            and_(
                Asset.asset_group_id == group_id,
                Asset.is_active == True
            )
        ).count()

        if active_assets_count > 0:
            raise ValueError(
                f"Az eszközcsoport nem törölhető, mert {active_assets_count} aktív eszköz tartozik hozzá"
            )

        asset_group.is_active = False
        self.db.commit()

        return True

    # ========================================================================
    # Asset Operations (Eszközök)
    # ========================================================================

    def create_asset(
        self,
        asset_group_id: int,
        name: str,
        inventory_number: Optional[str] = None,
        manufacturer: Optional[str] = None,
        model: Optional[str] = None,
        serial_number: Optional[str] = None,
        purchase_date: Optional[date] = None,
        purchase_price: Optional[Decimal] = None,
        current_value: Optional[Decimal] = None,
        location: Optional[str] = None,
        responsible_employee_id: Optional[int] = None,
        status: str = "ACTIVE",
        notes: Optional[str] = None,
        is_active: bool = True
    ) -> Asset:
        """
        Új eszköz létrehozása.

        Args:
            asset_group_id: Eszközcsoport azonosító
            name: Eszköz neve
            inventory_number: Leltári szám (opcionális, de egyedinek kell lennie)
            manufacturer: Gyártó
            model: Modell
            serial_number: Sorozatszám
            purchase_date: Beszerzési dátum
            purchase_price: Beszerzési ár
            current_value: Jelenlegi érték
            location: Helyszín
            responsible_employee_id: Felelős munkatárs
            status: Státusz (default: ACTIVE)
            notes: Megjegyzések
            is_active: Aktív státusz

        Returns:
            Asset: Létrehozott eszköz rekord

        Raises:
            ValueError: Ha az eszközcsoport nem található vagy a leltári szám már létezik
        """
        # Ellenőrizzük hogy az eszközcsoport létezik-e
        asset_group = self.get_asset_group_by_id(asset_group_id)
        if not asset_group:
            raise ValueError(f"Eszközcsoport nem található: {asset_group_id}")

        # Leltári szám egyediség ellenőrzése ha meg van adva
        if inventory_number:
            existing = self.db.query(Asset).filter(
                Asset.inventory_number == inventory_number
            ).first()

            if existing:
                raise ValueError(f"A leltári szám már létezik: {inventory_number}")

        # Validáljuk a státuszt
        try:
            asset_status = AssetStatus(status)
        except ValueError:
            raise ValueError(f"Érvénytelen eszköz státusz: {status}")

        asset = Asset(
            asset_group_id=asset_group_id,
            name=name,
            inventory_number=inventory_number,
            manufacturer=manufacturer,
            model=model,
            serial_number=serial_number,
            purchase_date=purchase_date,
            purchase_price=purchase_price,
            current_value=current_value,
            location=location,
            responsible_employee_id=responsible_employee_id,
            status=asset_status,
            notes=notes,
            is_active=is_active
        )

        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)

        return asset

    def get_asset_by_id(self, asset_id: int) -> Optional[Asset]:
        """
        Eszköz lekérdezése azonosító alapján.

        Args:
            asset_id: Eszköz azonosító

        Returns:
            Optional[Asset]: Eszköz vagy None
        """
        return self.db.query(Asset).filter(
            Asset.id == asset_id
        ).first()

    def get_assets(
        self,
        asset_group_id: Optional[int] = None,
        status: Optional[str] = None,
        responsible_employee_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Asset]:
        """
        Eszközök listázása szűrési feltételekkel.

        Args:
            asset_group_id: Eszközcsoport szűrő (opcionális)
            status: Státusz szűrő (opcionális)
            responsible_employee_id: Felelős munkatárs szűrő (opcionális)
            is_active: Aktív státusz szűrő (opcionális)
            limit: Maximum eredmények száma
            offset: Lapozási eltolás

        Returns:
            List[Asset]: Eszközök listája
        """
        query = self.db.query(Asset)

        if asset_group_id is not None:
            query = query.filter(Asset.asset_group_id == asset_group_id)

        if status:
            query = query.filter(Asset.status == status)

        if responsible_employee_id is not None:
            query = query.filter(Asset.responsible_employee_id == responsible_employee_id)

        if is_active is not None:
            query = query.filter(Asset.is_active == is_active)

        query = query.order_by(desc(Asset.created_at))
        query = query.limit(limit).offset(offset)

        return query.all()

    def update_asset(
        self,
        asset_id: int,
        asset_group_id: Optional[int] = None,
        name: Optional[str] = None,
        inventory_number: Optional[str] = None,
        manufacturer: Optional[str] = None,
        model: Optional[str] = None,
        serial_number: Optional[str] = None,
        purchase_date: Optional[date] = None,
        purchase_price: Optional[Decimal] = None,
        current_value: Optional[Decimal] = None,
        location: Optional[str] = None,
        responsible_employee_id: Optional[int] = None,
        status: Optional[str] = None,
        notes: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Asset:
        """
        Eszköz frissítése.

        Args:
            asset_id: Eszköz azonosító
            (+ egyéb opcionális mezők)

        Returns:
            Asset: Frissített eszköz rekord

        Raises:
            ValueError: Ha az eszköz nem található vagy egyediségi megszorítás sérül
        """
        asset = self.get_asset_by_id(asset_id)

        if not asset:
            raise ValueError(f"Eszköz nem található: {asset_id}")

        # Leltári szám egyediség ellenőrzése ha módosítva van
        if inventory_number and inventory_number != asset.inventory_number:
            existing = self.db.query(Asset).filter(
                and_(
                    Asset.inventory_number == inventory_number,
                    Asset.id != asset_id
                )
            ).first()

            if existing:
                raise ValueError(f"A leltári szám már létezik: {inventory_number}")

            asset.inventory_number = inventory_number

        if asset_group_id is not None:
            # Ellenőrizzük hogy az eszközcsoport létezik-e
            asset_group = self.get_asset_group_by_id(asset_group_id)
            if not asset_group:
                raise ValueError(f"Eszközcsoport nem található: {asset_group_id}")
            asset.asset_group_id = asset_group_id

        if name is not None:
            asset.name = name

        if manufacturer is not None:
            asset.manufacturer = manufacturer

        if model is not None:
            asset.model = model

        if serial_number is not None:
            asset.serial_number = serial_number

        if purchase_date is not None:
            asset.purchase_date = purchase_date

        if purchase_price is not None:
            asset.purchase_price = purchase_price

        if current_value is not None:
            asset.current_value = current_value

        if location is not None:
            asset.location = location

        if responsible_employee_id is not None:
            asset.responsible_employee_id = responsible_employee_id

        if status is not None:
            try:
                asset.status = AssetStatus(status)
            except ValueError:
                raise ValueError(f"Érvénytelen eszköz státusz: {status}")

        if notes is not None:
            asset.notes = notes

        if is_active is not None:
            asset.is_active = is_active

        self.db.commit()
        self.db.refresh(asset)

        return asset

    def delete_asset(self, asset_id: int) -> bool:
        """
        Eszköz törlése (soft delete).

        Args:
            asset_id: Eszköz azonosító

        Returns:
            bool: True ha sikeres volt a törlés

        Raises:
            ValueError: Ha az eszköz nem található
        """
        asset = self.get_asset_by_id(asset_id)

        if not asset:
            raise ValueError(f"Eszköz nem található: {asset_id}")

        asset.is_active = False
        self.db.commit()

        return True

    # ========================================================================
    # Asset Service Operations (Eszköz Szervizek)
    # ========================================================================

    def create_asset_service(
        self,
        asset_id: int,
        service_type: str,
        service_date: date,
        description: str,
        cost: Optional[Decimal] = None,
        service_provider: Optional[str] = None,
        next_service_date: Optional[date] = None,
        performed_by_employee_id: Optional[int] = None,
        documents_url: Optional[str] = None
    ) -> AssetService:
        """
        Új szerviz bejegyzés létrehozása.

        Args:
            asset_id: Eszköz azonosító
            service_type: Szerviz típusa
            service_date: Szerviz dátuma
            description: Leírás/munka részletei
            cost: Költség
            service_provider: Szervizes cég/személy
            next_service_date: Következő szerviz dátuma
            performed_by_employee_id: Végző munkatárs
            documents_url: Dokumentumok URL-je

        Returns:
            AssetService: Létrehozott szerviz rekord

        Raises:
            ValueError: Ha az eszköz nem található vagy a szerviz típus érvénytelen
        """
        # Ellenőrizzük hogy az eszköz létezik-e
        asset = self.get_asset_by_id(asset_id)
        if not asset:
            raise ValueError(f"Eszköz nem található: {asset_id}")

        # Validáljuk a szerviz típust
        try:
            service_type_enum = ServiceType(service_type)
        except ValueError:
            raise ValueError(f"Érvénytelen szerviz típus: {service_type}")

        asset_service = AssetService(
            asset_id=asset_id,
            service_type=service_type_enum,
            service_date=service_date,
            description=description,
            cost=cost,
            service_provider=service_provider,
            next_service_date=next_service_date,
            performed_by_employee_id=performed_by_employee_id,
            documents_url=documents_url
        )

        self.db.add(asset_service)
        self.db.commit()
        self.db.refresh(asset_service)

        return asset_service

    def get_asset_service_by_id(self, service_id: int) -> Optional[AssetService]:
        """
        Szerviz bejegyzés lekérdezése azonosító alapján.

        Args:
            service_id: Szerviz azonosító

        Returns:
            Optional[AssetService]: Szerviz bejegyzés vagy None
        """
        return self.db.query(AssetService).filter(
            AssetService.id == service_id
        ).first()

    def get_asset_services(
        self,
        asset_id: Optional[int] = None,
        service_type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AssetService]:
        """
        Szerviz bejegyzések listázása szűrési feltételekkel.

        Args:
            asset_id: Eszköz azonosító szűrő (opcionális)
            service_type: Szerviz típus szűrő (opcionális)
            start_date: Kezdő dátum szűrő (opcionális)
            end_date: Záró dátum szűrő (opcionális)
            limit: Maximum eredmények száma
            offset: Lapozási eltolás

        Returns:
            List[AssetService]: Szerviz bejegyzések listája
        """
        query = self.db.query(AssetService)

        if asset_id is not None:
            query = query.filter(AssetService.asset_id == asset_id)

        if service_type:
            query = query.filter(AssetService.service_type == service_type)

        if start_date:
            query = query.filter(AssetService.service_date >= start_date)

        if end_date:
            query = query.filter(AssetService.service_date <= end_date)

        query = query.order_by(desc(AssetService.service_date))
        query = query.limit(limit).offset(offset)

        return query.all()

    def update_asset_service(
        self,
        service_id: int,
        service_type: Optional[str] = None,
        service_date: Optional[date] = None,
        description: Optional[str] = None,
        cost: Optional[Decimal] = None,
        service_provider: Optional[str] = None,
        next_service_date: Optional[date] = None,
        performed_by_employee_id: Optional[int] = None,
        documents_url: Optional[str] = None
    ) -> AssetService:
        """
        Szerviz bejegyzés frissítése.

        Args:
            service_id: Szerviz azonosító
            (+ egyéb opcionális mezők)

        Returns:
            AssetService: Frissített szerviz rekord

        Raises:
            ValueError: Ha a szerviz nem található vagy a típus érvénytelen
        """
        asset_service = self.get_asset_service_by_id(service_id)

        if not asset_service:
            raise ValueError(f"Szerviz bejegyzés nem található: {service_id}")

        if service_type is not None:
            try:
                asset_service.service_type = ServiceType(service_type)
            except ValueError:
                raise ValueError(f"Érvénytelen szerviz típus: {service_type}")

        if service_date is not None:
            asset_service.service_date = service_date

        if description is not None:
            asset_service.description = description

        if cost is not None:
            asset_service.cost = cost

        if service_provider is not None:
            asset_service.service_provider = service_provider

        if next_service_date is not None:
            asset_service.next_service_date = next_service_date

        if performed_by_employee_id is not None:
            asset_service.performed_by_employee_id = performed_by_employee_id

        if documents_url is not None:
            asset_service.documents_url = documents_url

        self.db.commit()
        self.db.refresh(asset_service)

        return asset_service

    def delete_asset_service(self, service_id: int) -> bool:
        """
        Szerviz bejegyzés törlése (hard delete).

        Args:
            service_id: Szerviz azonosító

        Returns:
            bool: True ha sikeres volt a törlés

        Raises:
            ValueError: Ha a szerviz nem található
        """
        asset_service = self.get_asset_service_by_id(service_id)

        if not asset_service:
            raise ValueError(f"Szerviz bejegyzés nem található: {service_id}")

        self.db.delete(asset_service)
        self.db.commit()

        return True
