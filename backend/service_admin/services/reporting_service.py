"""
Reporting Service - Business logic for analytics and reporting.

This service provides aggregated data from multiple services (orders, inventory)
for sales reports, top products analysis, and inventory consumption tracking.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from sqlalchemy import func, desc, and_, text
from sqlalchemy.orm import Session
import httpx

from backend.service_admin.config import settings


class ReportingService:
    """
    Service for generating analytics and reports.

    This service aggregates data from orders, payments, and inventory
    to provide comprehensive business intelligence reports.
    """

    @staticmethod
    async def get_sales_report(
        db: Session,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Generate sales report with daily breakdown and payment method analysis.

        Args:
            db: Database session
            start_date: Report start date
            end_date: Report end date

        Returns:
            Dictionary containing sales metrics and breakdowns
        """
        # Query orders within date range
        query = text("""
            WITH daily_sales AS (
                SELECT
                    DATE(o.created_at) as sale_date,
                    COUNT(DISTINCT o.id) as order_count,
                    COALESCE(SUM(o.total_amount), 0) as total_revenue,
                    COALESCE(AVG(o.total_amount), 0) as avg_cart_value
                FROM orders o
                WHERE o.status IN ('FELDOLGOZVA', 'LEZART')
                    AND DATE(o.created_at) BETWEEN :start_date AND :end_date
                GROUP BY DATE(o.created_at)
            ),
            payment_breakdown AS (
                SELECT
                    DATE(o.created_at) as sale_date,
                    p.payment_method,
                    COUNT(DISTINCT o.id) as order_count,
                    COALESCE(SUM(p.amount), 0) as total_amount
                FROM orders o
                JOIN payments p ON o.id = p.order_id
                WHERE o.status IN ('FELDOLGOZVA', 'LEZART')
                    AND p.status = 'SIKERES'
                    AND DATE(o.created_at) BETWEEN :start_date AND :end_date
                GROUP BY DATE(o.created_at), p.payment_method
            )
            SELECT * FROM daily_sales
            ORDER BY sale_date ASC
        """)

        daily_results = db.execute(
            query,
            {"start_date": start_date, "end_date": end_date}
        ).fetchall()

        # Query payment breakdown
        payment_query = text("""
            SELECT
                DATE(o.created_at) as sale_date,
                p.payment_method,
                COUNT(DISTINCT o.id) as order_count,
                COALESCE(SUM(p.amount), 0) as total_amount
            FROM orders o
            JOIN payments p ON o.id = p.order_id
            WHERE o.status IN ('FELDOLGOZVA', 'LEZART')
                AND p.status = 'SIKERES'
                AND DATE(o.created_at) BETWEEN :start_date AND :end_date
            GROUP BY DATE(o.created_at), p.payment_method
            ORDER BY sale_date ASC, p.payment_method
        """)

        payment_results = db.execute(
            payment_query,
            {"start_date": start_date, "end_date": end_date}
        ).fetchall()

        # Organize payment data by date
        payment_by_date = {}
        for row in payment_results:
            sale_date = row[0]
            payment_method = row[1]
            order_count = row[2]
            total_amount = row[3]

            if sale_date not in payment_by_date:
                payment_by_date[sale_date] = {}

            payment_by_date[sale_date][payment_method] = {
                'order_count': order_count,
                'revenue': float(total_amount)
            }

        # Build daily breakdown
        daily_breakdown = []
        total_revenue = Decimal(0)
        total_orders = 0

        for row in daily_results:
            sale_date = row[0]
            order_count = row[1]
            revenue = Decimal(str(row[2]))
            avg_cart = Decimal(str(row[3]))

            # Get payment breakdown for this date
            date_payments = payment_by_date.get(sale_date, {})

            # Map KESZPENZ/KARTYA to CASH/CARD for response
            cash_data = date_payments.get('KESZPENZ', {'revenue': 0, 'order_count': 0})
            card_data = date_payments.get('KARTYA', {'revenue': 0, 'order_count': 0})

            daily_breakdown.append({
                'date': sale_date,
                'total_revenue': float(revenue),
                'order_count': order_count,
                'average_cart_value': float(avg_cart),
                'cash_revenue': cash_data['revenue'],
                'card_revenue': card_data['revenue'],
                'cash_order_count': cash_data['order_count'],
                'card_order_count': card_data['order_count']
            })

            total_revenue += revenue
            total_orders += order_count

        # Build payment method summary
        payment_summary = {}
        for date_data in payment_by_date.values():
            for method, data in date_data.items():
                # Map to CASH/CARD
                mapped_method = 'CASH' if method == 'KESZPENZ' else ('CARD' if method == 'KARTYA' else method)

                if mapped_method not in payment_summary:
                    payment_summary[mapped_method] = {'revenue': 0, 'order_count': 0}

                payment_summary[mapped_method]['revenue'] += data['revenue']
                payment_summary[mapped_method]['order_count'] += data['order_count']

        avg_cart_value = float(total_revenue / total_orders) if total_orders > 0 else 0.0

        return {
            'start_date': start_date,
            'end_date': end_date,
            'total_revenue': float(total_revenue),
            'total_orders': total_orders,
            'average_cart_value': avg_cart_value,
            'daily_breakdown': daily_breakdown,
            'payment_method_breakdown': payment_summary
        }

    @staticmethod
    async def get_top_products_report(
        db: Session,
        limit: int = 10,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Generate top products report by quantity sold.

        Args:
            db: Database session
            limit: Number of top products to return
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Dictionary containing top products data
        """
        # Build date filter
        date_filter = ""
        params = {"limit": limit}

        if start_date and end_date:
            date_filter = "AND DATE(o.created_at) BETWEEN :start_date AND :end_date"
            params["start_date"] = start_date
            params["end_date"] = end_date

        query = text(f"""
            SELECT
                oi.product_id,
                SUM(oi.quantity) as total_quantity,
                SUM(oi.quantity * oi.unit_price) as total_revenue,
                COUNT(DISTINCT oi.order_id) as order_count,
                AVG(oi.unit_price) as avg_price
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            WHERE o.status IN ('FELDOLGOZVA', 'LEZART')
                {date_filter}
            GROUP BY oi.product_id
            ORDER BY total_quantity DESC
            LIMIT :limit
        """)

        results = db.execute(query, params).fetchall()

        # Get product names from menu service
        product_ids = [row[0] for row in results]
        product_names = await ReportingService._fetch_product_names(product_ids)

        # Get total products count
        count_query = text(f"""
            SELECT COUNT(DISTINCT oi.product_id)
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            WHERE o.status IN ('FELDOLGOZVA', 'LEZART')
                {date_filter}
        """)

        total_products = db.execute(count_query, params).scalar() or 0

        products = []
        for row in results:
            product_id = row[0]
            total_quantity = row[1]
            total_revenue = row[2]
            order_count = row[3]
            avg_price = row[4]

            products.append({
                'product_id': product_id,
                'product_name': product_names.get(product_id, f"Product #{product_id}"),
                'total_quantity_sold': float(total_quantity),
                'total_revenue': float(total_revenue),
                'order_count': order_count,
                'average_price': float(avg_price)
            })

        return {
            'limit': limit,
            'start_date': start_date,
            'end_date': end_date,
            'products': products,
            'total_products_analyzed': total_products
        }

    @staticmethod
    async def get_consumption_report(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Generate inventory consumption report.

        This report shows current inventory levels and estimated consumption.
        For a more accurate consumption report, historical inventory snapshots
        would be needed.

        Args:
            db: Database session
            start_date: Optional start date (for future implementation)
            end_date: Optional end date (for future implementation)

        Returns:
            Dictionary containing inventory consumption data
        """
        query = text("""
            SELECT
                id,
                name,
                unit,
                current_stock_perpetual,
                last_cost_per_unit
            FROM inventory_items
            ORDER BY name ASC
        """)

        results = db.execute(query).fetchall()

        items = []
        total_estimated_cost = Decimal(0)
        high_consumption_items = []

        for row in results:
            item_id = row[0]
            name = row[1]
            unit = row[2]
            current_stock = Decimal(str(row[3]))
            last_cost = Decimal(str(row[4])) if row[4] else Decimal(0)

            # For this basic implementation, we'll use a mock opening stock
            # In a real implementation, this would come from historical data
            # or daily inventory sheets
            opening_stock = current_stock * Decimal('1.5')  # Mock: assume 50% consumption
            consumed_quantity = opening_stock - current_stock
            consumption_percentage = float((consumed_quantity / opening_stock * 100)) if opening_stock > 0 else 0
            estimated_cost = consumed_quantity * last_cost

            item_data = {
                'inventory_item_id': item_id,
                'inventory_item_name': name,
                'unit': unit,
                'opening_stock': float(opening_stock),
                'current_stock': float(current_stock),
                'consumed_quantity': float(consumed_quantity),
                'consumption_percentage': consumption_percentage,
                'last_cost_per_unit': float(last_cost) if last_cost else None,
                'estimated_cost': float(estimated_cost) if last_cost else None
            }

            items.append(item_data)

            if last_cost:
                total_estimated_cost += estimated_cost

            if consumption_percentage > 50:
                high_consumption_items.append(item_data)

        return {
            'start_date': start_date,
            'end_date': end_date,
            'report_generated_at': datetime.now(),
            'items': items,
            'total_items': len(items),
            'total_estimated_cost': float(total_estimated_cost),
            'high_consumption_items': high_consumption_items
        }

    @staticmethod
    async def _fetch_product_names(product_ids: List[int]) -> Dict[int, str]:
        """
        Fetch product names from menu service.

        Args:
            product_ids: List of product IDs to fetch

        Returns:
            Dictionary mapping product_id to product_name
        """
        if not product_ids:
            return {}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.menu_service_url}/api/v1/products",
                    params={"limit": 1000},
                    timeout=10.0
                )

                if response.status_code == 200:
                    products = response.json()
                    return {
                        product['id']: product['name']
                        for product in products
                        if product['id'] in product_ids
                    }
        except Exception as e:
            # If menu service is unavailable, return empty dict
            # Product names will fall back to "Product #ID"
            print(f"Failed to fetch product names: {e}")

        return {}
