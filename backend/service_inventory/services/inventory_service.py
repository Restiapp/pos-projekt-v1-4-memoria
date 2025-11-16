"""
Inventory Service - Business Logic Layer
Module 5: Készletkezelés

Ez a modul tartalmazza az InventoryService osztályt, amely
a készletkezelési műveletek üzleti logikáját implementálja.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.service_inventory.models.inventory_item import InventoryItem
from backend.service_inventory.schemas.inventory_item import (
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryItemResponse,
    InventoryItemListResponse
)


class InventoryService:
    """
    Service osztály a készlet (inventory) kezeléséhez.

    Tartalmazza a CRUD műveleteket és az üzleti logikát
    a current_stock_perpetual (automatikus raktár) kezeléséhez.
    """

    def __init__(self, db: Session):
        """
        Inicializálja az InventoryService-t.

        Args:
            db: SQLAlchemy Session objektum
        """
        self.db = db

    def create_item(self, item_data: InventoryItemCreate) -> InventoryItem:
        """
        Új készletelem létrehozása.

        Args:
            item_data: InventoryItemCreate schema az új elem adataival

        Returns:
            InventoryItem: A létrehozott készletelem

        Raises:
            ValueError: Ha már létezik ilyen nevű elem
        """
        # Ellenőrizzük, hogy létezik-e már ilyen nevű elem
        existing_item = self.db.query(InventoryItem).filter(
            InventoryItem.name == item_data.name
        ).first()

        if existing_item:
            raise ValueError(f"Inventory item with name '{item_data.name}' already exists")

        # Új elem létrehozása
        db_item = InventoryItem(
            name=item_data.name,
            unit=item_data.unit,
            current_stock_perpetual=item_data.current_stock_perpetual,
            last_cost_per_unit=item_data.last_cost_per_unit
        )

        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)

        return db_item

    def get_item(self, item_id: int) -> Optional[InventoryItem]:
        """
        Készletelem lekérdezése ID alapján.

        Args:
            item_id: A keresett elem azonosítója

        Returns:
            Optional[InventoryItem]: A megtalált elem vagy None
        """
        return self.db.query(InventoryItem).filter(
            InventoryItem.id == item_id
        ).first()

    def get_item_by_name(self, name: str) -> Optional[InventoryItem]:
        """
        Készletelem lekérdezése név alapján.

        Args:
            name: A keresett elem neve

        Returns:
            Optional[InventoryItem]: A megtalált elem vagy None
        """
        return self.db.query(InventoryItem).filter(
            InventoryItem.name == name
        ).first()

    def list_items(
        self,
        skip: int = 0,
        limit: int = 100,
        name_filter: Optional[str] = None
    ) -> InventoryItemListResponse:
        """
        Készletelemek listázása paginálással és szűréssel.

        Args:
            skip: Kihagyandó elemek száma (offset)
            limit: Maximum visszaadott elemek száma
            name_filter: Opcionális név szűrő (részleges egyezés)

        Returns:
            InventoryItemListResponse: Paginált válasz az elemekkel
        """
        query = self.db.query(InventoryItem)

        # Név szűrés, ha van
        if name_filter:
            query = query.filter(
                InventoryItem.name.ilike(f"%{name_filter}%")
            )

        # Összes elem száma
        total = query.count()

        # Paginált elemek lekérdezése
        items = query.offset(skip).limit(limit).all()

        # Válasz összeállítása
        page = (skip // limit) + 1 if limit > 0 else 1

        return InventoryItemListResponse(
            items=[InventoryItemResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=limit
        )

    def update_item(
        self,
        item_id: int,
        item_data: InventoryItemUpdate
    ) -> Optional[InventoryItem]:
        """
        Készletelem frissítése.

        Args:
            item_id: A frissítendő elem azonosítója
            item_data: InventoryItemUpdate schema a frissítési adatokkal

        Returns:
            Optional[InventoryItem]: A frissített elem vagy None, ha nem található

        Raises:
            ValueError: Ha a név módosítása ütközést okozna
        """
        db_item = self.get_item(item_id)

        if not db_item:
            return None

        # Ellenőrizzük név ütközést, ha változik a név
        if item_data.name and item_data.name != db_item.name:
            existing_item = self.get_item_by_name(item_data.name)
            if existing_item:
                raise ValueError(f"Inventory item with name '{item_data.name}' already exists")

        # Frissítjük csak azokat a mezőket, amelyek meg vannak adva
        update_data = item_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_item, field, value)

        self.db.commit()
        self.db.refresh(db_item)

        return db_item

    def delete_item(self, item_id: int) -> bool:
        """
        Készletelem törlése.

        Args:
            item_id: A törlendő elem azonosítója

        Returns:
            bool: True, ha sikerült törölni, False ha nem található
        """
        db_item = self.get_item(item_id)

        if not db_item:
            return False

        self.db.delete(db_item)
        self.db.commit()

        return True

    def update_stock(
        self,
        item_id: int,
        quantity_change: float,
        new_cost_per_unit: Optional[float] = None
    ) -> Optional[InventoryItem]:
        """
        Készlet módosítása (növelés vagy csökkentés).

        Ez a speciális művelet lehetővé teszi a készlet perpetuális
        frissítését beszerzés vagy felhasználás esetén.

        Args:
            item_id: A készletelem azonosítója
            quantity_change: A mennyiség változása (+ növelés, - csökkentés)
            new_cost_per_unit: Új egységár, ha van (pl. beszerzéskor)

        Returns:
            Optional[InventoryItem]: A frissített elem vagy None

        Raises:
            ValueError: Ha a készlet negatívba menne
        """
        db_item = self.get_item(item_id)

        if not db_item:
            return None

        # Új készlet kiszámítása
        new_stock = float(db_item.current_stock_perpetual) + quantity_change

        # Ellenőrizzük, hogy nem megy-e negatívba
        if new_stock < 0:
            raise ValueError(
                f"Insufficient stock for item '{db_item.name}'. "
                f"Current: {db_item.current_stock_perpetual}, "
                f"Requested change: {quantity_change}"
            )

        # Frissítjük a készletet
        db_item.current_stock_perpetual = new_stock

        # Frissítjük az egységárat, ha van új
        if new_cost_per_unit is not None:
            db_item.last_cost_per_unit = new_cost_per_unit

        self.db.commit()
        self.db.refresh(db_item)

        return db_item

    def get_low_stock_items(
        self,
        threshold: float = 10.0
    ) -> List[InventoryItem]:
        """
        Alacsony készletű elemek lekérdezése.

        Args:
            threshold: A készlet küszöbérték

        Returns:
            List[InventoryItem]: Az alacsony készletű elemek listája
        """
        return self.db.query(InventoryItem).filter(
            InventoryItem.current_stock_perpetual <= threshold
        ).all()

    def get_total_inventory_value(self) -> float:
        """
        Teljes készlet értékének kiszámítása.

        Returns:
            float: A teljes készlet értéke (készlet * egységár összege)
        """
        items = self.db.query(InventoryItem).filter(
            InventoryItem.last_cost_per_unit.isnot(None)
        ).all()

        total_value = sum(
            float(item.current_stock_perpetual) * float(item.last_cost_per_unit)
            for item in items
        )

        return total_value
