"""
VehicleService - Járművek (Vehicles) kezelés
Module 8: Admin - Vehicle Management (V3.0 Phase 3.4)

Ez a service felelős a járművek és kapcsolódó bejegyzések kezeléséért:
- Járművek (Vehicle) CRUD műveletek
- Tankolások (VehicleRefueling) kezelése
- Karbantartások (VehicleMaintenance) kezelése
- Figyelmeztetések (biztosítás, műszaki lejárat)
"""

from typing import Optional, List, Dict
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func

from backend.service_admin.models.vehicles import (
    Vehicle,
    VehicleRefueling,
    VehicleMaintenance,
    VehicleStatus,
    FuelType,
    MaintenanceType
)


class VehicleManagementService:
    """
    Service osztály a járművek kezeléséhez.

    Felelősségek:
    - Járművek kezelése (CRUD)
    - Tankolások kezelése
    - Karbantartások kezelése
    - Figyelmeztetések (biztosítás, műszaki)
    """

    def __init__(self, db: Session):
        """
        Inicializálja a VehicleManagementService-t.

        Args:
            db: SQLAlchemy Session objektum dependency injectionből
        """
        self.db = db

    # ========================================================================
    # Vehicle Operations (Járművek)
    # ========================================================================

    def create_vehicle(
        self,
        license_plate: str,
        brand: str,
        model: str,
        fuel_type: str,
        year: Optional[int] = None,
        vin: Optional[str] = None,
        purchase_date: Optional[date] = None,
        purchase_price: Optional[Decimal] = None,
        current_value: Optional[Decimal] = None,
        current_mileage: Optional[int] = None,
        responsible_employee_id: Optional[int] = None,
        status: str = "ACTIVE",
        insurance_expiry_date: Optional[date] = None,
        mot_expiry_date: Optional[date] = None,
        notes: Optional[str] = None,
        is_active: bool = True
    ) -> Vehicle:
        """
        Új jármű létrehozása.

        Args:
            license_plate: Rendszám (egyedi)
            brand: Márka
            model: Modell
            fuel_type: Üzemanyag típusa
            year: Gyártási év
            vin: VIN szám (egyedi)
            purchase_date: Beszerzési dátum
            purchase_price: Beszerzési ár
            current_value: Jelenlegi érték
            current_mileage: Aktuális kilométeróra állás
            responsible_employee_id: Felelős munkatárs
            status: Státusz (default: ACTIVE)
            insurance_expiry_date: Biztosítás lejárata
            mot_expiry_date: Műszaki vizsga lejárata
            notes: Megjegyzések
            is_active: Aktív státusz

        Returns:
            Vehicle: Létrehozott jármű rekord

        Raises:
            ValueError: Ha a rendszám vagy VIN már létezik
        """
        # Ellenőrizzük hogy a rendszám egyedi-e
        existing = self.db.query(Vehicle).filter(
            Vehicle.license_plate == license_plate
        ).first()

        if existing:
            raise ValueError(f"A rendszám már létezik: {license_plate}")

        # VIN egyediség ellenőrzése ha meg van adva
        if vin:
            existing_vin = self.db.query(Vehicle).filter(
                Vehicle.vin == vin
            ).first()

            if existing_vin:
                raise ValueError(f"A VIN szám már létezik: {vin}")

        # Validáljuk a státuszt
        try:
            vehicle_status = VehicleStatus(status)
        except ValueError:
            raise ValueError(f"Érvénytelen jármű státusz: {status}")

        # Validáljuk az üzemanyag típust
        try:
            fuel_type_enum = FuelType(fuel_type)
        except ValueError:
            raise ValueError(f"Érvénytelen üzemanyag típus: {fuel_type}")

        vehicle = Vehicle(
            license_plate=license_plate,
            brand=brand,
            model=model,
            year=year,
            vin=vin,
            fuel_type=fuel_type_enum,
            purchase_date=purchase_date,
            purchase_price=purchase_price,
            current_value=current_value,
            current_mileage=current_mileage,
            responsible_employee_id=responsible_employee_id,
            status=vehicle_status,
            insurance_expiry_date=insurance_expiry_date,
            mot_expiry_date=mot_expiry_date,
            notes=notes,
            is_active=is_active
        )

        self.db.add(vehicle)
        self.db.commit()
        self.db.refresh(vehicle)

        return vehicle

    def get_vehicle_by_id(self, vehicle_id: int) -> Optional[Vehicle]:
        """
        Jármű lekérdezése azonosító alapján.

        Args:
            vehicle_id: Jármű azonosító

        Returns:
            Optional[Vehicle]: Jármű vagy None
        """
        return self.db.query(Vehicle).filter(
            Vehicle.id == vehicle_id
        ).first()

    def get_vehicles(
        self,
        status: Optional[str] = None,
        fuel_type: Optional[str] = None,
        responsible_employee_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Vehicle]:
        """
        Járművek listázása szűrési feltételekkel.

        Args:
            status: Státusz szűrő (opcionális)
            fuel_type: Üzemanyag típus szűrő (opcionális)
            responsible_employee_id: Felelős munkatárs szűrő (opcionális)
            is_active: Aktív státusz szűrő (opcionális)
            limit: Maximum eredmények száma
            offset: Lapozási eltolás

        Returns:
            List[Vehicle]: Járművek listája
        """
        query = self.db.query(Vehicle)

        if status:
            query = query.filter(Vehicle.status == status)

        if fuel_type:
            query = query.filter(Vehicle.fuel_type == fuel_type)

        if responsible_employee_id is not None:
            query = query.filter(Vehicle.responsible_employee_id == responsible_employee_id)

        if is_active is not None:
            query = query.filter(Vehicle.is_active == is_active)

        query = query.order_by(desc(Vehicle.created_at))
        query = query.limit(limit).offset(offset)

        return query.all()

    def update_vehicle(
        self,
        vehicle_id: int,
        license_plate: Optional[str] = None,
        brand: Optional[str] = None,
        model: Optional[str] = None,
        year: Optional[int] = None,
        vin: Optional[str] = None,
        fuel_type: Optional[str] = None,
        purchase_date: Optional[date] = None,
        purchase_price: Optional[Decimal] = None,
        current_value: Optional[Decimal] = None,
        current_mileage: Optional[int] = None,
        responsible_employee_id: Optional[int] = None,
        status: Optional[str] = None,
        insurance_expiry_date: Optional[date] = None,
        mot_expiry_date: Optional[date] = None,
        notes: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Vehicle:
        """
        Jármű frissítése.

        Args:
            vehicle_id: Jármű azonosító
            (+ egyéb opcionális mezők)

        Returns:
            Vehicle: Frissített jármű rekord

        Raises:
            ValueError: Ha a jármű nem található vagy egyediségi megszorítás sérül
        """
        vehicle = self.get_vehicle_by_id(vehicle_id)

        if not vehicle:
            raise ValueError(f"Jármű nem található: {vehicle_id}")

        # Rendszám egyediség ellenőrzése ha módosítva van
        if license_plate and license_plate != vehicle.license_plate:
            existing = self.db.query(Vehicle).filter(
                and_(
                    Vehicle.license_plate == license_plate,
                    Vehicle.id != vehicle_id
                )
            ).first()

            if existing:
                raise ValueError(f"A rendszám már létezik: {license_plate}")

            vehicle.license_plate = license_plate

        # VIN egyediség ellenőrzése ha módosítva van
        if vin and vin != vehicle.vin:
            existing_vin = self.db.query(Vehicle).filter(
                and_(
                    Vehicle.vin == vin,
                    Vehicle.id != vehicle_id
                )
            ).first()

            if existing_vin:
                raise ValueError(f"A VIN szám már létezik: {vin}")

            vehicle.vin = vin

        if brand is not None:
            vehicle.brand = brand

        if model is not None:
            vehicle.model = model

        if year is not None:
            vehicle.year = year

        if fuel_type is not None:
            try:
                vehicle.fuel_type = FuelType(fuel_type)
            except ValueError:
                raise ValueError(f"Érvénytelen üzemanyag típus: {fuel_type}")

        if purchase_date is not None:
            vehicle.purchase_date = purchase_date

        if purchase_price is not None:
            vehicle.purchase_price = purchase_price

        if current_value is not None:
            vehicle.current_value = current_value

        if current_mileage is not None:
            vehicle.current_mileage = current_mileage

        if responsible_employee_id is not None:
            vehicle.responsible_employee_id = responsible_employee_id

        if status is not None:
            try:
                vehicle.status = VehicleStatus(status)
            except ValueError:
                raise ValueError(f"Érvénytelen jármű státusz: {status}")

        if insurance_expiry_date is not None:
            vehicle.insurance_expiry_date = insurance_expiry_date

        if mot_expiry_date is not None:
            vehicle.mot_expiry_date = mot_expiry_date

        if notes is not None:
            vehicle.notes = notes

        if is_active is not None:
            vehicle.is_active = is_active

        self.db.commit()
        self.db.refresh(vehicle)

        return vehicle

    def delete_vehicle(self, vehicle_id: int) -> bool:
        """
        Jármű törlése (soft delete).

        Args:
            vehicle_id: Jármű azonosító

        Returns:
            bool: True ha sikeres volt a törlés

        Raises:
            ValueError: Ha a jármű nem található
        """
        vehicle = self.get_vehicle_by_id(vehicle_id)

        if not vehicle:
            raise ValueError(f"Jármű nem található: {vehicle_id}")

        vehicle.is_active = False
        self.db.commit()

        return True

    # ========================================================================
    # Vehicle Refueling Operations (Tankolások)
    # ========================================================================

    def create_vehicle_refueling(
        self,
        vehicle_id: int,
        refueling_date: date,
        fuel_type: str,
        quantity_liters: Decimal,
        price_per_liter: Decimal,
        total_cost: Decimal,
        mileage: Optional[int] = None,
        full_tank: bool = True,
        location: Optional[str] = None,
        invoice_number: Optional[str] = None,
        recorded_by_employee_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> VehicleRefueling:
        """
        Új tankolás bejegyzés létrehozása.

        Args:
            vehicle_id: Jármű azonosító
            refueling_date: Tankolás dátuma
            fuel_type: Üzemanyag típusa
            quantity_liters: Mennyiség (liter)
            price_per_liter: Egységár (Ft/liter)
            total_cost: Teljes költség
            mileage: Kilométeróra állás tankoláskor
            full_tank: Tele tank (True = teletankolás)
            location: Benzinkút / helyszín
            invoice_number: Számla szám
            recorded_by_employee_id: Rögzítő munkatárs
            notes: Megjegyzések

        Returns:
            VehicleRefueling: Létrehozott tankolás rekord

        Raises:
            ValueError: Ha a jármű nem található vagy az üzemanyag típus érvénytelen
        """
        # Ellenőrizzük hogy a jármű létezik-e
        vehicle = self.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            raise ValueError(f"Jármű nem található: {vehicle_id}")

        # Validáljuk az üzemanyag típust
        try:
            fuel_type_enum = FuelType(fuel_type)
        except ValueError:
            raise ValueError(f"Érvénytelen üzemanyag típus: {fuel_type}")

        refueling = VehicleRefueling(
            vehicle_id=vehicle_id,
            refueling_date=refueling_date,
            mileage=mileage,
            fuel_type=fuel_type_enum,
            quantity_liters=quantity_liters,
            price_per_liter=price_per_liter,
            total_cost=total_cost,
            full_tank=full_tank,
            location=location,
            invoice_number=invoice_number,
            recorded_by_employee_id=recorded_by_employee_id,
            notes=notes
        )

        self.db.add(refueling)
        self.db.commit()
        self.db.refresh(refueling)

        # Frissítsük a jármű kilométeróra állását ha meg van adva
        if mileage and (not vehicle.current_mileage or mileage > vehicle.current_mileage):
            vehicle.current_mileage = mileage
            self.db.commit()

        return refueling

    def get_vehicle_refueling_by_id(self, refueling_id: int) -> Optional[VehicleRefueling]:
        """
        Tankolás bejegyzés lekérdezése azonosító alapján.

        Args:
            refueling_id: Tankolás azonosító

        Returns:
            Optional[VehicleRefueling]: Tankolás bejegyzés vagy None
        """
        return self.db.query(VehicleRefueling).filter(
            VehicleRefueling.id == refueling_id
        ).first()

    def get_vehicle_refuelings(
        self,
        vehicle_id: Optional[int] = None,
        fuel_type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[VehicleRefueling]:
        """
        Tankolás bejegyzések listázása szűrési feltételekkel.

        Args:
            vehicle_id: Jármű azonosító szűrő (opcionális)
            fuel_type: Üzemanyag típus szűrő (opcionális)
            start_date: Kezdő dátum szűrő (opcionális)
            end_date: Záró dátum szűrő (opcionális)
            limit: Maximum eredmények száma
            offset: Lapozási eltolás

        Returns:
            List[VehicleRefueling]: Tankolás bejegyzések listája
        """
        query = self.db.query(VehicleRefueling)

        if vehicle_id is not None:
            query = query.filter(VehicleRefueling.vehicle_id == vehicle_id)

        if fuel_type:
            query = query.filter(VehicleRefueling.fuel_type == fuel_type)

        if start_date:
            query = query.filter(VehicleRefueling.refueling_date >= start_date)

        if end_date:
            query = query.filter(VehicleRefueling.refueling_date <= end_date)

        query = query.order_by(desc(VehicleRefueling.refueling_date))
        query = query.limit(limit).offset(offset)

        return query.all()

    def update_vehicle_refueling(
        self,
        refueling_id: int,
        refueling_date: Optional[date] = None,
        mileage: Optional[int] = None,
        fuel_type: Optional[str] = None,
        quantity_liters: Optional[Decimal] = None,
        price_per_liter: Optional[Decimal] = None,
        total_cost: Optional[Decimal] = None,
        full_tank: Optional[bool] = None,
        location: Optional[str] = None,
        invoice_number: Optional[str] = None,
        recorded_by_employee_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> VehicleRefueling:
        """
        Tankolás bejegyzés frissítése.

        Args:
            refueling_id: Tankolás azonosító
            (+ egyéb opcionális mezők)

        Returns:
            VehicleRefueling: Frissített tankolás rekord

        Raises:
            ValueError: Ha a tankolás nem található vagy az üzemanyag típus érvénytelen
        """
        refueling = self.get_vehicle_refueling_by_id(refueling_id)

        if not refueling:
            raise ValueError(f"Tankolás bejegyzés nem található: {refueling_id}")

        if refueling_date is not None:
            refueling.refueling_date = refueling_date

        if mileage is not None:
            refueling.mileage = mileage

        if fuel_type is not None:
            try:
                refueling.fuel_type = FuelType(fuel_type)
            except ValueError:
                raise ValueError(f"Érvénytelen üzemanyag típus: {fuel_type}")

        if quantity_liters is not None:
            refueling.quantity_liters = quantity_liters

        if price_per_liter is not None:
            refueling.price_per_liter = price_per_liter

        if total_cost is not None:
            refueling.total_cost = total_cost

        if full_tank is not None:
            refueling.full_tank = full_tank

        if location is not None:
            refueling.location = location

        if invoice_number is not None:
            refueling.invoice_number = invoice_number

        if recorded_by_employee_id is not None:
            refueling.recorded_by_employee_id = recorded_by_employee_id

        if notes is not None:
            refueling.notes = notes

        self.db.commit()
        self.db.refresh(refueling)

        return refueling

    def delete_vehicle_refueling(self, refueling_id: int) -> bool:
        """
        Tankolás bejegyzés törlése (hard delete).

        Args:
            refueling_id: Tankolás azonosító

        Returns:
            bool: True ha sikeres volt a törlés

        Raises:
            ValueError: Ha a tankolás nem található
        """
        refueling = self.get_vehicle_refueling_by_id(refueling_id)

        if not refueling:
            raise ValueError(f"Tankolás bejegyzés nem található: {refueling_id}")

        self.db.delete(refueling)
        self.db.commit()

        return True

    # ========================================================================
    # Vehicle Maintenance Operations (Karbantartások)
    # ========================================================================

    def create_vehicle_maintenance(
        self,
        vehicle_id: int,
        maintenance_type: str,
        maintenance_date: date,
        description: str,
        mileage: Optional[int] = None,
        cost: Optional[Decimal] = None,
        service_provider: Optional[str] = None,
        next_maintenance_date: Optional[date] = None,
        next_maintenance_mileage: Optional[int] = None,
        invoice_number: Optional[str] = None,
        recorded_by_employee_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> VehicleMaintenance:
        """
        Új karbantartás bejegyzés létrehozása.

        Args:
            vehicle_id: Jármű azonosító
            maintenance_type: Karbantartás típusa
            maintenance_date: Karbantartás dátuma
            description: Leírás/munka részletei
            mileage: Kilométeróra állás karbantartáskor
            cost: Költség
            service_provider: Szerviz / javítóműhely
            next_maintenance_date: Következő szerviz dátuma
            next_maintenance_mileage: Következő szerviz km állás
            invoice_number: Számla szám
            recorded_by_employee_id: Rögzítő munkatárs
            notes: Megjegyzések

        Returns:
            VehicleMaintenance: Létrehozott karbantartás rekord

        Raises:
            ValueError: Ha a jármű nem található vagy a karbantartás típus érvénytelen
        """
        # Ellenőrizzük hogy a jármű létezik-e
        vehicle = self.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            raise ValueError(f"Jármű nem található: {vehicle_id}")

        # Validáljuk a karbantartás típust
        try:
            maintenance_type_enum = MaintenanceType(maintenance_type)
        except ValueError:
            raise ValueError(f"Érvénytelen karbantartás típus: {maintenance_type}")

        maintenance = VehicleMaintenance(
            vehicle_id=vehicle_id,
            maintenance_type=maintenance_type_enum,
            maintenance_date=maintenance_date,
            mileage=mileage,
            description=description,
            cost=cost,
            service_provider=service_provider,
            next_maintenance_date=next_maintenance_date,
            next_maintenance_mileage=next_maintenance_mileage,
            invoice_number=invoice_number,
            recorded_by_employee_id=recorded_by_employee_id,
            notes=notes
        )

        self.db.add(maintenance)
        self.db.commit()
        self.db.refresh(maintenance)

        # Frissítsük a jármű kilométeróra állását ha meg van adva
        if mileage and (not vehicle.current_mileage or mileage > vehicle.current_mileage):
            vehicle.current_mileage = mileage
            self.db.commit()

        return maintenance

    def get_vehicle_maintenance_by_id(self, maintenance_id: int) -> Optional[VehicleMaintenance]:
        """
        Karbantartás bejegyzés lekérdezése azonosító alapján.

        Args:
            maintenance_id: Karbantartás azonosító

        Returns:
            Optional[VehicleMaintenance]: Karbantartás bejegyzés vagy None
        """
        return self.db.query(VehicleMaintenance).filter(
            VehicleMaintenance.id == maintenance_id
        ).first()

    def get_vehicle_maintenances(
        self,
        vehicle_id: Optional[int] = None,
        maintenance_type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[VehicleMaintenance]:
        """
        Karbantartás bejegyzések listázása szűrési feltételekkel.

        Args:
            vehicle_id: Jármű azonosító szűrő (opcionális)
            maintenance_type: Karbantartás típus szűrő (opcionális)
            start_date: Kezdő dátum szűrő (opcionális)
            end_date: Záró dátum szűrő (opcionális)
            limit: Maximum eredmények száma
            offset: Lapozási eltolás

        Returns:
            List[VehicleMaintenance]: Karbantartás bejegyzések listája
        """
        query = self.db.query(VehicleMaintenance)

        if vehicle_id is not None:
            query = query.filter(VehicleMaintenance.vehicle_id == vehicle_id)

        if maintenance_type:
            query = query.filter(VehicleMaintenance.maintenance_type == maintenance_type)

        if start_date:
            query = query.filter(VehicleMaintenance.maintenance_date >= start_date)

        if end_date:
            query = query.filter(VehicleMaintenance.maintenance_date <= end_date)

        query = query.order_by(desc(VehicleMaintenance.maintenance_date))
        query = query.limit(limit).offset(offset)

        return query.all()

    def update_vehicle_maintenance(
        self,
        maintenance_id: int,
        maintenance_type: Optional[str] = None,
        maintenance_date: Optional[date] = None,
        mileage: Optional[int] = None,
        description: Optional[str] = None,
        cost: Optional[Decimal] = None,
        service_provider: Optional[str] = None,
        next_maintenance_date: Optional[date] = None,
        next_maintenance_mileage: Optional[int] = None,
        invoice_number: Optional[str] = None,
        recorded_by_employee_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> VehicleMaintenance:
        """
        Karbantartás bejegyzés frissítése.

        Args:
            maintenance_id: Karbantartás azonosító
            (+ egyéb opcionális mezők)

        Returns:
            VehicleMaintenance: Frissített karbantartás rekord

        Raises:
            ValueError: Ha a karbantartás nem található vagy a típus érvénytelen
        """
        maintenance = self.get_vehicle_maintenance_by_id(maintenance_id)

        if not maintenance:
            raise ValueError(f"Karbantartás bejegyzés nem található: {maintenance_id}")

        if maintenance_type is not None:
            try:
                maintenance.maintenance_type = MaintenanceType(maintenance_type)
            except ValueError:
                raise ValueError(f"Érvénytelen karbantartás típus: {maintenance_type}")

        if maintenance_date is not None:
            maintenance.maintenance_date = maintenance_date

        if mileage is not None:
            maintenance.mileage = mileage

        if description is not None:
            maintenance.description = description

        if cost is not None:
            maintenance.cost = cost

        if service_provider is not None:
            maintenance.service_provider = service_provider

        if next_maintenance_date is not None:
            maintenance.next_maintenance_date = next_maintenance_date

        if next_maintenance_mileage is not None:
            maintenance.next_maintenance_mileage = next_maintenance_mileage

        if invoice_number is not None:
            maintenance.invoice_number = invoice_number

        if recorded_by_employee_id is not None:
            maintenance.recorded_by_employee_id = recorded_by_employee_id

        if notes is not None:
            maintenance.notes = notes

        self.db.commit()
        self.db.refresh(maintenance)

        return maintenance

    def delete_vehicle_maintenance(self, maintenance_id: int) -> bool:
        """
        Karbantartás bejegyzés törlése (hard delete).

        Args:
            maintenance_id: Karbantartás azonosító

        Returns:
            bool: True ha sikeres volt a törlés

        Raises:
            ValueError: Ha a karbantartás nem található
        """
        maintenance = self.get_vehicle_maintenance_by_id(maintenance_id)

        if not maintenance:
            raise ValueError(f"Karbantartás bejegyzés nem található: {maintenance_id}")

        self.db.delete(maintenance)
        self.db.commit()

        return True

    # ========================================================================
    # Warning & Alert Operations (Figyelmeztetések)
    # ========================================================================

    def get_vehicle_warnings(self, vehicle_id: int, days_threshold: int = 30) -> Dict[str, any]:
        """
        Egy adott jármű figyelmeztetéseinek lekérdezése.

        Figyelmeztetések:
        - Biztosítás lejárat közeleg
        - Műszaki vizsga lejárat közeleg
        - Következő szerviz esedékes (dátum vagy km alapján)

        Args:
            vehicle_id: Jármű azonosító
            days_threshold: Hány nappal előre figyelmeztessen (default: 30)

        Returns:
            Dict: Figyelmeztetések dictionary

        Raises:
            ValueError: Ha a jármű nem található
        """
        vehicle = self.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            raise ValueError(f"Jármű nem található: {vehicle_id}")

        warnings = {
            "vehicle_id": vehicle_id,
            "license_plate": vehicle.license_plate,
            "warnings": []
        }

        today = date.today()
        threshold_date = today + timedelta(days=days_threshold)

        # Biztosítás lejárat ellenőrzése
        if vehicle.insurance_expiry_date:
            if vehicle.insurance_expiry_date < today:
                warnings["warnings"].append({
                    "type": "insurance_expired",
                    "message": f"Biztosítás LEJÁRT: {vehicle.insurance_expiry_date}",
                    "severity": "critical",
                    "date": vehicle.insurance_expiry_date
                })
            elif vehicle.insurance_expiry_date <= threshold_date:
                days_left = (vehicle.insurance_expiry_date - today).days
                warnings["warnings"].append({
                    "type": "insurance_expiring",
                    "message": f"Biztosítás hamarosan lejár: {vehicle.insurance_expiry_date} ({days_left} nap)",
                    "severity": "warning",
                    "date": vehicle.insurance_expiry_date
                })

        # Műszaki vizsga lejárat ellenőrzése
        if vehicle.mot_expiry_date:
            if vehicle.mot_expiry_date < today:
                warnings["warnings"].append({
                    "type": "mot_expired",
                    "message": f"Műszaki vizsga LEJÁRT: {vehicle.mot_expiry_date}",
                    "severity": "critical",
                    "date": vehicle.mot_expiry_date
                })
            elif vehicle.mot_expiry_date <= threshold_date:
                days_left = (vehicle.mot_expiry_date - today).days
                warnings["warnings"].append({
                    "type": "mot_expiring",
                    "message": f"Műszaki vizsga hamarosan lejár: {vehicle.mot_expiry_date} ({days_left} nap)",
                    "severity": "warning",
                    "date": vehicle.mot_expiry_date
                })

        # Következő karbantartás esedékessége (legutóbbi bejegyzés alapján)
        latest_maintenance = self.db.query(VehicleMaintenance).filter(
            VehicleMaintenance.vehicle_id == vehicle_id
        ).order_by(desc(VehicleMaintenance.maintenance_date)).first()

        if latest_maintenance:
            # Dátum alapú figyelmeztetés
            if latest_maintenance.next_maintenance_date:
                if latest_maintenance.next_maintenance_date < today:
                    warnings["warnings"].append({
                        "type": "maintenance_overdue",
                        "message": f"Szerviz esedékes volt: {latest_maintenance.next_maintenance_date}",
                        "severity": "warning",
                        "date": latest_maintenance.next_maintenance_date
                    })
                elif latest_maintenance.next_maintenance_date <= threshold_date:
                    days_left = (latest_maintenance.next_maintenance_date - today).days
                    warnings["warnings"].append({
                        "type": "maintenance_due",
                        "message": f"Következő szerviz közeleg: {latest_maintenance.next_maintenance_date} ({days_left} nap)",
                        "severity": "info",
                        "date": latest_maintenance.next_maintenance_date
                    })

            # Kilométer alapú figyelmeztetés
            if latest_maintenance.next_maintenance_mileage and vehicle.current_mileage:
                if vehicle.current_mileage >= latest_maintenance.next_maintenance_mileage:
                    warnings["warnings"].append({
                        "type": "maintenance_mileage_overdue",
                        "message": f"Szerviz esedékes kilométer alapján: {latest_maintenance.next_maintenance_mileage} km (jelenlegi: {vehicle.current_mileage} km)",
                        "severity": "warning",
                        "mileage": latest_maintenance.next_maintenance_mileage
                    })
                elif vehicle.current_mileage >= (latest_maintenance.next_maintenance_mileage - 1000):
                    km_left = latest_maintenance.next_maintenance_mileage - vehicle.current_mileage
                    warnings["warnings"].append({
                        "type": "maintenance_mileage_due",
                        "message": f"Szerviz közeleg kilométer alapján: {latest_maintenance.next_maintenance_mileage} km ({km_left} km van hátra)",
                        "severity": "info",
                        "mileage": latest_maintenance.next_maintenance_mileage
                    })

        return warnings

    def get_all_vehicle_warnings(self, days_threshold: int = 30) -> List[Dict[str, any]]:
        """
        Összes aktív jármű figyelmeztetéseinek lekérdezése.

        Args:
            days_threshold: Hány nappal előre figyelmeztessen (default: 30)

        Returns:
            List[Dict]: Járművek figyelmeztetéseinek listája
        """
        vehicles = self.get_vehicles(is_active=True, limit=1000)

        all_warnings = []
        for vehicle in vehicles:
            vehicle_warnings = self.get_vehicle_warnings(vehicle.id, days_threshold)
            if vehicle_warnings["warnings"]:  # Csak akkor adjuk hozzá ha van figyelmeztetés
                all_warnings.append(vehicle_warnings)

        return all_warnings
