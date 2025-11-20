"""
Pydantic schemas for Reports/Analytics endpoints.

This module defines the request and response schemas for reporting and analytics
operations in the Service Admin module, including sales reports, product analytics,
and inventory consumption tracking.
"""

from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Sales Report Schemas
# ============================================================================

class DailySalesData(BaseModel):
    """Schema for daily sales breakdown."""

    model_config = ConfigDict(from_attributes=True)

    date: date = Field(
        ...,
        description="Nap dátuma",
        examples=["2024-01-15", "2024-02-20"]
    )
    total_revenue: Decimal = Field(
        ...,
        description="Összesített bevétel (Ft)",
        examples=[150000.00, 250000.50]
    )
    cash_revenue: Decimal = Field(
        ...,
        description="Készpénzes bevétel (Ft)",
        examples=[80000.00, 120000.00]
    )
    card_revenue: Decimal = Field(
        ...,
        description="Kártyás bevétel (Ft)",
        examples=[70000.00, 130000.50]
    )
    order_count: int = Field(
        ...,
        description="Rendelések száma",
        examples=[45, 78, 120]
    )
    average_order_value: Decimal = Field(
        ...,
        description="Átlagos rendelés érték (Ft)",
        examples=[3333.33, 4500.00]
    )


class SalesReportResponse(BaseModel):
    """Schema for sales report response."""

    model_config = ConfigDict(from_attributes=True)

    sales_data: List[DailySalesData] = Field(
        ...,
        description="Napi bontású értékesítési adatok"
    )
    total_revenue: Decimal = Field(
        ...,
        description="Teljes bevétel az időszakban (Ft)",
        examples=[1500000.00, 3500000.50]
    )
    total_orders: int = Field(
        ...,
        description="Összes rendelés az időszakban",
        examples=[450, 890]
    )
    average_daily_revenue: Decimal = Field(
        ...,
        description="Átlagos napi bevétel (Ft)",
        examples=[150000.00, 250000.00]
    )


# ============================================================================
# Top Products Schemas
# ============================================================================

class TopProductData(BaseModel):
    """Schema for top product data."""

    model_config = ConfigDict(from_attributes=True)

    product_id: int = Field(
        ...,
        description="Termék azonosító",
        examples=[1, 2, 3]
    )
    product_name: str = Field(
        ...,
        description="Termék neve",
        examples=["Pizza Margherita", "Coca-Cola 0.5L", "Tiramisu"]
    )
    quantity_sold: int = Field(
        ...,
        description="Eladott mennyiség (db)",
        examples=[120, 85, 45]
    )
    total_revenue: Decimal = Field(
        ...,
        description="Összes bevétel ebből a termékből (Ft)",
        examples=[180000.00, 42500.00]
    )
    average_price: Decimal = Field(
        ...,
        description="Átlagos eladási ár (Ft)",
        examples=[1500.00, 500.00]
    )
    category_name: Optional[str] = Field(
        None,
        description="Kategória neve",
        examples=["Pizza", "Italok", "Desszertek"]
    )


class TopProductsResponse(BaseModel):
    """Schema for top products report response."""

    model_config = ConfigDict(from_attributes=True)

    products: List[TopProductData] = Field(
        ...,
        description="Top termékek listája"
    )
    total_products_analyzed: int = Field(
        ...,
        description="Összes elemzett termék száma",
        examples=[45, 120]
    )


# ============================================================================
# Consumption/Inventory Schemas
# ============================================================================

class InventoryConsumptionData(BaseModel):
    """Schema for inventory consumption data."""

    model_config = ConfigDict(from_attributes=True)

    ingredient_id: int = Field(
        ...,
        description="Alapanyag/készletcikk azonosító",
        examples=[1, 2, 3]
    )
    ingredient_name: str = Field(
        ...,
        description="Alapanyag neve",
        examples=["Liszt", "Sajt", "Paradicsom"]
    )
    quantity_consumed: Decimal = Field(
        ...,
        description="Fogyott mennyiség",
        examples=[15.5, 8.3, 25.0]
    )
    unit: str = Field(
        ...,
        description="Mennyiségi egység",
        examples=["kg", "liter", "db"]
    )
    estimated_cost: Optional[Decimal] = Field(
        None,
        description="Becsült költség (Ft)",
        examples=[12000.00, 5500.00]
    )


class ConsumptionReportResponse(BaseModel):
    """Schema for inventory consumption report response."""

    model_config = ConfigDict(from_attributes=True)

    consumption_data: List[InventoryConsumptionData] = Field(
        ...,
        description="Készletfogyási adatok"
    )
    total_items: int = Field(
        ...,
        description="Összes fogyó tétel száma",
        examples=[15, 30]
    )
    total_estimated_cost: Optional[Decimal] = Field(
        None,
        description="Összes becsült költség (Ft)",
        examples=[150000.00, 250000.00]
    )


# ============================================================================
# Common Query Parameters (not Pydantic, for documentation)
# ============================================================================

# These would be used as query parameters in FastAPI endpoints:
# - start_date: Optional[date] = Query(None, description="Kezdő dátum")
# - end_date: Optional[date] = Query(None, description="Záró dátum")
# - limit: int = Query(10, ge=1, le=100, description="Eredmények száma")
# - group_by: str = Query("day", description="Csoportosítás: day/week/month")
