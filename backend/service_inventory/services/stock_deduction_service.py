"""
Stock Deduction Service - Business Logic Layer
Handles automatic inventory deduction when orders are closed

This service is triggered by the Orders Service when an order is marked as LEZART (closed).
It fetches order items, looks up recipes, and deducts ingredients from inventory.
"""
import logging
from typing import Dict, Any, List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import Depends
import httpx

from backend.service_inventory.services.recipe_service import RecipeService
from backend.service_inventory.services.inventory_service import InventoryService
from backend.service_inventory.config import settings
from backend.service_inventory.models.database import get_db

logger = logging.getLogger(__name__)


class StockDeductionService:
    """
    Service for automatic stock deduction based on order consumption

    This service:
    1. Fetches order items from Orders Service via HTTP
    2. For each order item (product), looks up recipes
    3. Calculates ingredient consumption based on recipes and quantities
    4. Deducts ingredients from inventory using InventoryService
    5. Returns a deduction summary with success/failure details
    """

    def __init__(self, db: Session):
        self.db = db
        self.recipe_service = RecipeService(db)
        self.inventory_service = InventoryService(db)

    def deduct_stock_for_order(
        self,
        order_id: int,
        orders_service_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Deduct inventory stock for a closed order

        Args:
            order_id: The ID of the order to process
            orders_service_url: Optional override for Orders Service URL

        Returns:
            Dict with deduction summary:
            {
                "success": bool,
                "order_id": int,
                "items_processed": int,
                "ingredients_deducted": List[dict],
                "errors": List[dict],
                "message": str
            }

        Raises:
            ValueError: If order cannot be fetched
            httpx.HTTPError: If Orders Service is unreachable
        """
        service_url = orders_service_url or settings.menu_service_url.replace("8001", "8002")
        # NOTE: Using hardcoded port replacement as temporary workaround
        # TODO: Add orders_service_url to service_inventory config.py

        logger.info(f"[STOCK DEDUCTION] Processing order {order_id}")

        try:
            # Step 1: Fetch order details from Orders Service
            order_data = self._fetch_order_from_service(order_id, service_url)

            # Step 2: Fetch order items
            order_items = self._fetch_order_items_from_service(order_id, service_url)

            if not order_items:
                logger.warning(f"[STOCK DEDUCTION] Order {order_id} has no items")
                return {
                    "success": True,
                    "order_id": order_id,
                    "items_processed": 0,
                    "ingredients_deducted": [],
                    "errors": [],
                    "message": "No items to process"
                }

            # Step 3: Process each order item and deduct ingredients
            deduction_results = self._process_order_items(order_items)

            # Step 4: Compile summary
            total_items = len(order_items)
            successful_deductions = deduction_results["successful"]
            failed_deductions = deduction_results["failed"]
            skipped_items = deduction_results["skipped"]

            success = len(failed_deductions) == 0

            message = f"Processed {total_items} order items: " \
                     f"{len(successful_deductions)} ingredients deducted, " \
                     f"{len(skipped_items)} items skipped (no recipe), " \
                     f"{len(failed_deductions)} errors"

            logger.info(f"[STOCK DEDUCTION] {message}")

            return {
                "success": success,
                "order_id": order_id,
                "items_processed": total_items,
                "ingredients_deducted": successful_deductions,
                "skipped_items": skipped_items,
                "errors": failed_deductions,
                "message": message
            }

        except httpx.HTTPError as e:
            error_msg = f"Failed to fetch order {order_id} from Orders Service: {str(e)}"
            logger.error(f"[STOCK DEDUCTION] {error_msg}")
            raise ValueError(error_msg)

        except Exception as e:
            error_msg = f"Unexpected error processing order {order_id}: {str(e)}"
            logger.error(f"[STOCK DEDUCTION] {error_msg}")
            return {
                "success": False,
                "order_id": order_id,
                "items_processed": 0,
                "ingredients_deducted": [],
                "errors": [{"message": error_msg}],
                "message": error_msg
            }

    def _fetch_order_from_service(
        self,
        order_id: int,
        service_url: str
    ) -> Dict[str, Any]:
        """
        Fetch order details from Orders Service via HTTP

        Args:
            order_id: Order ID
            service_url: Orders Service base URL

        Returns:
            Order data as dict

        Raises:
            httpx.HTTPError: If request fails
            ValueError: If order not found
        """
        with httpx.Client(timeout=5.0) as client:
            url = f"{service_url}/api/orders/{order_id}"
            logger.debug(f"[STOCK DEDUCTION] Fetching order from: {url}")

            response = client.get(url)

            if response.status_code == 404:
                raise ValueError(f"Order {order_id} not found in Orders Service")

            response.raise_for_status()
            return response.json()

    def _fetch_order_items_from_service(
        self,
        order_id: int,
        service_url: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch order items from Orders Service via HTTP

        Args:
            order_id: Order ID
            service_url: Orders Service base URL

        Returns:
            List of order items

        Raises:
            httpx.HTTPError: If request fails
        """
        with httpx.Client(timeout=5.0) as client:
            url = f"{service_url}/api/orders/{order_id}/items"
            logger.debug(f"[STOCK DEDUCTION] Fetching order items from: {url}")

            response = client.get(url)

            if response.status_code == 404:
                # Order exists but no items endpoint - try to get from order object
                logger.warning(f"[STOCK DEDUCTION] /items endpoint not found, extracting from order")
                order_data = self._fetch_order_from_service(order_id, service_url)
                return order_data.get("order_items", [])

            response.raise_for_status()
            return response.json()

    def _process_order_items(
        self,
        order_items: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Process all order items and deduct ingredients from inventory

        Args:
            order_items: List of order item dicts with product_id and quantity

        Returns:
            Dict with three lists: successful, failed, skipped
        """
        successful = []
        failed = []
        skipped = []

        for item in order_items:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)
            item_id = item.get("id")

            if not product_id:
                logger.warning(f"[STOCK DEDUCTION] Order item {item_id} has no product_id")
                skipped.append({
                    "order_item_id": item_id,
                    "reason": "No product_id"
                })
                continue

            logger.debug(f"[STOCK DEDUCTION] Processing product {product_id} (qty: {quantity})")

            try:
                # Get recipes for this product
                recipes = self.recipe_service.get_recipes_by_product(product_id)

                if not recipes:
                    logger.info(f"[STOCK DEDUCTION] Product {product_id} has no recipes, skipping")
                    skipped.append({
                        "order_item_id": item_id,
                        "product_id": product_id,
                        "quantity": quantity,
                        "reason": "No recipe found"
                    })
                    continue

                # Deduct ingredients for each recipe
                for recipe in recipes:
                    inventory_item_id = recipe.inventory_item_id
                    quantity_per_unit = float(recipe.quantity_used)
                    total_quantity = quantity_per_unit * quantity

                    # Deduct from inventory (negative quantity_change)
                    updated_item = self.inventory_service.update_stock(
                        item_id=inventory_item_id,
                        quantity_change=-total_quantity
                    )

                    if updated_item:
                        successful.append({
                            "order_item_id": item_id,
                            "product_id": product_id,
                            "inventory_item_id": inventory_item_id,
                            "inventory_item_name": updated_item.name,
                            "quantity_deducted": total_quantity,
                            "remaining_stock": float(updated_item.current_stock_perpetual),
                            "unit": updated_item.unit
                        })

                        logger.info(
                            f"[STOCK DEDUCTION] Deducted {total_quantity} {updated_item.unit} "
                            f"of {updated_item.name} (remaining: {updated_item.current_stock_perpetual})"
                        )

            except ValueError as e:
                # Insufficient stock or other business logic error
                error_detail = {
                    "order_item_id": item_id,
                    "product_id": product_id,
                    "quantity": quantity,
                    "error": str(e)
                }
                failed.append(error_detail)
                logger.error(f"[STOCK DEDUCTION] Failed to deduct for item {item_id}: {str(e)}")

            except Exception as e:
                # Unexpected error
                error_detail = {
                    "order_item_id": item_id,
                    "product_id": product_id,
                    "quantity": quantity,
                    "error": f"Unexpected error: {str(e)}"
                }
                failed.append(error_detail)
                logger.error(f"[STOCK DEDUCTION] Unexpected error for item {item_id}: {str(e)}")

        return {
            "successful": successful,
            "failed": failed,
            "skipped": skipped
        }


def get_stock_deduction_service(db: Session = Depends(get_db)) -> StockDeductionService:
    """Dependency injection helper for StockDeductionService"""
    return StockDeductionService(db)
