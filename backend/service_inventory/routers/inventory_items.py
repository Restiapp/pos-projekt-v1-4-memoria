"""
Inventory Items Router - FastAPI Endpoints
Module 5: Készletkezelés - CRUD API

Ez a modul tartalmazza az InventoryItem entitáshoz tartozó CRUD végpontokat.
Használja az InventoryService-t az üzleti logika kezeléséhez.
"""

from typing import Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.service_inventory.models.database import get_db
from backend.service_inventory.services.inventory_service import InventoryService
from backend.service_inventory.schemas.inventory_item import (
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryItemResponse,
    InventoryItemListResponse
)

# Router instance
router = APIRouter(
    prefix="/inventory/items",
    tags=["Inventory Items"],
    responses={
        404: {"description": "Item not found"},
        400: {"description": "Bad request"},
    }
)


def get_inventory_service(db: Session = Depends(get_db)) -> InventoryService:
    """
    Dependency injection az InventoryService-hez.

    Args:
        db: SQLAlchemy Session (injected)

    Returns:
        InventoryService: Inicializált service instance
    """
    return InventoryService(db)


@router.get(
    "",
    response_model=InventoryItemListResponse,
    summary="List inventory items",
    description="Retrieve a paginated list of inventory items with optional name filtering"
)
def list_inventory_items(
    skip: int = Query(0, ge=0, description="Number of items to skip (offset)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of items to return"),
    name_filter: Optional[str] = Query(None, description="Filter items by name (partial match)"),
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Készletelemek listázása paginálással és szűréssel.

    **Query paraméterek:**
    - `skip`: Kihagyandó elemek száma (alapértelmezett: 0)
    - `limit`: Maximum visszaadott elemek (alapértelmezett: 20, max: 100)
    - `name_filter`: Név szerinti szűrés (opcionális, részleges egyezés)

    **Visszatérési érték:**
    - `items`: Készletelemek listája
    - `total`: Összes elem száma
    - `page`: Aktuális oldal szám
    - `page_size`: Oldal méret
    """
    return service.list_items(skip=skip, limit=limit, name_filter=name_filter)


@router.post(
    "",
    response_model=InventoryItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create inventory item",
    description="Create a new inventory item with initial stock and cost"
)
def create_inventory_item(
    item_data: InventoryItemCreate,
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Új készletelem létrehozása.

    **Request body:**
    - `name`: Készletelem neve (egyedi, kötelező)
    - `unit`: Mértékegység (pl. 'kg', 'liter', 'db')
    - `current_stock_perpetual`: Kezdő készlet mennyiség (alapértelmezett: 0.000)
    - `last_cost_per_unit`: Utolsó beszerzési egységár HUF-ban (opcionális)

    **Hibák:**
    - 400: Ha már létezik ilyen nevű elem
    """
    try:
        item = service.create_item(item_data)
        return InventoryItemResponse.model_validate(item)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{item_id}",
    response_model=InventoryItemResponse,
    summary="Get inventory item by ID",
    description="Retrieve a single inventory item by its unique identifier"
)
def get_inventory_item(
    item_id: int,
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Készletelem lekérdezése ID alapján.

    **Path paraméterek:**
    - `item_id`: A készletelem egyedi azonosítója

    **Hibák:**
    - 404: Ha nem található az elem
    """
    item = service.get_item(item_id)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory item with id {item_id} not found"
        )

    return InventoryItemResponse.model_validate(item)


@router.patch(
    "/{item_id}",
    response_model=InventoryItemResponse,
    summary="Update inventory item",
    description="Partially update an existing inventory item"
)
def update_inventory_item(
    item_id: int,
    item_data: InventoryItemUpdate,
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Készletelem frissítése (partial update).

    **Path paraméterek:**
    - `item_id`: A frissítendő elem azonosítója

    **Request body:** (minden mező opcionális)
    - `name`: Új név
    - `unit`: Új mértékegység
    - `current_stock_perpetual`: Új készlet mennyiség
    - `last_cost_per_unit`: Új egységár

    **Hibák:**
    - 404: Ha nem található az elem
    - 400: Ha a név módosítása ütközést okozna
    """
    try:
        item = service.update_item(item_id, item_data)

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inventory item with id {item_id} not found"
            )

        return InventoryItemResponse.model_validate(item)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete inventory item",
    description="Delete an inventory item by its ID"
)
def delete_inventory_item(
    item_id: int,
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Készletelem törlése.

    **Path paraméterek:**
    - `item_id`: A törlendő elem azonosítója

    **Hibák:**
    - 404: Ha nem található az elem
    """
    success = service.delete_item(item_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory item with id {item_id} not found"
        )

    return None


# ===== KIEGÉSZÍTŐ VÉGPONTOK =====

class StockUpdateRequest(BaseModel):
    """Schema for stock update operations."""
    quantity_change: Decimal = Field(
        ...,
        description="Quantity change (positive for increase, negative for decrease)",
        examples=[10.5, -5.0]
    )
    new_cost_per_unit: Optional[Decimal] = Field(
        None,
        ge=0,
        description="New cost per unit (optional, typically provided on purchase)",
        examples=[1500.00]
    )


from pydantic import BaseModel, Field


@router.post(
    "/{item_id}/stock",
    response_model=InventoryItemResponse,
    summary="Update item stock",
    description="Increase or decrease stock quantity with optional cost update"
)
def update_item_stock(
    item_id: int,
    stock_update: StockUpdateRequest,
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Készlet mennyiség módosítása (beszerzés vagy felhasználás).

    **Path paraméterek:**
    - `item_id`: A készletelem azonosítója

    **Request body:**
    - `quantity_change`: Mennyiség változás (+ növelés, - csökkentés)
    - `new_cost_per_unit`: Új egységár (opcionális, beszerzéskor)

    **Példák:**
    - Beszerzés: `{"quantity_change": 50.0, "new_cost_per_unit": 1200.00}`
    - Felhasználás: `{"quantity_change": -10.5}`

    **Hibák:**
    - 404: Ha nem található az elem
    - 400: Ha a készlet negatívba menne
    """
    try:
        item = service.update_stock(
            item_id=item_id,
            quantity_change=float(stock_update.quantity_change),
            new_cost_per_unit=float(stock_update.new_cost_per_unit) if stock_update.new_cost_per_unit else None
        )

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inventory item with id {item_id} not found"
            )

        return InventoryItemResponse.model_validate(item)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/reports/low-stock",
    response_model=list[InventoryItemResponse],
    summary="Get low stock items",
    description="Retrieve items with stock below the specified threshold"
)
def get_low_stock_items(
    threshold: float = Query(10.0, ge=0, description="Stock threshold level"),
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Alacsony készletű elemek lekérdezése.

    **Query paraméterek:**
    - `threshold`: Készlet küszöbérték (alapértelmezett: 10.0)

    **Visszatérési érték:**
    - Lista az alacsony készletű elemekről
    """
    items = service.get_low_stock_items(threshold=threshold)
    return [InventoryItemResponse.model_validate(item) for item in items]


class InventoryValueResponse(BaseModel):
    """Response schema for total inventory value."""
    total_value: Decimal = Field(
        ...,
        description="Total inventory value in HUF",
        examples=[1500000.00]
    )
    currency: str = Field(
        default="HUF",
        description="Currency code"
    )


@router.get(
    "/reports/total-value",
    response_model=InventoryValueResponse,
    summary="Get total inventory value",
    description="Calculate the total value of all inventory items"
)
def get_total_inventory_value(
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Teljes készlet értékének lekérdezése.

    **Visszatérési érték:**
    - `total_value`: Összesített készlet érték HUF-ban
    - `currency`: Pénznem kód (HUF)

    **Számítás:**
    - Minden elem: `current_stock_perpetual * last_cost_per_unit`
    - Összegzés: Összes elem értékének összege
    """
    total_value = service.get_total_inventory_value()
    return InventoryValueResponse(
        total_value=Decimal(str(total_value)),
        currency="HUF"
    )
