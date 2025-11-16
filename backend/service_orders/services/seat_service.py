"""
Seat Service - Business Logic Layer
Module 1: Rendeléskezelés és Asztalok

Ez a modul kezeli az ülőhelyekkel kapcsolatos üzleti logikát.
CRUD műveletek és validációs logika az ülőhelyekhez.
Támogatja a split-check (számlák személyenkénti felosztását).
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.service_orders.models.seat import Seat
from backend.service_orders.models.table import Table
from backend.service_orders.schemas.seat import SeatCreate, SeatUpdate


class SeatService:
    """
    Service osztály az ülőhelyek kezeléséhez.

    Támogatott műveletek:
    - Új ülőhely létrehozása
    - Ülőhely lekérdezése ID alapján
    - Összes ülőhely listázása (pagináció támogatással)
    - Asztalhoz tartozó ülőhelyek listázása
    - Ülőhely frissítése
    - Ülőhely törlése
    """

    @staticmethod
    def create_seat(db: Session, seat_data: SeatCreate) -> Seat:
        """
        Új ülőhely létrehozása az adatbázisban.

        Args:
            db: SQLAlchemy session
            seat_data: SeatCreate schema az új ülőhely adataival

        Returns:
            Seat: A létrehozott ülőhely objektum

        Raises:
            ValueError: Ha az asztal nem létezik
            IntegrityError: Ha a (table_id, seat_number) kombináció már létezik
        """
        # Ellenőrizzük, hogy létezik-e az asztal
        table_exists = db.query(Table).filter(
            Table.id == seat_data.table_id
        ).first()

        if not table_exists:
            raise ValueError(
                f"Az asztal (ID: {seat_data.table_id}) nem található az adatbázisban."
            )

        db_seat = Seat(
            table_id=seat_data.table_id,
            seat_number=seat_data.seat_number
        )

        db.add(db_seat)
        try:
            db.commit()
            db.refresh(db_seat)
        except IntegrityError as e:
            db.rollback()
            raise ValueError(
                f"Az ülőhely (Asztal ID: {seat_data.table_id}, "
                f"Szék szám: {seat_data.seat_number}) már létezik."
            ) from e

        return db_seat

    @staticmethod
    def get_seat(db: Session, seat_id: int) -> Optional[Seat]:
        """
        Ülőhely lekérdezése ID alapján.

        Args:
            db: SQLAlchemy session
            seat_id: Az ülőhely egyedi azonosítója

        Returns:
            Seat | None: Az ülőhely objektum vagy None, ha nem található
        """
        return db.query(Seat).filter(Seat.id == seat_id).first()

    @staticmethod
    def get_seat_by_table_and_number(
        db: Session,
        table_id: int,
        seat_number: int
    ) -> Optional[Seat]:
        """
        Ülőhely lekérdezése asztal ID és székszám alapján.

        Args:
            db: SQLAlchemy session
            table_id: Az asztal egyedi azonosítója
            seat_number: A szék száma az asztalon belül

        Returns:
            Seat | None: Az ülőhely objektum vagy None, ha nem található
        """
        return db.query(Seat).filter(
            Seat.table_id == table_id,
            Seat.seat_number == seat_number
        ).first()

    @staticmethod
    def list_seats(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Seat], int]:
        """
        Összes ülőhely listázása pagináció támogatással.

        Args:
            db: SQLAlchemy session
            skip: Hány rekordot ugorjunk át (offset)
            limit: Maximum hány rekordot adjunk vissza (page size)

        Returns:
            tuple: (ülőhelyek listája, összes ülőhely száma)
        """
        # Összes ülőhely számának lekérdezése
        total = db.query(Seat).count()

        # Paginált lista lekérdezése
        seats = db.query(Seat).offset(skip).limit(limit).all()

        return seats, total

    @staticmethod
    def list_seats_by_table(db: Session, table_id: int) -> List[Seat]:
        """
        Egy adott asztalhoz tartozó összes ülőhely listázása.

        Args:
            db: SQLAlchemy session
            table_id: Az asztal egyedi azonosítója

        Returns:
            List[Seat]: Az asztalhoz tartozó ülőhelyek listája
        """
        return db.query(Seat).filter(
            Seat.table_id == table_id
        ).order_by(Seat.seat_number).all()

    @staticmethod
    def update_seat(
        db: Session,
        seat_id: int,
        seat_data: SeatUpdate
    ) -> Optional[Seat]:
        """
        Meglévő ülőhely adatainak frissítése.

        Args:
            db: SQLAlchemy session
            seat_id: Az ülőhely egyedi azonosítója
            seat_data: SeatUpdate schema a frissítendő mezőkkel

        Returns:
            Seat | None: A frissített ülőhely objektum vagy None, ha nem található

        Raises:
            ValueError: Ha az új table_id nem létezik
            IntegrityError: Ha a módosítás unique constraint ütközést okoz
        """
        db_seat = db.query(Seat).filter(Seat.id == seat_id).first()

        if not db_seat:
            return None

        # Csak azokat a mezőket frissítjük, amelyek nem None értékűek
        update_data = seat_data.model_dump(exclude_unset=True)

        # Ha módosítjuk a table_id-t, ellenőrizzük, hogy létezik-e
        if 'table_id' in update_data:
            table_exists = db.query(Table).filter(
                Table.id == update_data['table_id']
            ).first()

            if not table_exists:
                raise ValueError(
                    f"Az asztal (ID: {update_data['table_id']}) "
                    f"nem található az adatbázisban."
                )

        for field, value in update_data.items():
            setattr(db_seat, field, value)

        try:
            db.commit()
            db.refresh(db_seat)
        except IntegrityError as e:
            db.rollback()
            raise ValueError(
                f"Nem sikerült frissíteni az ülőhelyet. Lehetséges ok: "
                f"az (Asztal ID: {db_seat.table_id}, "
                f"Szék szám: {db_seat.seat_number}) kombináció már használatban van."
            ) from e

        return db_seat

    @staticmethod
    def delete_seat(db: Session, seat_id: int) -> bool:
        """
        Ülőhely törlése az adatbázisból.

        Args:
            db: SQLAlchemy session
            seat_id: A törlendő ülőhely egyedi azonosítója

        Returns:
            bool: True ha sikeres volt a törlés, False ha nem található az ülőhely

        Note:
            Ha az ülőhelyhez rendelés tételek tartoznak, azok is törlődnek
            vagy orphan maradnak (függ a relationship konfigurációtól).
        """
        db_seat = db.query(Seat).filter(Seat.id == seat_id).first()

        if not db_seat:
            return False

        db.delete(db_seat)
        db.commit()

        return True

    @staticmethod
    def count_seats(db: Session) -> int:
        """
        Összes ülőhely számának lekérdezése.

        Args:
            db: SQLAlchemy session

        Returns:
            int: Az ülőhelyek száma
        """
        return db.query(Seat).count()

    @staticmethod
    def count_seats_by_table(db: Session, table_id: int) -> int:
        """
        Egy adott asztalhoz tartozó ülőhelyek számának lekérdezése.

        Args:
            db: SQLAlchemy session
            table_id: Az asztal egyedi azonosítója

        Returns:
            int: Az asztalhoz tartozó ülőhelyek száma
        """
        return db.query(Seat).filter(Seat.table_id == table_id).count()

    @staticmethod
    def bulk_create_seats(
        db: Session,
        table_id: int,
        seat_count: int
    ) -> List[Seat]:
        """
        Több ülőhely egyidejű létrehozása egy asztalhoz.

        Args:
            db: SQLAlchemy session
            table_id: Az asztal egyedi azonosítója
            seat_count: Hány ülőhelyet hozzunk létre

        Returns:
            List[Seat]: A létrehozott ülőhelyek listája

        Raises:
            ValueError: Ha az asztal nem létezik vagy seat_count <= 0
        """
        # Ellenőrizzük, hogy létezik-e az asztal
        table_exists = db.query(Table).filter(Table.id == table_id).first()

        if not table_exists:
            raise ValueError(
                f"Az asztal (ID: {table_id}) nem található az adatbázisban."
            )

        if seat_count <= 0:
            raise ValueError("A seat_count értékének pozitívnak kell lennie.")

        # Létrehozzuk az ülőhelyeket
        seats = []
        for seat_num in range(1, seat_count + 1):
            seat = Seat(table_id=table_id, seat_number=seat_num)
            db.add(seat)
            seats.append(seat)

        try:
            db.commit()
            # Frissítjük az objektumokat
            for seat in seats:
                db.refresh(seat)
        except IntegrityError as e:
            db.rollback()
            raise ValueError(
                f"Hiba történt az ülőhelyek létrehozása során. "
                f"Lehetséges, hogy néhány székszám már létezik ennél az asztalnál."
            ) from e

        return seats


# Singleton példány exportálása
seat_service = SeatService()
