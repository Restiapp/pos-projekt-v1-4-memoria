"""
Daily Inventory Service - Business Logic Layer
Module 5: Készletkezelés

Ez a service layer felelős a napi leltárívek (DailyInventorySheet)
és napi leltárszámlálások (DailyInventoryCount) üzleti logikájáért.

Kiemelt funkció: a counts JSONB mező kezelése
(List[CountItem] <-> Dict[str, Decimal] konverzió).
"""

from decimal import Decimal
from typing import Optional, List, Dict
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from backend.service_inventory.models.daily_inventory_sheet import (
    DailyInventorySheet,
    DailyInventoryCount
)
from backend.service_inventory.models.inventory_item import InventoryItem
from backend.service_inventory.schemas.daily_inventory import (
    DailyInventorySheetCreate,
    DailyInventorySheetUpdate,
    DailyInventorySheetResponse,
    DailyInventorySheetDetailResponse,
    DailyInventorySheetListResponse,
    DailyInventoryCountCreate,
    DailyInventoryCountUpdate,
    DailyInventoryCountResponse,
    DailyInventoryCountDetailResponse,
    DailyInventoryCountListResponse,
    CountItem
)


class DailyInventoryService:
    """
    Daily Inventory kezelő szolgáltatás.

    Felelősségek:
    - Leltárívek (sheets/sablonok) létrehozása, módosítása, törlése, lekérdezése
    - Leltárszámlálások (counts) létrehozása, módosítása, törlése, lekérdezése
    - JSONB counts mező kezelése (konverzió a Pydantic schemák és DB között)
    - Adatvalidáció és üzleti logika végrehajtása
    """

    # ===== DailyInventorySheet CRUD Operations =====

    @staticmethod
    def create_sheet(
        db: Session,
        sheet_data: DailyInventorySheetCreate
    ) -> DailyInventorySheetDetailResponse:
        """
        Új leltárív (sablon) létrehozása.

        Args:
            db: Database session
            sheet_data: Leltárív adatok (DailyInventorySheetCreate schema)

        Returns:
            DailyInventorySheetDetailResponse: Létrehozott leltárív

        Raises:
            HTTPException:
                - 400 ha már létezik ilyen nevű leltárív
                - 404 ha valamelyik inventory_item_id nem létezik
        """
        # Ellenőrizzük, hogy nincs-e már ilyen nevű leltárív
        existing = db.query(DailyInventorySheet).filter(
            DailyInventorySheet.name == sheet_data.name
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Daily inventory sheet with name '{sheet_data.name}' already exists"
            )

        # Új leltárív létrehozása
        db_sheet = DailyInventorySheet(name=sheet_data.name)

        # Inventory itemek hozzáadása (ha vannak)
        if sheet_data.inventory_item_ids:
            for item_id in sheet_data.inventory_item_ids:
                item = db.query(InventoryItem).filter(
                    InventoryItem.id == item_id
                ).first()

                if not item:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Inventory item with id {item_id} not found"
                    )

                db_sheet.inventory_items.append(item)

        try:
            db.add(db_sheet)
            db.commit()
            db.refresh(db_sheet)
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database integrity error: {str(e)}"
            )

        # Response összeállítása
        return DailyInventorySheetDetailResponse(
            id=db_sheet.id,
            name=db_sheet.name,
            created_at=db_sheet.created_at,
            inventory_item_ids=[item.id for item in db_sheet.inventory_items]
        )

    @staticmethod
    def get_sheet(
        db: Session,
        sheet_id: int,
        include_items: bool = False
    ) -> DailyInventorySheetDetailResponse:
        """
        Leltárív lekérdezése ID alapján.

        Args:
            db: Database session
            sheet_id: Leltárív azonosító
            include_items: Ha True, tartalmazza az inventory item ID-kat

        Returns:
            DailyInventorySheetDetailResponse: Leltárív adatok

        Raises:
            HTTPException: 404 ha a leltárív nem található
        """
        sheet = db.query(DailyInventorySheet).filter(
            DailyInventorySheet.id == sheet_id
        ).first()

        if not sheet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Daily inventory sheet with id {sheet_id} not found"
            )

        return DailyInventorySheetDetailResponse(
            id=sheet.id,
            name=sheet.name,
            created_at=sheet.created_at,
            inventory_item_ids=[item.id for item in sheet.inventory_items] if include_items else None
        )

    @staticmethod
    def get_sheets(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> DailyInventorySheetListResponse:
        """
        Leltárívek listázása lapozással.

        Args:
            db: Database session
            skip: Kihagyott elemek száma (pagination offset)
            limit: Max visszaadott elemek száma (pagination limit)

        Returns:
            DailyInventorySheetListResponse: Leltárív lista lapozási információkkal
        """
        query = db.query(DailyInventorySheet)

        # Összes elem száma
        total = query.count()

        # Lapozás
        sheets = query.offset(skip).limit(limit).all()

        # Response összeállítása
        return DailyInventorySheetListResponse(
            items=[DailyInventorySheetResponse.model_validate(sheet) for sheet in sheets],
            total=total,
            page=(skip // limit) + 1 if limit > 0 else 1,
            page_size=limit
        )

    @staticmethod
    def update_sheet(
        db: Session,
        sheet_id: int,
        sheet_data: DailyInventorySheetUpdate
    ) -> DailyInventorySheetDetailResponse:
        """
        Leltárív módosítása.

        Args:
            db: Database session
            sheet_id: Leltárív azonosító
            sheet_data: Módosítandó adatok (DailyInventorySheetUpdate schema)

        Returns:
            DailyInventorySheetDetailResponse: Módosított leltárív

        Raises:
            HTTPException:
                - 404 ha a leltárív nem található
                - 400 ha a név már foglalt
                - 404 ha valamelyik inventory_item_id nem létezik
        """
        # Leltárív lekérdezése
        sheet = db.query(DailyInventorySheet).filter(
            DailyInventorySheet.id == sheet_id
        ).first()

        if not sheet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Daily inventory sheet with id {sheet_id} not found"
            )

        # Csak azokat a mezőket frissítjük, amelyek meg vannak adva
        update_data = sheet_data.model_dump(exclude_unset=True)

        # Ellenőrizzük a név egyediségét (ha változik)
        if 'name' in update_data:
            new_name = update_data['name']
            existing = db.query(DailyInventorySheet).filter(
                DailyInventorySheet.name == new_name,
                DailyInventorySheet.id != sheet_id
            ).first()

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Daily inventory sheet with name '{new_name}' already exists"
                )

            sheet.name = new_name

        # Inventory itemek frissítése (ha van megadva)
        if 'inventory_item_ids' in update_data:
            item_ids = update_data['inventory_item_ids']

            # Töröljük a meglévő kapcsolatokat
            sheet.inventory_items.clear()

            # Hozzáadjuk az új itemeket
            if item_ids:
                for item_id in item_ids:
                    item = db.query(InventoryItem).filter(
                        InventoryItem.id == item_id
                    ).first()

                    if not item:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Inventory item with id {item_id} not found"
                        )

                    sheet.inventory_items.append(item)

        try:
            db.commit()
            db.refresh(sheet)
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database integrity error: {str(e)}"
            )

        return DailyInventorySheetDetailResponse(
            id=sheet.id,
            name=sheet.name,
            created_at=sheet.created_at,
            inventory_item_ids=[item.id for item in sheet.inventory_items]
        )

    @staticmethod
    def delete_sheet(
        db: Session,
        sheet_id: int,
        force: bool = False
    ) -> dict:
        """
        Leltárív törlése.

        Args:
            db: Database session
            sheet_id: Leltárív azonosító
            force: Ha True, akkor a kapcsolódó count rekordokat is törli (cascade)

        Returns:
            dict: Törlés megerősítése

        Raises:
            HTTPException:
                - 404 ha a leltárív nem található
                - 400 ha vannak kapcsolódó count rekordok és force=False
        """
        sheet = db.query(DailyInventorySheet).filter(
            DailyInventorySheet.id == sheet_id
        ).first()

        if not sheet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Daily inventory sheet with id {sheet_id} not found"
            )

        # Ellenőrizzük, hogy vannak-e kapcsolódó count rekordok
        counts_count = db.query(DailyInventoryCount).filter(
            DailyInventoryCount.sheet_id == sheet_id
        ).count()

        if counts_count > 0 and not force:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Sheet has {counts_count} associated counts. Use force=True to delete."
            )

        # Ha force=True, a cascade törli a count rekordokat (lásd model relationship)
        try:
            db.delete(sheet)
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete sheet: {str(e)}"
            )

        return {
            "message": f"Daily inventory sheet {sheet_id} deleted successfully",
            "deleted_id": sheet_id
        }

    # ===== DailyInventoryCount CRUD Operations =====

    @staticmethod
    def _convert_count_items_to_jsonb(count_items: List[CountItem]) -> Dict[str, Decimal]:
        """
        Konvertálja a CountItem listát JSONB-nek megfelelő dict-é.

        Args:
            count_items: Lista a számlált itemekről

        Returns:
            Dict[str, Decimal]: {'item_id': quantity, ...} formátum
        """
        counts_dict = {}
        for item in count_items:
            counts_dict[str(item.inventory_item_id)] = item.counted_quantity
        return counts_dict

    @staticmethod
    def _convert_jsonb_to_count_items(counts_dict: Dict[str, Decimal]) -> List[CountItem]:
        """
        Konvertálja a JSONB dict-et CountItem listává.

        Args:
            counts_dict: {'item_id': quantity, ...} formátum

        Returns:
            List[CountItem]: Lista a számlált itemekről
        """
        count_items = []
        for item_id_str, quantity in counts_dict.items():
            count_items.append(CountItem(
                inventory_item_id=int(item_id_str),
                counted_quantity=quantity
            ))
        return count_items

    @staticmethod
    def create_count(
        db: Session,
        count_data: DailyInventoryCountCreate
    ) -> DailyInventoryCountDetailResponse:
        """
        Új leltárszámlálás létrehozása.

        Args:
            db: Database session
            count_data: Leltárszámlálás adatok (DailyInventoryCountCreate schema)

        Returns:
            DailyInventoryCountDetailResponse: Létrehozott leltárszámlálás

        Raises:
            HTTPException:
                - 404 ha a sheet_id nem létezik
        """
        # Ellenőrizzük, hogy a sheet létezik-e
        sheet = db.query(DailyInventorySheet).filter(
            DailyInventorySheet.id == count_data.sheet_id
        ).first()

        if not sheet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Daily inventory sheet with id {count_data.sheet_id} not found"
            )

        # Konvertáljuk a count_items-t JSONB formátumra
        counts_dict = DailyInventoryService._convert_count_items_to_jsonb(
            count_data.count_items
        )

        # Új leltárszámlálás létrehozása
        db_count = DailyInventoryCount(
            sheet_id=count_data.sheet_id,
            count_date=count_data.count_date,
            employee_id=count_data.employee_id,
            counts=counts_dict
        )

        try:
            db.add(db_count)
            db.commit()
            db.refresh(db_count)
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database integrity error: {str(e)}"
            )

        # Response összeállítása
        return DailyInventoryCountDetailResponse(
            id=db_count.id,
            sheet_id=db_count.sheet_id,
            count_date=db_count.count_date,
            employee_id=db_count.employee_id,
            counts=db_count.counts,
            created_at=db_count.created_at,
            count_items_detail=count_data.count_items
        )

    @staticmethod
    def get_count(
        db: Session,
        count_id: int,
        include_detail: bool = False
    ) -> DailyInventoryCountDetailResponse:
        """
        Leltárszámlálás lekérdezése ID alapján.

        Args:
            db: Database session
            count_id: Leltárszámlálás azonosító
            include_detail: Ha True, count_items_detail is tartalmazza

        Returns:
            DailyInventoryCountDetailResponse: Leltárszámlálás adatok

        Raises:
            HTTPException: 404 ha a leltárszámlálás nem található
        """
        count = db.query(DailyInventoryCount).filter(
            DailyInventoryCount.id == count_id
        ).first()

        if not count:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Daily inventory count with id {count_id} not found"
            )

        count_items_detail = None
        if include_detail and count.counts:
            count_items_detail = DailyInventoryService._convert_jsonb_to_count_items(
                count.counts
            )

        return DailyInventoryCountDetailResponse(
            id=count.id,
            sheet_id=count.sheet_id,
            count_date=count.count_date,
            employee_id=count.employee_id,
            counts=count.counts,
            created_at=count.created_at,
            count_items_detail=count_items_detail
        )

    @staticmethod
    def get_counts(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        sheet_id: Optional[int] = None,
        count_date: Optional[date] = None
    ) -> DailyInventoryCountListResponse:
        """
        Leltárszámlálások listázása lapozással és szűréssel.

        Args:
            db: Database session
            skip: Kihagyott elemek száma (pagination offset)
            limit: Max visszaadott elemek száma (pagination limit)
            sheet_id: Szűrés sheet_id alapján
            count_date: Szűrés dátum alapján

        Returns:
            DailyInventoryCountListResponse: Leltárszámlálás lista lapozási információkkal
        """
        query = db.query(DailyInventoryCount)

        # Szűrés sheet_id alapján
        if sheet_id is not None:
            query = query.filter(DailyInventoryCount.sheet_id == sheet_id)

        # Szűrés dátum alapján
        if count_date is not None:
            query = query.filter(DailyInventoryCount.count_date == count_date)

        # Rendezés dátum szerint (legújabb először)
        query = query.order_by(DailyInventoryCount.count_date.desc())

        # Összes elem száma a szűrés után
        total = query.count()

        # Lapozás
        counts = query.offset(skip).limit(limit).all()

        # Response összeállítása
        return DailyInventoryCountListResponse(
            items=[DailyInventoryCountResponse.model_validate(count) for count in counts],
            total=total,
            page=(skip // limit) + 1 if limit > 0 else 1,
            page_size=limit
        )

    @staticmethod
    def update_count(
        db: Session,
        count_id: int,
        count_data: DailyInventoryCountUpdate
    ) -> DailyInventoryCountDetailResponse:
        """
        Leltárszámlálás módosítása.

        Args:
            db: Database session
            count_id: Leltárszámlálás azonosító
            count_data: Módosítandó adatok (DailyInventoryCountUpdate schema)

        Returns:
            DailyInventoryCountDetailResponse: Módosított leltárszámlálás

        Raises:
            HTTPException:
                - 404 ha a leltárszámlálás nem található
                - 404 ha az új sheet_id nem létezik
        """
        # Leltárszámlálás lekérdezése
        count = db.query(DailyInventoryCount).filter(
            DailyInventoryCount.id == count_id
        ).first()

        if not count:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Daily inventory count with id {count_id} not found"
            )

        # Csak azokat a mezőket frissítjük, amelyek meg vannak adva
        update_data = count_data.model_dump(exclude_unset=True)

        # Ellenőrizzük a sheet_id-t (ha változik)
        if 'sheet_id' in update_data:
            new_sheet_id = update_data['sheet_id']
            sheet = db.query(DailyInventorySheet).filter(
                DailyInventorySheet.id == new_sheet_id
            ).first()

            if not sheet:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Daily inventory sheet with id {new_sheet_id} not found"
                )

            count.sheet_id = new_sheet_id

        # Egyszerű mezők frissítése
        if 'count_date' in update_data:
            count.count_date = update_data['count_date']

        if 'employee_id' in update_data:
            count.employee_id = update_data['employee_id']

        # Count items frissítése (ha van megadva)
        if 'count_items' in update_data:
            count_items = update_data['count_items']
            if count_items:
                counts_dict = DailyInventoryService._convert_count_items_to_jsonb(
                    count_items
                )
                count.counts = counts_dict

        try:
            db.commit()
            db.refresh(count)
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database integrity error: {str(e)}"
            )

        # Response összeállítása
        count_items_detail = None
        if count.counts:
            count_items_detail = DailyInventoryService._convert_jsonb_to_count_items(
                count.counts
            )

        return DailyInventoryCountDetailResponse(
            id=count.id,
            sheet_id=count.sheet_id,
            count_date=count.count_date,
            employee_id=count.employee_id,
            counts=count.counts,
            created_at=count.created_at,
            count_items_detail=count_items_detail
        )

    @staticmethod
    def delete_count(
        db: Session,
        count_id: int
    ) -> dict:
        """
        Leltárszámlálás törlése.

        Args:
            db: Database session
            count_id: Leltárszámlálás azonosító

        Returns:
            dict: Törlés megerősítése

        Raises:
            HTTPException: 404 ha a leltárszámlálás nem található
        """
        count = db.query(DailyInventoryCount).filter(
            DailyInventoryCount.id == count_id
        ).first()

        if not count:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Daily inventory count with id {count_id} not found"
            )

        try:
            db.delete(count)
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete count: {str(e)}"
            )

        return {
            "message": f"Daily inventory count {count_id} deleted successfully",
            "deleted_id": count_id
        }
