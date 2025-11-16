"""
Table Service - Business Logic Layer
Module 1: Rendeléskezelés és Asztalok

Ez a modul kezeli az asztalokkal kapcsolatos üzleti logikát.
CRUD műveletek és validációs logika az asztalokhoz.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.service_orders.models.table import Table
from backend.service_orders.schemas.table import TableCreate, TableUpdate


class TableService:
    """
    Service osztály az asztalok kezeléséhez.

    Támogatott műveletek:
    - Új asztal létrehozása
    - Asztal lekérdezése ID alapján
    - Asztal lekérdezése asztalszám alapján
    - Összes asztal listázása (pagináció támogatással)
    - Asztal frissítése
    - Asztal törlése
    """

    @staticmethod
    def create_table(db: Session, table_data: TableCreate) -> Table:
        """
        Új asztal létrehozása az adatbázisban.

        Args:
            db: SQLAlchemy session
            table_data: TableCreate schema az új asztal adataival

        Returns:
            Table: A létrehozott asztal objektum

        Raises:
            IntegrityError: Ha a table_number már létezik
        """
        db_table = Table(
            table_number=table_data.table_number,
            position_x=table_data.position_x,
            position_y=table_data.position_y,
            capacity=table_data.capacity
        )

        db.add(db_table)
        try:
            db.commit()
            db.refresh(db_table)
        except IntegrityError as e:
            db.rollback()
            raise ValueError(
                f"Asztal '{table_data.table_number}' már létezik az adatbázisban."
            ) from e

        return db_table

    @staticmethod
    def get_table(db: Session, table_id: int) -> Optional[Table]:
        """
        Asztal lekérdezése ID alapján.

        Args:
            db: SQLAlchemy session
            table_id: Az asztal egyedi azonosítója

        Returns:
            Table | None: Az asztal objektum vagy None, ha nem található
        """
        return db.query(Table).filter(Table.id == table_id).first()

    @staticmethod
    def get_table_by_number(db: Session, table_number: str) -> Optional[Table]:
        """
        Asztal lekérdezése asztalszám alapján.

        Args:
            db: SQLAlchemy session
            table_number: Az asztal száma/azonosítója

        Returns:
            Table | None: Az asztal objektum vagy None, ha nem található
        """
        return db.query(Table).filter(Table.table_number == table_number).first()

    @staticmethod
    def list_tables(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Table], int]:
        """
        Összes asztal listázása pagináció támogatással.

        Args:
            db: SQLAlchemy session
            skip: Hány rekordot ugorjunk át (offset)
            limit: Maximum hány rekordot adjunk vissza (page size)

        Returns:
            tuple: (asztalok listája, összes asztal száma)
        """
        # Összes asztal számának lekérdezése
        total = db.query(Table).count()

        # Paginált lista lekérdezése
        tables = db.query(Table).offset(skip).limit(limit).all()

        return tables, total

    @staticmethod
    def update_table(
        db: Session,
        table_id: int,
        table_data: TableUpdate
    ) -> Optional[Table]:
        """
        Meglévő asztal adatainak frissítése.

        Args:
            db: SQLAlchemy session
            table_id: Az asztal egyedi azonosítója
            table_data: TableUpdate schema a frissítendő mezőkkel

        Returns:
            Table | None: A frissített asztal objektum vagy None, ha nem található

        Raises:
            IntegrityError: Ha a table_number módosítása ütközést okoz
        """
        db_table = db.query(Table).filter(Table.id == table_id).first()

        if not db_table:
            return None

        # Csak azokat a mezőket frissítjük, amelyek nem None értékűek
        update_data = table_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_table, field, value)

        try:
            db.commit()
            db.refresh(db_table)
        except IntegrityError as e:
            db.rollback()
            raise ValueError(
                f"Nem sikerült frissíteni az asztalt. Lehetséges ok: "
                f"az asztalszám '{table_data.table_number}' már használatban van."
            ) from e

        return db_table

    @staticmethod
    def delete_table(db: Session, table_id: int) -> bool:
        """
        Asztal törlése az adatbázisból.

        Args:
            db: SQLAlchemy session
            table_id: A törlendő asztal egyedi azonosítója

        Returns:
            bool: True ha sikeres volt a törlés, False ha nem található az asztal

        Note:
            A cascade="all, delete-orphan" miatt az asztalhoz tartozó ülőhelyek
            automatikusan törlődnek.
        """
        db_table = db.query(Table).filter(Table.id == table_id).first()

        if not db_table:
            return False

        db.delete(db_table)
        db.commit()

        return True

    @staticmethod
    def count_tables(db: Session) -> int:
        """
        Összes asztal számának lekérdezése.

        Args:
            db: SQLAlchemy session

        Returns:
            int: Az asztalok száma
        """
        return db.query(Table).count()

    @staticmethod
    def get_tables_with_capacity(
        db: Session,
        min_capacity: int
    ) -> List[Table]:
        """
        Asztalok lekérdezése minimum kapacitás alapján.

        Args:
            db: SQLAlchemy session
            min_capacity: Minimum ülőhely kapacitás

        Returns:
            List[Table]: Asztalok listája, amelyek kapacitása >= min_capacity
        """
        return db.query(Table).filter(
            Table.capacity >= min_capacity
        ).all()


# Singleton példány exportálása
table_service = TableService()
