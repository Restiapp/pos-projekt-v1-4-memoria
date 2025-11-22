"""
Pydantic schemas for Reporting & Analytics entities.

This module defines the request and response schemas for reporting operations
in the Service Admin module, including sales reports, top products, and consumption.
"""

from datetime import date as DateType, datetime
from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Sales Report Schemas
# ============================================================================

class SalesByDateResponse(BaseModel):
    """Schema for daily sales breakdown."""

    date: DateType = Field(
        ...,
        description="Nap dátuma",
        examples=["2024-01-15"]
    )
    total_revenue: Decimal = Field(
        ...,
        description="Napi összbevétel",
        examples=[125000.00, 89500.50]
    )
    order_count: int = Field(
        ...,
        description="Rendelések száma",
        examples=[45, 32]
    )
    average_cart_value: Decimal = Field(
        ...,
        description="Átlagos kosárérték",
        examples=[2777.78, 2796.89]
    )
    cash_revenue: Decimal = Field(
        ...,
        description="Készpénzes bevétel",
        examples=[75000.00, 50000.00]
    )
    card_revenue: Decimal = Field(
        ...,
        description="Kártyás bevétel",
        examples=[50000.00, 39500.50]
    )
    cash_order_count: int = Field(
        ...,
        description="Készpénzes rendelések száma",
        examples=[25, 18]
    )
    card_order_count: int = Field(
        ...,
        description="Kártyás rendelések száma",
        examples=[20, 14]
    )


class SalesReportResponse(BaseModel):
    """Schema for sales report response."""

    start_date: DateType = Field(
        ...,
        description="Kezdő dátum",
        examples=["2024-01-01"]
    )
    end_date: DateType = Field(
        ...,
        description="Befejező dátum",
        examples=["2024-01-31"]
    )
    total_revenue: Decimal = Field(
        ...,
        description="Időszak összbevétele",
        examples=[3500000.00]
    )
    total_orders: int = Field(
        ...,
        description="Összes rendelés",
        examples=[1250]
    )
    average_cart_value: Decimal = Field(
        ...,
        description="Átlagos kosárérték",
        examples=[2800.00]
    )
    daily_breakdown: List[SalesByDateResponse] = Field(
        ...,
        description="Napi bontás"
    )
    payment_method_breakdown: dict = Field(
        ...,
        description="Fizetési mód szerinti bontás",
        examples=[{
            "CASH": {"revenue": 2000000.00, "order_count": 700},
            "CARD": {"revenue": 1500000.00, "order_count": 550}
        }]
    )


# ============================================================================
# Top Products Schemas
# ============================================================================

class TopProductResponse(BaseModel):
    """Schema for top product item."""

    product_id: int = Field(
        ...,
        description="Termék azonosító",
        examples=[1, 2, 3]
    )
    product_name: str = Field(
        ...,
        description="Termék neve",
        examples=["Pizza Margherita", "Coca-Cola 0.5L"]
    )
    total_quantity_sold: Decimal = Field(
        ...,
        description="Összes eladott mennyiség",
        examples=[450, 320]
    )
    total_revenue: Decimal = Field(
        ...,
        description="Összes bevétel a termékből",
        examples=[675000.00, 128000.00]
    )
    order_count: int = Field(
        ...,
        description="Hány rendelésben szerepelt",
        examples=[380, 280]
    )
    average_price: Decimal = Field(
        ...,
        description="Átlagos eladási ár",
        examples=[1500.00, 400.00]
    )


class TopProductsReportResponse(BaseModel):
    """Schema for top products report response."""

    limit: int = Field(
        ...,
        description="Kért toplista mérete",
        examples=[10, 20, 50]
    )
    start_date: Optional[DateType] = Field(
        None,
        description="Kezdő dátum (ha van)",
        examples=["2024-01-01"]
    )
    end_date: Optional[DateType] = Field(
        None,
        description="Befejező dátum (ha van)",
        examples=["2024-01-31"]
    )
    products: List[TopProductResponse] = Field(
        ...,
        description="Top termékek listája"
    )
    total_products_analyzed: int = Field(
        ...,
        description="Összes elemzett termék száma",
        examples=[156]
    )


# ============================================================================
# Consumption Report Schemas
# ============================================================================

class InventoryConsumptionItem(BaseModel):
    """Schema for inventory consumption item."""

    inventory_item_id: int = Field(
        ...,
        description="Készletcikk azonosító",
        examples=[1, 2, 3]
    )
    inventory_item_name: str = Field(
        ...,
        description="Készletcikk neve",
        examples=["Liszt", "Paradicsom", "Sajt"]
    )
    unit: str = Field(
        ...,
        description="Mértékegység",
        examples=["kg", "db", "l"]
    )
    opening_stock: Decimal = Field(
        ...,
        description="Nyitó készlet",
        examples=[100.00, 50.00]
    )
    current_stock: Decimal = Field(
        ...,
        description="Jelenlegi készlet",
        examples=[75.00, 25.00]
    )
    consumed_quantity: Decimal = Field(
        ...,
        description="Felhasznált mennyiség",
        examples=[25.00, 25.00]
    )
    consumption_percentage: Decimal = Field(
        ...,
        description="Fogyás százalékban",
        examples=[25.00, 50.00]
    )
    last_cost_per_unit: Optional[Decimal] = Field(
        None,
        description="Utolsó egységár",
        examples=[500.00, 300.00]
    )
    estimated_cost: Optional[Decimal] = Field(
        None,
        description="Becsült fogyás értéke",
        examples=[12500.00, 7500.00]
    )


class ConsumptionReportResponse(BaseModel):
    """Schema for consumption report response."""

    start_date: Optional[DateType] = Field(
        None,
        description="Kezdő dátum (ha van)",
        examples=["2024-01-01"]
    )
    end_date: Optional[DateType] = Field(
        None,
        description="Befejező dátum (ha van)",
        examples=["2024-01-31"]
    )
    report_generated_at: datetime = Field(
        ...,
        description="Riport generálás időpontja"
    )
    items: List[InventoryConsumptionItem] = Field(
        ...,
        description="Készletcikkek fogyása"
    )
    total_items: int = Field(
        ...,
        description="Összes készletcikk száma",
        examples=[45]
    )
    total_estimated_cost: Decimal = Field(
        ...,
        description="Összes becsült fogyás értéke",
        examples=[450000.00]
    )
    high_consumption_items: List[InventoryConsumptionItem] = Field(
        ...,
        description="Magas fogyású tételek (>50%)",
        examples=[]
    )
