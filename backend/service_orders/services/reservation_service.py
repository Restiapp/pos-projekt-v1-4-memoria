"""
Reservation Service - Business Logic Layer
Module 1: Rendeléskezelés és Asztalok

Ez a modul kezeli a foglalásokkal kapcsolatos üzleti logikát.
CRUD műveletek, validációs logika és smart availability checking.
"""

from typing import Optional, List
from datetime import datetime, date, time, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_

from backend.service_orders.models.reservation import Reservation, ReservationStatus, ReservationSource
from backend.service_orders.models.opening_hours import OpeningHours
from backend.service_orders.models.table import Table
from backend.service_orders.schemas.reservation import (
    ReservationCreate,
    ReservationUpdate,
    AvailabilityQuery,
    TimeSlot
)


class ReservationService:
    """
    Service osztály a foglalások kezeléséhez.

    Támogatott műveletek:
    - Új foglalás létrehozása (ütközés ellenőrzéssel)
    - Foglalás lekérdezése ID alapján
    - Összes foglalás listázása (szűrőkkel és paginációval)
    - Foglalás frissítése
    - Foglalás törlése/lemondása
    - Smart availability checking (szabad időpontok keresése)
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
            ValueError: Ha az asztal nem létezik, nincs elég kapacitás, vagy ütközés van
        """
        # 1. Ellenőrizzük, hogy az asztal létezik-e
        table = db.query(Table).filter(Table.id == reservation_data.table_id).first()
        if not table:
            raise ValueError(f"Asztal (ID: {reservation_data.table_id}) nem található")

        # 2. Ellenőrizzük a kapacitást
        if table.capacity and reservation_data.guest_count > table.capacity:
            raise ValueError(
                f"Az asztal kapacitása ({table.capacity} fő) kevesebb, mint a vendégek száma "
                f"({reservation_data.guest_count} fő)"
            )

        # 3. Ütközés ellenőrzése
        end_time = reservation_data.start_time + timedelta(minutes=reservation_data.duration_minutes)
        conflict = ReservationService._check_conflict(
            db,
            table_id=reservation_data.table_id,
            start_time=reservation_data.start_time,
            end_time=end_time,
            exclude_reservation_id=None
        )
        if conflict:
            raise ValueError(
                f"Az asztal már foglalt ebben az időpontban. "
                f"Ütköző foglalás: {conflict.start_time} - "
                f"{conflict.start_time + timedelta(minutes=conflict.duration_minutes)}"
            )

        # 4. Foglalás létrehozása
        db_reservation = Reservation(
            table_id=reservation_data.table_id,
            customer_name=reservation_data.customer_name,
            customer_phone=reservation_data.customer_phone,
            customer_email=reservation_data.customer_email,
            start_time=reservation_data.start_time,
            duration_minutes=reservation_data.duration_minutes,
            guest_count=reservation_data.guest_count,
            status=ReservationStatus.PENDING,
            source=reservation_data.source,
            notes=reservation_data.notes
        )

        db.add(db_reservation)
        try:
            db.commit()
            db.refresh(db_reservation)
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Adatbázis hiba a foglalás létrehozása során: {str(e)}") from e

        return db_reservation

    @staticmethod
    def _check_conflict(
        db: Session,
        table_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_reservation_id: Optional[int] = None
    ) -> Optional[Reservation]:
        """
        Ellenőrzi, hogy van-e ütköző foglalás az adott asztalra és időpontra.

        Args:
            db: SQLAlchemy session
            table_id: Asztal ID
            start_time: Foglalás kezdete
            end_time: Foglalás vége
            exclude_reservation_id: Kizárandó foglalás ID (update esetén)

        Returns:
            Reservation | None: Ütköző foglalás vagy None
        """
        query = db.query(Reservation).filter(
            Reservation.table_id == table_id,
            Reservation.status.in_([ReservationStatus.PENDING, ReservationStatus.CONFIRMED]),
            or_(
                # Új foglalás kezdete egy meglévő foglalás időtartama alatt van
                and_(
                    Reservation.start_time <= start_time,
                    Reservation.start_time + timedelta(minutes=Reservation.duration_minutes) > start_time
                ),
                # Új foglalás vége egy meglévő foglalás időtartama alatt van
                and_(
                    Reservation.start_time < end_time,
                    Reservation.start_time + timedelta(minutes=Reservation.duration_minutes) >= end_time
                ),
                # Új foglalás teljesen magában foglalja a meglévő foglalást
                and_(
                    Reservation.start_time >= start_time,
                    Reservation.start_time + timedelta(minutes=Reservation.duration_minutes) <= end_time
                )
            )
        )

        if exclude_reservation_id:
            query = query.filter(Reservation.id != exclude_reservation_id)

        return query.first()

    @staticmethod
    def get_reservation(db: Session, reservation_id: int) -> Optional[Reservation]:
        """
        Foglalás lekérdezése ID alapján.

        Args:
            db: SQLAlchemy session
            reservation_id: A foglalás egyedi azonosítója

        Returns:
            Reservation | None: A foglalás objektum vagy None
        """
        return db.query(Reservation).filter(Reservation.id == reservation_id).first()

    @staticmethod
    def list_reservations(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        table_id: Optional[int] = None,
        status: Optional[ReservationStatus] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        customer_phone: Optional[str] = None,
        customer_email: Optional[str] = None
    ) -> tuple[List[Reservation], int]:
        """
        Foglalások listázása szűrőkkel és paginációval.

        Args:
            db: SQLAlchemy session
            skip: Hány rekordot ugorjunk át
            limit: Maximum hány rekordot adjunk vissza
            table_id: Szűrés asztal ID alapján
            status: Szűrés státusz alapján
            date_from: Szűrés kezdő dátum alapján
            date_to: Szűrés záró dátum alapján
            customer_phone: Szűrés telefonszám alapján
            customer_email: Szűrés email alapján

        Returns:
            tuple: (foglalások listája, összes találat száma)
        """
        query = db.query(Reservation)

        # Szűrők alkalmazása
        if table_id:
            query = query.filter(Reservation.table_id == table_id)
        if status:
            query = query.filter(Reservation.status == status)
        if date_from:
            query = query.filter(Reservation.start_time >= datetime.combine(date_from, time.min))
        if date_to:
            query = query.filter(Reservation.start_time <= datetime.combine(date_to, time.max))
        if customer_phone:
            query = query.filter(Reservation.customer_phone.ilike(f"%{customer_phone}%"))
        if customer_email:
            query = query.filter(Reservation.customer_email.ilike(f"%{customer_email}%"))

        # Teljes találatok száma
        total = query.count()

        # Rendezés és lapozás
        reservations = query.order_by(Reservation.start_time.desc()).offset(skip).limit(limit).all()

        return reservations, total

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
            reservation_id: Frissítendő foglalás ID
            reservation_data: Frissítendő mezők

        Returns:
            Reservation | None: Frissített foglalás vagy None

        Raises:
            ValueError: Ha ütközés van vagy validációs hiba
        """
        reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if not reservation:
            return None

        # Frissítendő mezők
        update_data = reservation_data.model_dump(exclude_unset=True)

        # Ha módosítjuk az időpontot vagy asztalt, ellenőrizzük az ütközést
        if 'start_time' in update_data or 'duration_minutes' in update_data or 'table_id' in update_data:
            new_start = update_data.get('start_time', reservation.start_time)
            new_duration = update_data.get('duration_minutes', reservation.duration_minutes)
            new_table_id = update_data.get('table_id', reservation.table_id)
            new_end = new_start + timedelta(minutes=new_duration)

            conflict = ReservationService._check_conflict(
                db,
                table_id=new_table_id,
                start_time=new_start,
                end_time=new_end,
                exclude_reservation_id=reservation_id
            )
            if conflict:
                raise ValueError(
                    f"Az asztal már foglalt ebben az időpontban. "
                    f"Ütköző foglalás ID: {conflict.id}"
                )

        # Kapacitás ellenőrzése, ha módosítjuk a vendégszámot vagy asztalt
        if 'guest_count' in update_data or 'table_id' in update_data:
            table_id = update_data.get('table_id', reservation.table_id)
            guest_count = update_data.get('guest_count', reservation.guest_count)
            table = db.query(Table).filter(Table.id == table_id).first()
            if table and table.capacity and guest_count > table.capacity:
                raise ValueError(
                    f"Az asztal kapacitása ({table.capacity} fő) kevesebb, mint a vendégek száma ({guest_count} fő)"
                )

        # Frissítés
        for field, value in update_data.items():
            setattr(reservation, field, value)

        try:
            db.commit()
            db.refresh(reservation)
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Adatbázis hiba a foglalás frissítése során: {str(e)}") from e

        return reservation

    @staticmethod
    def delete_reservation(db: Session, reservation_id: int) -> bool:
        """
        Foglalás törlése.

        Args:
            db: SQLAlchemy session
            reservation_id: Törlendő foglalás ID

        Returns:
            bool: True ha sikeres, False ha nem található
        """
        reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if not reservation:
            return False

        db.delete(reservation)
        db.commit()
        return True

    @staticmethod
    def cancel_reservation(db: Session, reservation_id: int) -> Optional[Reservation]:
        """
        Foglalás lemondása (státusz CANCELLED-re állítása).

        Args:
            db: SQLAlchemy session
            reservation_id: Lemondandó foglalás ID

        Returns:
            Reservation | None: Lemondott foglalás vagy None
        """
        reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if not reservation:
            return None

        reservation.status = ReservationStatus.CANCELLED
        db.commit()
        db.refresh(reservation)
        return reservation

    @staticmethod
    def get_available_slots(
        db: Session,
        query: AvailabilityQuery
    ) -> tuple[List[TimeSlot], Optional[str]]:
        """
        Smart availability checking - szabad időpontok keresése.

        Args:
            db: SQLAlchemy session
            query: Availability query paraméterek (date, guests, duration)

        Returns:
            tuple: (szabad időpontok listája, opcionális üzenet)
        """
        # 1. Nyitvatartás ellenőrzése
        opening_hours = ReservationService._get_opening_hours(db, query.date)
        if not opening_hours or opening_hours.is_closed:
            return [], "A étterem ezen a napon zárva tart"

        # 2. Megfelelő kapacitású asztalok keresése
        suitable_tables = db.query(Table).filter(
            Table.capacity >= query.guests
        ).all()

        if not suitable_tables:
            return [], f"Nincs megfelelő asztal {query.guests} fő részére"

        # 3. Időpontok generálása (30 perces intervallumokkal)
        available_slots = []
        current_time = datetime.combine(query.date, opening_hours.open_time)
        closing_time = datetime.combine(query.date, opening_hours.close_time)

        # Biztosítjuk, hogy a foglalás vége a zárás előtt legyen
        last_slot_start = closing_time - timedelta(minutes=query.duration_minutes)

        while current_time <= last_slot_start:
            # Minden időpontra ellenőrizzük, mely asztalok szabadok
            end_time = current_time + timedelta(minutes=query.duration_minutes)
            available_table_ids = []

            for table in suitable_tables:
                conflict = ReservationService._check_conflict(
                    db,
                    table_id=table.id,
                    start_time=current_time,
                    end_time=end_time
                )
                if not conflict:
                    available_table_ids.append(table.id)

            # Ha van szabad asztal, hozzáadjuk az időpontot
            if available_table_ids:
                available_slots.append(
                    TimeSlot(
                        time=current_time.time(),
                        available_tables=available_table_ids
                    )
                )

            # Következő időpont (30 perc múlva)
            current_time += timedelta(minutes=30)

        message = None
        if not available_slots:
            message = "Nincs szabad időpont a megadott dátumra és vendégszámra"

        return available_slots, message

    @staticmethod
    def _get_opening_hours(db: Session, target_date: date) -> Optional[OpeningHours]:
        """
        Nyitvatartás lekérdezése egy adott dátumra.

        Prioritás:
        1. Speciális dátum (pl. ünnepek)
        2. Hétköznapi nyitvatartás

        Args:
            db: SQLAlchemy session
            target_date: Cél dátum

        Returns:
            OpeningHours | None: Nyitvatartás vagy None
        """
        # 1. Speciális dátum ellenőrzése
        special = db.query(OpeningHours).filter(
            OpeningHours.special_date == target_date
        ).first()
        if special:
            return special

        # 2. Hétköznapi nyitvatartás (0=Hétfő, 6=Vasárnap)
        day_of_week = target_date.weekday()
        regular = db.query(OpeningHours).filter(
            OpeningHours.day_of_week == day_of_week,
            OpeningHours.special_date.is_(None)
        ).first()

        return regular
