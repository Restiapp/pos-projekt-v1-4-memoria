"""
Channel API Routes
Module 0: Terméktörzs és Menü

Ez a modul tartalmazza az értékesítési csatornákhoz kapcsolódó FastAPI végpontokat.
Implementálja a csatorna láthatóság beállítását és a csatorna-specifikus árkezelést.
"""

from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from backend.service_menu.database import get_db_connection
from backend.service_menu.services.channel_service import ChannelService
from backend.service_menu.schemas.product import (
    ChannelVisibilityResponse
)
from pydantic import BaseModel, Field


# Router létrehozása
router = APIRouter(
    prefix="/products",
    tags=["channels"]
)


def get_channel_service() -> ChannelService:
    """
    Dependency function a ChannelService injektálásához.

    Returns:
        ChannelService: Channel service instance
    """
    return ChannelService()


# Request schema for setting channel visibility
class SetChannelVisibilityRequest(BaseModel):
    """Schema for setting channel visibility."""

    channel_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Sales channel name",
        examples=["Pult", "Kiszállítás", "Helybeni"]
    )
    is_visible: bool = Field(
        True,
        description="Whether the product is visible on this channel",
        examples=[True, False]
    )
    price_override: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Channel-specific price override (if different from base_price)",
        examples=[1500.00, None]
    )


# Response schema for channel price
class ChannelPriceResponse(BaseModel):
    """Schema for channel price response."""

    product_id: int = Field(
        ...,
        description="Product identifier",
        examples=[1, 42]
    )
    channel_name: str = Field(
        ...,
        description="Sales channel name",
        examples=["Pult", "Kiszállítás", "Helybeni"]
    )
    price: Optional[Decimal] = Field(
        None,
        description="Product price on this channel (None if not visible)",
        examples=[1290.00, 1500.00, None]
    )
    is_visible: bool = Field(
        ...,
        description="Whether the product is visible on this channel",
        examples=[True, False]
    )


@router.post(
    "/{product_id}/channels",
    response_model=ChannelVisibilityResponse,
    status_code=status.HTTP_200_OK,
    summary="Set channel visibility for product",
    description="""
    Set or update the visibility and pricing for a product on a specific sales channel.

    This endpoint allows you to:
    - Enable or disable product visibility on a specific channel
    - Set channel-specific pricing (price override)
    - Update existing channel settings

    **Sales Channels:**
    Common channel names include:
    - `Pult` - Counter/POS sales
    - `Kiszállítás` - Delivery
    - `Helybeni` - Dine-in

    **Path Parameters:**
    - `product_id`: Unique product identifier (integer)

    **Request Body:**
    - `channel_name`: Name of the sales channel (required)
    - `is_visible`: Whether product is visible on this channel (default: true)
    - `price_override`: Optional channel-specific price (if different from base_price)

    **Returns:**
    - 200: Channel visibility settings updated successfully
    - 404: Product not found
    - 400: Invalid input data
    """
)
def set_channel_visibility(
    product_id: int,
    request: SetChannelVisibilityRequest,
    db: Session = Depends(get_db_connection),
    service: ChannelService = Depends(get_channel_service)
):
    """
    Csatorna láthatóság beállítása egy termékhez.

    Args:
        product_id: Product unique identifier
        request: SetChannelVisibilityRequest with channel settings
        db: Database session (injected)
        service: ChannelService instance (injected)

    Returns:
        ChannelVisibilityResponse: Channel visibility settings

    Raises:
        HTTPException 404: If product not found
        HTTPException 400: If validation fails
    """
    try:
        channel_visibility = service.set_channel_visibility(
            db=db,
            product_id=product_id,
            channel_name=request.channel_name,
            is_visible=request.is_visible,
            price_override=request.price_override
        )
        return channel_visibility
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while setting channel visibility: {str(e)}"
        )


@router.get(
    "/{product_id}/channels/{channel_name}/price",
    response_model=ChannelPriceResponse,
    summary="Get product price for channel",
    description="""
    Retrieve the price for a product on a specific sales channel.

    This endpoint returns:
    - The channel-specific price if a price override is set
    - The base product price if no override exists
    - `null` price if the product is not visible on the channel

    **Path Parameters:**
    - `product_id`: Unique product identifier (integer)
    - `channel_name`: Name of the sales channel (e.g., 'Pult', 'Kiszállítás', 'Helybeni')

    **Returns:**
    - 200: Product price information for the channel
    - 404: Product not found

    **Example Response:**
    ```json
    {
        "product_id": 1,
        "channel_name": "Kiszállítás",
        "price": 1500.00,
        "is_visible": true
    }
    ```

    If product is not visible:
    ```json
    {
        "product_id": 1,
        "channel_name": "Pult",
        "price": null,
        "is_visible": false
    }
    ```
    """
)
def get_product_price_for_channel(
    product_id: int,
    channel_name: str,
    db: Session = Depends(get_db_connection),
    service: ChannelService = Depends(get_channel_service)
):
    """
    Termék árának lekérdezése egy adott csatornán.

    Args:
        product_id: Product unique identifier
        channel_name: Sales channel name
        db: Database session (injected)
        service: ChannelService instance (injected)

    Returns:
        ChannelPriceResponse: Product price information for the channel

    Raises:
        HTTPException 404: If product not found
    """
    try:
        price = service.get_product_price_for_channel(
            db=db,
            product_id=product_id,
            channel_name=channel_name
        )

        # Determine visibility based on price (None means not visible)
        is_visible = price is not None

        return ChannelPriceResponse(
            product_id=product_id,
            channel_name=channel_name,
            price=price,
            is_visible=is_visible
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving channel price: {str(e)}"
        )
