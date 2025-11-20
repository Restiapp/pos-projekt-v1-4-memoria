"""
Reservation Service - Business Logic Layer
Module 1: Rendeléskezelés és Asztalok

Ez a modul kezeli a foglalásokkal kapcsolatos üzleti logikát.
CRUD műveletek és validációs logika a foglalásokhoz.
"""

from typing import Optional, List
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

from backend.service_orders.models.reservation import Reservation
from backend.service_orders.models.table import Table
from backend.service_orders.schemas.reservation import ReservationCreate, ReservationUpdate


class ReservationService:
    """
    Service osztály a foglalások kezeléséhez.

    Támogatott műveletek:
    - Új foglalás létrehozása
    - Foglalás lekérdezése ID alapján
    - Összes foglalás listázása (pagináció támogatással)
    - Foglalások szűrése dátum szerint
    - Foglalás frissítése (státusz, részletek)
    - Foglalás törlése
    """

    @staticmethod
    def create_reservation(db: Session, reservation_data: ReservationCreate) -> Reservation:
        """
        Új foglalás létrehozása az adatbázisban.

        Args:
            db: SQLAlchemy session
            reservation_data: ReservationCreate schema az új foglalás adataival

        Returns:
            Reservation: A létrehozott foglalás objektum

        Raises:
            ValueError: Ha az asztal nem létezik vagy ha validációs hiba történik
        """
        # Ellenőrizzük, hogy létezik-e az asztal
        table = db.query(Table).filter(Table.id == reservation_data.table_id).first()
        if not table:
            raise ValueError(f"Asztal (ID: {reservation_data.table_id}) nem található")

        # Ellenőrizzük, hogy a vendégszám nem haladja-e meg az asztal kapacitását
        if table.capacity and reservation_data.guest_count > table.capacity:
            raise ValueError(
                f"A vendégszám ({reservation_data.guest_count}) meghaladja az asztal kapacitását ({table.capacity})"
            )

        db_reservation = Reservation(
            table_id=reservation_data.table_id,
            customer_id=reservation_data.customer_id,
            guest_name=reservation_data.guest_name,
            guest_phone=reservation_data.guest_phone,
            guest_email=reservation_data.guest_email,
            reservation_date=reservation_data.reservation_date,
            reservation_time=reservation_data.reservation_time,
            guest_count=reservation_data.guest_count,
            duration_minutes=reservation_data.duration_minutes or 120,
            status=reservation_data.status or "PENDING",
            special_requests=reservation_data.special_requests
        )

        db.add(db_reservation)
        try:
            db.commit()
            db.refresh(db_reservation)
        except IntegrityError as e:
            db.rollback()
            raise ValueError("Hiba történt a foglalás létrehozása során") from e

        return db_reservation

    @staticmethod
    def get_reservation(db: Session, reservation_id: int) -> Optional[Reservation]:
        """
        Foglalás lekérdezése ID alapján.

        Args:
            db: SQLAlchemy session
            reservation_id: A foglalás egyedi azonosítója

        Returns:
            Reservation | None: A foglalás objektum vagy None, ha nem található
        """
        return db.query(Reservation).filter(Reservation.id == reservation_id).first()

    @staticmethod
    def list_reservations(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Reservation], int]:
        """
        Összes foglalás listázása pagináció támogatással.

        Args:
            db: SQLAlchemy session
            skip: Hány rekordot hagyjon ki (offset)
            limit: Maximum hány rekordot adjon vissza

        Returns:
            tuple: (foglalások listája, összes foglalás száma)
        """
        query = db.query(Reservation)
        total = query.count()
        reservations = query.order_by(
            Reservation.reservation_date.desc(),
            Reservation.reservation_time.desc()
        ).offset(skip).limit(limit).all()

        return reservations, total

    @staticmethod
    def get_reservations_by_date(
        db: Session,
        reservation_date: date
    ) -> List[Reservation]:
        """
        Foglalások lekérdezése dátum alapján.

        Args:
            db: SQLAlchemy session
            reservation_date: A foglalás dátuma

        Returns:
            List[Reservation]: Foglalások listája az adott napon
        """
        return db.query(Reservation).filter(
            Reservation.reservation_date == reservation_date
        ).order_by(Reservation.reservation_time).all()

    @staticmethod
    def get_reservations_by_date_range(
        db: Session,
        start_date: date,
        end_date: date
    ) -> List[Reservation]:
        """
        Foglalások lekérdezése dátumtartomány alapján.

        Args:
            db: SQLAlchemy session
            start_date: Kezdő dátum
            end_date: Záró dátum

        Returns:
            List[Reservation]: Foglalások listája a megadott időszakban
        """
        return db.query(Reservation).filter(
            and_(
                Reservation.reservation_date >= start_date,
                Reservation.reservation_date <= end_date
            )
        ).order_by(
            Reservation.reservation_date,
            Reservation.reservation_time
        ).all()

    @staticmethod
    def get_reservations_by_table(
        db: Session,
        table_id: int
    ) -> List[Reservation]:
        """
        Foglalások lekérdezése asztal alapján.

        Args:
            db: SQLAlchemy session
            table_id: Az asztal azonosítója

        Returns:
            List[Reservation]: Foglalások listája az adott asztalra
        """
        return db.query(Reservation).filter(
            Reservation.table_id == table_id
        ).order_by(
            Reservation.reservation_date.desc(),
            Reservation.reservation_time.desc()
        ).all()

    @staticmethod
    def get_reservations_by_status(
        db: Session,
        status: str
    ) -> List[Reservation]:
        """
        Foglalások lekérdezése státusz alapján.

        Args:
            db: SQLAlchemy session
            status: Foglalás státusza (PENDING, CONFIRMED, CANCELLED, COMPLETED, NO_SHOW)

        Returns:
            List[Reservation]: Foglalások listája a megadott státusszal
        """
        return db.query(Reservation).filter(
            Reservation.status == status
        ).order_by(
            Reservation.reservation_date,
            Reservation.reservation_time
        ).all()

    @staticmethod
    def update_reservation(
        db: Session,
        reservation_id: int,
        reservation_data: ReservationUpdate
    ) -> Optional[Reservation]:
        """
        Foglalás frissítése.

        Args:
            db: SQLAlchemy session
            reservation_id: A frissítendő foglalás azonosítója
            reservation_data: ReservationUpdate schema a módosítandó adatokkal

        Returns:
            Reservation | None: A frissített foglalás vagy None, ha nem található

        Raises:
            ValueError: Ha validációs hiba történik
        """
        db_reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if not db_reservation:
            return None

        # Frissítsük csak a megadott mezőket
        update_data = reservation_data.model_dump(exclude_unset=True)

        # Ha asztal ID változik, ellenőrizzük, hogy létezik-e
        if 'table_id' in update_data:
            table = db.query(Table).filter(Table.id == update_data['table_id']).first()
            if not table:
                raise ValueError(f"Asztal (ID: {update_data['table_id']}) nem található")

            # Ellenőrizzük a kapacitást
            guest_count = update_data.get('guest_count', db_reservation.guest_count)
            if table.capacity and guest_count > table.capacity:
                raise ValueError(
                    f"A vendégszám ({guest_count}) meghaladja az asztal kapacitását ({table.capacity})"
                )

        # Ha csak a vendégszám változik, ellenőrizzük a jelenlegi asztal kapacitását
        if 'guest_count' in update_data and 'table_id' not in update_data:
            table = db.query(Table).filter(Table.id == db_reservation.table_id).first()
            if table and table.capacity and update_data['guest_count'] > table.capacity:
                raise ValueError(
                    f"A vendégszám ({update_data['guest_count']}) meghaladja az asztal kapacitását ({table.capacity})"
                )

        for key, value in update_data.items():
            setattr(db_reservation, key, value)

        try:
            db.commit()
            db.refresh(db_reservation)
        except IntegrityError as e:
            db.rollback()
            raise ValueError("Hiba történt a foglalás frissítése során") from e

        return db_reservation

    @staticmethod
    def delete_reservation(db: Session, reservation_id: int) -> bool:
        """
        Foglalás törlése.

        Args:
            db: SQLAlchemy session
            reservation_id: A törlendő foglalás azonosítója

        Returns:
            bool: True ha sikeres, False ha nem található a foglalás
        """
        db_reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if not db_reservation:
            return False

        db.delete(db_reservation)
        db.commit()
        return True

    @staticmethod
    def update_reservation_status(
        db: Session,
        reservation_id: int,
        status: str
    ) -> Optional[Reservation]:
        """
        Foglalás státuszának frissítése.

        Args:
            db: SQLAlchemy session
            reservation_id: A foglalás azonosítója
            status: Új státusz

        Returns:
            Reservation | None: A frissített foglalás vagy None, ha nem található
        """
        db_reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if not db_reservation:
            return None

        db_reservation.status = status
        db.commit()
        db.refresh(db_reservation)
        return db_reservation
