"""
ReportsService - Riportok és Analitika (Reports & Analytics)

Ez a service felelős a dashboard analitikai adatainak előállításáért:
- Értékesítési statisztikák (napi bontás, bevételi adatok)
- Top termékek elemzése
- Készletfogyási riportok

A service kommunikál más mikroszolgáltatásokkal (orders, menu, inventory)
a szükséges adatok összegyűjtéséhez.
"""

import httpx
import logging
from typing import List, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from backend.service_admin.config import settings
from backend.service_admin.schemas.reports import (
    SalesReportResponse,
    DailySalesData,
    TopProductsResponse,
    TopProductData,
    ConsumptionReportResponse,
    InventoryConsumptionData
)

logger = logging.getLogger(__name__)


class ReportsService:
    """
    Service osztály a riportok és analitikai adatok kezeléséhez.

    Felelősségek:
    - Értékesítési riportok generálása
    - Top termékek elemzése
    - Készletfogyási riportok
    - Mikroszolgáltatások közötti adatkommunikáció
    """

    def __init__(self, db: Session):
        """
        Inicializálja a ReportsService-t.

        Args:
            db: SQLAlchemy Session objektum dependency injectionből
        """
        self.db = db
        self.orders_service_url = settings.orders_service_url
        self.menu_service_url = settings.menu_service_url
        self.inventory_service_url = settings.inventory_service_url

    # ========================================================================
    # Sales Report Methods
    # ========================================================================

    async def get_sales_report(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> SalesReportResponse:
        """
        Értékesítési riport lekérése napi bontásban.

        Args:
            start_date: Kezdő dátum (default: 30 nappal ezelőtt)
            end_date: Záró dátum (default: ma)

        Returns:
            SalesReportResponse: Napi bontású értékesítési adatok

        Raises:
            HTTPException: Ha a service_orders nem elérhető
        """
        # Default dátumok beállítása
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=30)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Lekérjük a rendeléseket és fizetéseket a service_orders-ből
                orders_url = f"{self.orders_service_url}/api/v1/orders"
                params = {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "status": "LEZART"  # Csak lezárt rendelések
                }

                logger.info(f"Fetching orders from {orders_url} with params {params}")
                response = await client.get(orders_url, params=params)
                response.raise_for_status()
                orders_data = response.json()

            # Feldolgozzuk az adatokat napi bontásban
            daily_sales_map = {}

            for order in orders_data:
                # Dátum kinyerése
                order_date_str = order.get("created_at", "")
                if not order_date_str:
                    continue

                order_date = datetime.fromisoformat(order_date_str.replace("Z", "+00:00")).date()

                # Összegek
                total_amount = Decimal(str(order.get("total_amount", 0)))

                # Fizetési módok szerinti bontás
                cash_amount = Decimal("0")
                card_amount = Decimal("0")

                payments = order.get("payments", [])
                for payment in payments:
                    payment_method = payment.get("payment_method", "")
                    amount = Decimal(str(payment.get("amount", 0)))

                    if payment_method == "KESZPENZ":
                        cash_amount += amount
                    elif payment_method in ["KARTYA", "SZEP_KARTYA"]:
                        card_amount += amount

                # Hozzáadjuk a napi összesítéshez
                date_key = order_date.isoformat()
                if date_key not in daily_sales_map:
                    daily_sales_map[date_key] = {
                        "date": order_date,
                        "total_revenue": Decimal("0"),
                        "cash_revenue": Decimal("0"),
                        "card_revenue": Decimal("0"),
                        "order_count": 0
                    }

                daily_sales_map[date_key]["total_revenue"] += total_amount
                daily_sales_map[date_key]["cash_revenue"] += cash_amount
                daily_sales_map[date_key]["card_revenue"] += card_amount
                daily_sales_map[date_key]["order_count"] += 1

            # Átlagos rendelés értékek számítása
            sales_data = []
            total_revenue = Decimal("0")
            total_orders = 0

            for date_key in sorted(daily_sales_map.keys()):
                daily_data = daily_sales_map[date_key]
                avg_order_value = (
                    daily_data["total_revenue"] / daily_data["order_count"]
                    if daily_data["order_count"] > 0
                    else Decimal("0")
                )

                sales_data.append(DailySalesData(
                    date=daily_data["date"],
                    total_revenue=daily_data["total_revenue"],
                    cash_revenue=daily_data["cash_revenue"],
                    card_revenue=daily_data["card_revenue"],
                    order_count=daily_data["order_count"],
                    average_order_value=avg_order_value
                ))

                total_revenue += daily_data["total_revenue"]
                total_orders += daily_data["order_count"]

            # Átlagos napi bevétel
            days_count = (end_date - start_date).days + 1
            average_daily_revenue = (
                total_revenue / days_count
                if days_count > 0
                else Decimal("0")
            )

            return SalesReportResponse(
                sales_data=sales_data,
                total_revenue=total_revenue,
                total_orders=total_orders,
                average_daily_revenue=average_daily_revenue
            )

        except httpx.HTTPError as e:
            logger.error(f"Error fetching sales data from orders service: {str(e)}")
            raise Exception(f"Failed to fetch sales data: {str(e)}")

    # ========================================================================
    # Top Products Methods
    # ========================================================================

    async def get_top_products(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 10
    ) -> TopProductsResponse:
        """
        Top termékek lekérése eladott mennyiség alapján.

        Args:
            start_date: Kezdő dátum (default: 30 nappal ezelőtt)
            end_date: Záró dátum (default: ma)
            limit: Maximum hány terméket adjunk vissza (default: 10)

        Returns:
            TopProductsResponse: Top termékek listája

        Raises:
            HTTPException: Ha a service_orders vagy service_menu nem elérhető
        """
        # Default dátumok beállítása
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=30)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Lekérjük a rendeléseket
                orders_url = f"{self.orders_service_url}/api/v1/orders"
                params = {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "status": "LEZART"
                }

                logger.info(f"Fetching orders for top products from {orders_url}")
                response = await client.get(orders_url, params=params)
                response.raise_for_status()
                orders_data = response.json()

                # Feldolgozzuk a termékeket
                product_stats = {}

                for order in orders_data:
                    order_items = order.get("order_items", [])

                    for item in order_items:
                        product_id = item.get("product_id")
                        quantity = item.get("quantity", 0)
                        unit_price = Decimal(str(item.get("unit_price", 0)))
                        revenue = quantity * unit_price

                        if product_id not in product_stats:
                            product_stats[product_id] = {
                                "quantity_sold": 0,
                                "total_revenue": Decimal("0"),
                                "price_sum": Decimal("0"),
                                "price_count": 0
                            }

                        product_stats[product_id]["quantity_sold"] += quantity
                        product_stats[product_id]["total_revenue"] += revenue
                        product_stats[product_id]["price_sum"] += unit_price
                        product_stats[product_id]["price_count"] += 1

                # Lekérjük a termék neveket és kategóriákat a service_menu-ből
                product_ids = list(product_stats.keys())
                products_details = {}

                for product_id in product_ids:
                    try:
                        product_url = f"{self.menu_service_url}/api/v1/products/{product_id}"
                        logger.info(f"Fetching product details from {product_url}")
                        response = await client.get(product_url)
                        response.raise_for_status()
                        product_data = response.json()
                        products_details[product_id] = product_data
                    except httpx.HTTPError as e:
                        logger.warning(f"Could not fetch product {product_id}: {str(e)}")
                        products_details[product_id] = {
                            "name": f"Termék #{product_id}",
                            "category": None
                        }

            # Összeállítjuk a top termékek listáját
            top_products = []

            for product_id, stats in product_stats.items():
                product_details = products_details.get(product_id, {})
                avg_price = (
                    stats["price_sum"] / stats["price_count"]
                    if stats["price_count"] > 0
                    else Decimal("0")
                )

                category_name = None
                if product_details.get("category"):
                    category_name = product_details["category"].get("name")

                top_products.append(TopProductData(
                    product_id=product_id,
                    product_name=product_details.get("name", f"Termék #{product_id}"),
                    quantity_sold=stats["quantity_sold"],
                    total_revenue=stats["total_revenue"],
                    average_price=avg_price,
                    category_name=category_name
                ))

            # Rendezés eladott mennyiség szerint csökkenő sorrendben
            top_products.sort(key=lambda x: x.quantity_sold, reverse=True)

            # Limitáljuk az eredményeket
            limited_products = top_products[:limit]

            return TopProductsResponse(
                products=limited_products,
                total_products_analyzed=len(product_stats)
            )

        except httpx.HTTPError as e:
            logger.error(f"Error fetching top products data: {str(e)}")
            raise Exception(f"Failed to fetch top products: {str(e)}")

    # ========================================================================
    # Inventory Consumption Methods
    # ========================================================================

    async def get_consumption_report(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> ConsumptionReportResponse:
        """
        Készletfogyási riport lekérése.

        Args:
            start_date: Kezdő dátum (default: 30 nappal ezelőtt)
            end_date: Záró dátum (default: ma)

        Returns:
            ConsumptionReportResponse: Készletfogyási adatok

        Raises:
            HTTPException: Ha a service_inventory nem elérhető
        """
        # Default dátumok beállítása
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=30)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Lekérjük a készletmozgásokat az inventory service-ből
                inventory_url = f"{self.inventory_service_url}/api/v1/inventory/movements"
                params = {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "movement_type": "CONSUMPTION"  # Csak fogyások
                }

                logger.info(f"Fetching inventory movements from {inventory_url}")
                response = await client.get(inventory_url, params=params)

                # Ha nincs ilyen endpoint, akkor üres listát adunk vissza
                if response.status_code == 404:
                    logger.warning("Inventory movements endpoint not found, returning empty consumption report")
                    return ConsumptionReportResponse(
                        consumption_data=[],
                        total_items=0,
                        total_estimated_cost=Decimal("0")
                    )

                response.raise_for_status()
                movements_data = response.json()

            # Feldolgozzuk a fogyásokat
            consumption_map = {}

            for movement in movements_data:
                item_id = movement.get("inventory_item_id")
                item_name = movement.get("item_name", f"Tétel #{item_id}")
                quantity = abs(Decimal(str(movement.get("quantity", 0))))  # Fogyás mindig pozitív
                unit = movement.get("unit", "db")
                unit_cost = Decimal(str(movement.get("unit_cost", 0)))

                if item_id not in consumption_map:
                    consumption_map[item_id] = {
                        "ingredient_name": item_name,
                        "quantity_consumed": Decimal("0"),
                        "unit": unit,
                        "estimated_cost": Decimal("0")
                    }

                consumption_map[item_id]["quantity_consumed"] += quantity
                consumption_map[item_id]["estimated_cost"] += quantity * unit_cost

            # Összeállítjuk a consumption listát
            consumption_data = []
            total_estimated_cost = Decimal("0")

            for item_id, data in consumption_map.items():
                consumption_data.append(InventoryConsumptionData(
                    ingredient_id=item_id,
                    ingredient_name=data["ingredient_name"],
                    quantity_consumed=data["quantity_consumed"],
                    unit=data["unit"],
                    estimated_cost=data["estimated_cost"]
                ))
                total_estimated_cost += data["estimated_cost"]

            # Rendezés fogyott mennyiség szerint
            consumption_data.sort(key=lambda x: x.quantity_consumed, reverse=True)

            return ConsumptionReportResponse(
                consumption_data=consumption_data,
                total_items=len(consumption_data),
                total_estimated_cost=total_estimated_cost
            )

        except httpx.HTTPError as e:
            logger.error(f"Error fetching consumption data from inventory service: {str(e)}")
            # Graceful degradation: return empty data instead of error
            logger.warning("Returning empty consumption report due to service error")
            return ConsumptionReportResponse(
                consumption_data=[],
                total_items=0,
                total_estimated_cost=Decimal("0")
            )
