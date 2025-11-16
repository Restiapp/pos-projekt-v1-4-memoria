"""
NTAK Service - National Tourism Data Service Integration
Module 8: Admin Service - Phase IV

This service handles all NTAK (Nemzeti Turizmus Adatszolgáltatási Központ)
data submission operations, including:
- Fetching order data from the Orders Service
- Transforming order data to NTAK-compliant format
- Submitting data to NTAK API
- Updating order records with NTAK submission results

Critical service for Hungarian tax compliance and tourism reporting.
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional, List

import httpx

from backend.service_admin.config import settings
from backend.service_admin.schemas.ntak import (
    NTAKOrderSummaryData,
    NTAKLineItem,
    NTAKPayment,
    NTAKResponse
)

# Configure logger
logger = logging.getLogger(__name__)


class NtakService:
    """
    Service class for NTAK data submission and management.

    This class handles the complete workflow for submitting order summaries
    to the National Tourism Data Service Center (NTAK), including data
    retrieval, transformation, API submission, and result tracking.

    All methods use async/await pattern for non-blocking I/O operations.
    """

    def __init__(self):
        """Initialize NTAK Service with configuration from settings."""
        self.ntak_enabled = settings.ntak_enabled
        self.ntak_api_url = settings.ntak_api_url
        self.ntak_api_key = settings.ntak_api_key
        self.ntak_restaurant_id = settings.ntak_restaurant_id
        self.ntak_tax_number = settings.ntak_tax_number
        self.orders_service_url = settings.orders_service_url

        logger.info(
            f"NtakService initialized: enabled={self.ntak_enabled}, "
            f"restaurant_id={self.ntak_restaurant_id}"
        )

    async def send_order_summary(self, order_id: int) -> NTAKResponse:
        """
        [KRITIKUS METÓDUS] Send order summary to NTAK.

        This is the main entry point for NTAK data submission. It orchestrates
        the complete workflow:
        1. Fetch order data from Orders Service
        2. Transform data to NTAK-compliant format
        3. Submit to NTAK API
        4. Update order record with submission results

        Args:
            order_id: Unique identifier of the order to submit

        Returns:
            NTAKResponse: Response from NTAK API with submission status

        Raises:
            httpx.HTTPStatusError: If Orders Service returns an error
            httpx.RequestError: If network communication fails
            ValueError: If order data is invalid or incomplete

        Example:
            >>> ntak_service = NtakService()
            >>> response = await ntak_service.send_order_summary(order_id=42)
            >>> print(response.success)
            True
        """
        logger.info(f"Starting NTAK submission for order_id={order_id}")

        # Step 1: Fetch order data from Orders Service
        try:
            order_data = await self._fetch_order_from_service(order_id)
            logger.debug(f"Fetched order data: {order_data}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to fetch order {order_id}: {e}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Network error fetching order {order_id}: {e}")
            raise

        # Step 2: Transform order data to NTAK format
        try:
            ntak_data = self._format_ntak_data(order_data)
            logger.debug(f"Formatted NTAK data: {ntak_data}")
        except (ValueError, KeyError) as e:
            logger.error(f"Failed to format NTAK data for order {order_id}: {e}")
            raise ValueError(f"Invalid order data for NTAK submission: {e}")

        # Step 3: Submit to NTAK API
        try:
            ntak_response = await self._send_to_ntak_api(ntak_data)
            logger.info(
                f"NTAK submission result for order {order_id}: "
                f"success={ntak_response.success}, "
                f"transaction_id={ntak_response.transaction_id}"
            )
        except Exception as e:
            logger.error(f"Failed to send data to NTAK API for order {order_id}: {e}")
            # Create error response
            ntak_response = NTAKResponse(
                success=False,
                message=f"NTAK API submission failed: {str(e)}",
                transaction_id=None,
                timestamp=datetime.utcnow(),
                error_code="SUBMISSION_ERROR",
                submitted_data=ntak_data
            )

        # Step 4: Update order record with NTAK response
        try:
            await self._update_order_ntak_data(order_id, ntak_response)
            logger.info(f"Updated order {order_id} with NTAK response data")
        except Exception as e:
            logger.warning(
                f"Failed to update order {order_id} with NTAK response: {e}. "
                "NTAK submission was successful but order record not updated."
            )

        return ntak_response

    async def _fetch_order_from_service(self, order_id: int) -> Dict[str, Any]:
        """
        Fetch order data from the Orders Service via HTTP.

        Makes an async HTTP GET request to the Orders Service to retrieve
        complete order data including items, payments, and calculated totals.

        Args:
            order_id: Unique identifier of the order

        Returns:
            Dict containing complete order data from Orders Service

        Raises:
            httpx.HTTPStatusError: If order not found (404) or other HTTP error
            httpx.RequestError: If network communication fails
        """
        url = f"{self.orders_service_url}/orders/{order_id}"
        logger.debug(f"Fetching order from: {url}")

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()  # Raise exception for 4xx/5xx responses

        order_data = response.json()
        logger.debug(f"Successfully fetched order {order_id}")
        return order_data

    def _format_ntak_data(self, order_data: Dict[str, Any]) -> NTAKOrderSummaryData:
        """
        Transform order data to NTAK-compliant format.

        This method converts the internal order representation from the Orders
        Service into the standardized NTAK Order Summary format required by
        the National Tourism Data Service Center.

        Transformations include:
        - Mapping order types to NTAK terminology (e.g., "Helyben" -> dine-in)
        - Extracting and formatting line items with VAT calculations
        - Formatting payment information with NTAK-compliant payment methods
        - Calculating subtotals, VAT amounts, and totals

        Args:
            order_data: Raw order data from Orders Service

        Returns:
            NTAKOrderSummaryData: NTAK-compliant order summary

        Raises:
            KeyError: If required fields are missing in order_data
            ValueError: If data values are invalid or out of range

        Example order_data structure:
            {
                "id": 42,
                "order_type": "Helyben",
                "status": "LEZART",
                "total_amount": 10160.00,
                "final_vat_rate": 27.00,
                "table_id": 5,
                "created_at": "2024-01-15T14:30:00Z",
                "order_items": [...],
                "payments": [...]
            }
        """
        logger.debug(f"Formatting NTAK data for order {order_data.get('id')}")

        # Extract basic order information
        order_id = order_data["id"]
        order_type = order_data["order_type"]
        timestamp = datetime.fromisoformat(
            order_data["created_at"].replace("Z", "+00:00")
        )
        table_number = order_data.get("table_id")

        # Determine if this is a cancellation
        is_cancellation = order_data.get("status") == "SZTORNÓ"

        # Format line items
        line_items = []
        subtotal = Decimal("0.00")
        vat_amount = Decimal("0.00")

        # Note: In real implementation, we would fetch order_items from a separate
        # endpoint or they would be included in the order response.
        # For now, we'll create a placeholder structure.
        # TODO: Integrate with actual order items data
        order_items = order_data.get("order_items", [])

        if not order_items:
            # If no items provided, create a single line item from order total
            # This is a fallback for demo/testing purposes
            logger.warning(
                f"No order items found for order {order_id}, "
                "creating placeholder line item"
            )
            total_amount = Decimal(str(order_data.get("total_amount", "0.00")))
            vat_rate = Decimal(str(order_data.get("final_vat_rate", "27.00")))

            # Calculate unit price excluding VAT
            vat_multiplier = Decimal("1") + (vat_rate / Decimal("100"))
            unit_price = (total_amount / vat_multiplier).quantize(Decimal("0.01"))

            line_items.append(NTAKLineItem(
                product_name="Vegyes rendelés",
                quantity=1,
                unit_price=unit_price,
                vat_rate=vat_rate,
                total_amount=total_amount,
                product_id=None
            ))

            subtotal = unit_price
            vat_amount = total_amount - unit_price
        else:
            # Process actual order items
            for item in order_items:
                quantity = item.get("quantity", 1)
                unit_price = Decimal(str(item.get("unit_price", "0.00")))
                vat_rate = Decimal(str(order_data.get("final_vat_rate", "27.00")))

                # Calculate total for this line
                item_subtotal = unit_price * quantity
                item_vat = (item_subtotal * vat_rate / Decimal("100")).quantize(Decimal("0.01"))
                item_total = item_subtotal + item_vat

                line_items.append(NTAKLineItem(
                    product_name=item.get("product_name", "Ismeretlen termék"),
                    quantity=quantity,
                    unit_price=unit_price,
                    vat_rate=vat_rate,
                    total_amount=item_total,
                    product_id=item.get("product_id")
                ))

                subtotal += item_subtotal
                vat_amount += item_vat

        # Format payments
        payments = []
        payment_data = order_data.get("payments", [])

        if not payment_data:
            # If no payments provided, create a single payment for the total
            # This is a fallback for demo/testing purposes
            logger.warning(
                f"No payment data found for order {order_id}, "
                "creating placeholder payment"
            )
            total_amount = Decimal(str(order_data.get("total_amount", "0.00")))
            payments.append(NTAKPayment(
                payment_method="Készpénz",
                amount=total_amount,
                transaction_id=None
            ))
        else:
            # Process actual payments
            for payment in payment_data:
                payments.append(NTAKPayment(
                    payment_method=payment.get("payment_method", "Készpénz"),
                    amount=Decimal(str(payment.get("amount", "0.00"))),
                    transaction_id=payment.get("transaction_id")
                ))

        # Calculate totals
        total_amount = subtotal + vat_amount
        vat_rate = Decimal(str(order_data.get("final_vat_rate", "27.00")))

        # Create NTAK order summary
        ntak_data = NTAKOrderSummaryData(
            order_id=order_id,
            order_type=order_type,
            timestamp=timestamp,
            line_items=line_items,
            payments=payments,
            subtotal=subtotal.quantize(Decimal("0.01")),
            vat_amount=vat_amount.quantize(Decimal("0.01")),
            total_amount=total_amount.quantize(Decimal("0.01")),
            vat_rate=vat_rate,
            table_number=table_number,
            is_cancellation=is_cancellation
        )

        logger.debug(f"Successfully formatted NTAK data for order {order_id}")
        return ntak_data

    async def _send_to_ntak_api(self, ntak_data: NTAKOrderSummaryData) -> NTAKResponse:
        """
        [DUMMY/MOCK] Submit NTAK data to the NTAK API.

        This is a MOCK implementation that simulates successful NTAK API submission.
        In production, this would make an actual HTTPS request to the NTAK
        government service with proper authentication and encryption.

        NTAK API Requirements (for production implementation):
        - HTTPS with TLS 1.2+
        - API key authentication (settings.ntak_api_key)
        - XML or JSON payload format (TBD based on NTAK specs)
        - Digital signature for data integrity
        - Response validation and error handling

        Args:
            ntak_data: NTAK-compliant order summary data

        Returns:
            NTAKResponse: Mock success response with transaction ID

        Raises:
            Exception: In production, would raise for network/API errors

        TODO: Replace with actual NTAK API integration when specs available
        """
        logger.info(
            f"[MOCK] Sending NTAK data to API for order {ntak_data.order_id}"
        )

        # Check if NTAK is enabled
        if not self.ntak_enabled:
            logger.warning("NTAK submission skipped: NTAK is disabled in settings")
            return NTAKResponse(
                success=False,
                message="NTAK adatszolgáltatás ki van kapcsolva",
                transaction_id=None,
                timestamp=datetime.utcnow(),
                error_code="NTAK_DISABLED",
                submitted_data=ntak_data
            )

        # MOCK: Simulate API call delay
        # In production, this would be:
        # async with httpx.AsyncClient() as client:
        #     headers = {
        #         "Authorization": f"Bearer {self.ntak_api_key}",
        #         "Content-Type": "application/json",
        #         "X-Restaurant-ID": self.ntak_restaurant_id,
        #         "X-Tax-Number": self.ntak_tax_number
        #     }
        #     response = await client.post(
        #         f"{self.ntak_api_url}/order-summary",
        #         json=ntak_data.model_dump(),
        #         headers=headers,
        #         timeout=30.0
        #     )
        #     response.raise_for_status()
        #     result = response.json()

        # MOCK: Simulate successful response
        transaction_id = (
            f"NTAK-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-"
            f"{ntak_data.order_id:06d}"
        )

        logger.info(
            f"[MOCK] NTAK submission successful: transaction_id={transaction_id}"
        )

        return NTAKResponse(
            success=True,
            message="Rendelésösszesítő sikeresen elküldve (MOCK)",
            transaction_id=transaction_id,
            timestamp=datetime.utcnow(),
            error_code=None,
            submitted_data=ntak_data
        )

    async def _update_order_ntak_data(
        self,
        order_id: int,
        ntak_response: NTAKResponse
    ) -> Dict[str, Any]:
        """
        Update order record with NTAK submission results.

        Makes an async HTTP PATCH request to the Orders Service to update
        the order's ntak_data field with the submission results. This creates
        an audit trail of all NTAK submissions for the order.

        Args:
            order_id: Unique identifier of the order
            ntak_response: NTAK API response to store in order record

        Returns:
            Dict containing updated order data from Orders Service

        Raises:
            httpx.HTTPStatusError: If order update fails
            httpx.RequestError: If network communication fails
        """
        url = f"{self.orders_service_url}/orders/{order_id}"
        logger.debug(f"Updating order NTAK data at: {url}")

        # Prepare NTAK data for order update
        ntak_data_update = {
            "ntak_submitted": True,
            "ntak_transaction_id": ntak_response.transaction_id,
            "ntak_submission_timestamp": ntak_response.timestamp.isoformat(),
            "ntak_submission_success": ntak_response.success,
            "ntak_message": ntak_response.message,
            "ntak_error_code": ntak_response.error_code
        }

        # Prepare PATCH request payload
        update_payload = {
            "ntak_data": ntak_data_update
        }

        # Send PATCH request to Orders Service
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.patch(
                url,
                json=update_payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()

        updated_order = response.json()
        logger.info(f"Successfully updated order {order_id} with NTAK data")
        return updated_order


# Singleton instance for use across the application
ntak_service = NtakService()
