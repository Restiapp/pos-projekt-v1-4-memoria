"""
Address Service - Business Logic Layer
Module 5: Customer Relationship Management (CRM)

Ez a service layer felelős a címek üzleti logikájáért, beleértve:
- CRUD műveletek (Create, Read, Update, Delete)
- Ügyfél címeinek kezelése
- Alapértelmezett cím beállítása
- Számlázási és szállítási címek kezelése
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status
import logging

from backend.service_crm.models.address import Address
from backend.service_crm.schemas.address import (
    AddressCreate,
    AddressUpdate,
    AddressTypeEnum
)

logger = logging.getLogger(__name__)


class AddressService:
    """
    Service osztály a címek kezeléséhez.

    Felelősségek:
    - Címek létrehozása, lekérdezése, módosítása, törlése
    - Alapértelmezett címek kezelése
    - Ügyfél címeinek lekérdezése
    """

    @staticmethod
    def create_address(db: Session, address_data: AddressCreate) -> Address:
        """
        Új cím létrehozása.

        Args:
            db: SQLAlchemy session
            address_data: AddressCreate schema a bemeneti adatokkal

        Returns:
            Address: Az újonnan létrehozott cím

        Raises:
            HTTPException 400: Ha az adatok érvénytelenek

        Example:
            >>> address_data = AddressCreate(
            ...     customer_id=42,
            ...     address_type=AddressTypeEnum.SHIPPING,
            ...     postal_code="1011",
            ...     city="Budapest",
            ...     street_address="Fő utca",
            ...     street_number="1"
            ... )
            >>> new_address = AddressService.create_address(db, address_data)
        """
        try:
            # Ha ez lesz az első cím, vagy is_default=True, akkor állítsuk be alapértelmezettnek
            if address_data.is_default:
                # Ha már van alapértelmezett cím ugyanazzal a típussal, töröljük az alapértelmezett státuszt
                AddressService._unset_default_address(
                    db,
                    address_data.customer_id,
                    address_data.address_type
                )

            # Új Address objektum létrehozása
            db_address = Address(
                customer_id=address_data.customer_id,
                address_type=address_data.address_type.value,
                is_default=address_data.is_default,
                country=address_data.country,
                postal_code=address_data.postal_code,
                city=address_data.city,
                street_address=address_data.street_address,
                street_number=address_data.street_number,
                building=address_data.building,
                floor=address_data.floor,
                door=address_data.door,
                company_name=address_data.company_name,
                notes=address_data.notes
            )

            db.add(db_address)
            db.commit()
            db.refresh(db_address)

            logger.info(f"Address created: {db_address.id} for customer {db_address.customer_id}")
            return db_address

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating address: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hiba a cím létrehozása során: {str(e)}"
            )

    @staticmethod
    def get_address(db: Session, address_id: int) -> Address:
        """
        Egy cím lekérdezése ID alapján.

        Args:
            db: SQLAlchemy session
            address_id: A cím azonosítója

        Returns:
            Address: A lekérdezett cím

        Raises:
            HTTPException 404: Ha a cím nem található

        Example:
            >>> address = AddressService.get_address(db, address_id=42)
        """
        address = db.query(Address).filter(Address.id == address_id).first()

        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cím nem található: ID={address_id}"
            )

        return address

    @staticmethod
    def get_addresses(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        customer_id: Optional[int] = None,
        address_type: Optional[AddressTypeEnum] = None,
        is_default: Optional[bool] = None
    ) -> List[Address]:
        """
        Címek listájának lekérdezése szűrési lehetőségekkel.

        Args:
            db: SQLAlchemy session
            skip: Kihagyandó elemek száma (pagination)
            limit: Maximum visszaadott elemek száma
            customer_id: Szűrés ügyfél ID alapján
            address_type: Szűrés cím típus alapján
            is_default: Szűrés alapértelmezett címekre

        Returns:
            List[Address]: Címek listája

        Example:
            >>> addresses = AddressService.get_addresses(
            ...     db,
            ...     skip=0,
            ...     limit=20,
            ...     customer_id=42,
            ...     address_type=AddressTypeEnum.SHIPPING
            ... )
        """
        query = db.query(Address)

        # Ügyfél szűrés
        if customer_id is not None:
            query = query.filter(Address.customer_id == customer_id)

        # Cím típus szűrés
        if address_type is not None:
            query = query.filter(Address.address_type == address_type.value)

        # Alapértelmezett szűrés
        if is_default is not None:
            query = query.filter(Address.is_default == is_default)

        # Rendezés: legutóbb létrehozott először
        query = query.order_by(desc(Address.created_at))

        # Pagination
        addresses = query.offset(skip).limit(limit).all()

        return addresses

    @staticmethod
    def get_customer_addresses(
        db: Session,
        customer_id: int,
        address_type: Optional[AddressTypeEnum] = None
    ) -> List[Address]:
        """
        Egy ügyfél összes címének lekérdezése.

        Args:
            db: SQLAlchemy session
            customer_id: Az ügyfél azonosítója
            address_type: Opcionális szűrés cím típus alapján

        Returns:
            List[Address]: Címek listája

        Example:
            >>> addresses = AddressService.get_customer_addresses(db, customer_id=42)
        """
        return AddressService.get_addresses(
            db,
            customer_id=customer_id,
            address_type=address_type,
            skip=0,
            limit=100
        )

    @staticmethod
    def get_default_address(
        db: Session,
        customer_id: int,
        address_type: AddressTypeEnum
    ) -> Optional[Address]:
        """
        Ügyfél alapértelmezett címének lekérdezése típus alapján.

        Args:
            db: SQLAlchemy session
            customer_id: Az ügyfél azonosítója
            address_type: A cím típusa (SHIPPING, BILLING, BOTH)

        Returns:
            Optional[Address]: Az alapértelmezett cím vagy None

        Example:
            >>> default_shipping = AddressService.get_default_address(
            ...     db,
            ...     customer_id=42,
            ...     address_type=AddressTypeEnum.SHIPPING
            ... )
        """
        return db.query(Address).filter(
            Address.customer_id == customer_id,
            Address.address_type == address_type.value,
            Address.is_default == True
        ).first()

    @staticmethod
    def update_address(
        db: Session,
        address_id: int,
        address_data: AddressUpdate
    ) -> Address:
        """
        Cím adatainak módosítása.

        Args:
            db: SQLAlchemy session
            address_id: A módosítandó cím azonosítója
            address_data: AddressUpdate schema a módosítandó mezőkkel

        Returns:
            Address: A módosított cím

        Raises:
            HTTPException 404: Ha a cím nem található
            HTTPException 400: Ha a módosítás sikertelen

        Example:
            >>> update_data = AddressUpdate(floor="2", door="15")
            >>> updated_address = AddressService.update_address(db, address_id=42, address_data=update_data)
        """
        # Cím lekérdezése
        address = AddressService.get_address(db, address_id)

        try:
            # Ha is_default értéke változik True-ra, töröljük a többi cím alapértelmezett státuszát
            if address_data.is_default is not None and address_data.is_default:
                address_type = address_data.address_type if address_data.address_type else AddressTypeEnum(address.address_type)
                AddressService._unset_default_address(
                    db,
                    address.customer_id,
                    address_type,
                    exclude_address_id=address_id
                )

            # Csak a megadott mezők frissítése (exclude_unset=True)
            update_dict = address_data.model_dump(exclude_unset=True)

            # Enum konverzió address_type-nál
            if 'address_type' in update_dict and update_dict['address_type']:
                update_dict['address_type'] = update_dict['address_type'].value

            for field, value in update_dict.items():
                setattr(address, field, value)

            db.commit()
            db.refresh(address)

            logger.info(f"Address updated: {address.id}")
            return address

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating address {address_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hiba a cím módosítása során: {str(e)}"
            )

    @staticmethod
    def delete_address(db: Session, address_id: int) -> Dict[str, Any]:
        """
        Cím törlése (hard delete).

        Args:
            db: SQLAlchemy session
            address_id: A törlendő cím azonosítója

        Returns:
            Dict: Megerősítő üzenet

        Raises:
            HTTPException 404: Ha a cím nem található

        Example:
            >>> result = AddressService.delete_address(db, address_id=42)
        """
        address = AddressService.get_address(db, address_id)

        try:
            db.delete(address)
            db.commit()

            logger.info(f"Address deleted: {address_id}")
            return {
                "message": "Cím sikeresen törölve",
                "address_id": address_id
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting address {address_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hiba a cím törlése során: {str(e)}"
            )

    @staticmethod
    def count_addresses(
        db: Session,
        customer_id: Optional[int] = None,
        address_type: Optional[AddressTypeEnum] = None,
        is_default: Optional[bool] = None
    ) -> int:
        """
        Címek számának lekérdezése szűrési lehetőségekkel.

        Args:
            db: SQLAlchemy session
            customer_id: Szűrés ügyfél ID alapján
            address_type: Szűrés cím típus alapján
            is_default: Szűrés alapértelmezett címekre

        Returns:
            int: Címek száma

        Example:
            >>> count = AddressService.count_addresses(db, customer_id=42)
        """
        query = db.query(Address)

        if customer_id is not None:
            query = query.filter(Address.customer_id == customer_id)

        if address_type is not None:
            query = query.filter(Address.address_type == address_type.value)

        if is_default is not None:
            query = query.filter(Address.is_default == is_default)

        return query.count()

    @staticmethod
    def set_default_address(
        db: Session,
        address_id: int
    ) -> Address:
        """
        Cím beállítása alapértelmezettként.

        Args:
            db: SQLAlchemy session
            address_id: A cím azonosítója

        Returns:
            Address: A módosított cím

        Raises:
            HTTPException 404: Ha a cím nem található

        Example:
            >>> address = AddressService.set_default_address(db, address_id=42)
        """
        address = AddressService.get_address(db, address_id)

        try:
            # Töröljük a többi cím alapértelmezett státuszát ugyanannál a típusnál
            AddressService._unset_default_address(
                db,
                address.customer_id,
                AddressTypeEnum(address.address_type),
                exclude_address_id=address_id
            )

            # Beállítjuk az aktuális címet alapértelmezettnek
            address.is_default = True
            db.commit()
            db.refresh(address)

            logger.info(f"Address set as default: {address_id}")
            return address

        except Exception as e:
            db.rollback()
            logger.error(f"Error setting default address {address_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hiba az alapértelmezett cím beállítása során: {str(e)}"
            )

    @staticmethod
    def _unset_default_address(
        db: Session,
        customer_id: int,
        address_type: AddressTypeEnum,
        exclude_address_id: Optional[int] = None
    ) -> None:
        """
        Töröljük az alapértelmezett státuszt az adott típusú címekről.

        Args:
            db: SQLAlchemy session
            customer_id: Az ügyfél azonosítója
            address_type: A cím típusa
            exclude_address_id: Kihagyandó cím ID (opcionális)

        Example:
            >>> AddressService._unset_default_address(db, 42, AddressTypeEnum.SHIPPING, exclude_address_id=10)
        """
        query = db.query(Address).filter(
            Address.customer_id == customer_id,
            Address.address_type == address_type.value,
            Address.is_default == True
        )

        if exclude_address_id is not None:
            query = query.filter(Address.id != exclude_address_id)

        addresses = query.all()
        for addr in addresses:
            addr.is_default = False

        db.flush()
