"""
Integration Tests for Payment API
Sprint 2 - Task A5: Payment API + Split Fizetés

Test Cases:
1. GET /api/v1/payments/methods - Fizetési módok lekérdezése
2. POST /api/v1/orders/{id}/payments - 100% készpénz fizetés
3. POST /api/v1/orders/{id}/payments - 50% kártya + 50% SZÉP kártya (split payment)
4. POST /api/v1/orders/{id}/payments - Túlfizetési kísérlet (hiba esetben)
5. POST /api/v1/orders/{id}/payments - Érvénytelen státuszú rendelés (hiba esetben)
"""

import pytest
from decimal import Decimal
from fastapi import status


class TestPaymentMethods:
    """Test GET /api/v1/payments/methods endpoint."""

    def test_get_payment_methods_success(self, client):
        """Test successful retrieval of payment methods."""
        response = client.get("/api/v1/payments/methods")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify response structure
        assert "methods" in data
        assert isinstance(data["methods"], list)
        assert len(data["methods"]) > 0

        # Verify each payment method has required fields
        for method in data["methods"]:
            assert "code" in method
            assert "display_name" in method
            assert "enabled" in method
            assert method["enabled"] is True

        # Verify expected payment methods are present
        method_codes = [m["code"] for m in data["methods"]]
        assert "cash" in method_codes
        assert "card" in method_codes
        assert "szep_card" in method_codes

    def test_get_payment_methods_returns_display_names(self, client):
        """Test that payment methods include Hungarian display names."""
        response = client.get("/api/v1/payments/methods")
        data = response.json()

        # Find cash method
        cash_method = next(
            (m for m in data["methods"] if m["code"] == "cash"),
            None
        )
        assert cash_method is not None
        assert cash_method["display_name"] == "Készpénz"

        # Find card method
        card_method = next(
            (m for m in data["methods"] if m["code"] == "card"),
            None
        )
        assert card_method is not None
        assert card_method["display_name"] == "Bankkártya"


class TestSinglePayment:
    """Test POST /api/v1/orders/{id}/payments with single payment (100% cash)."""

    def test_single_payment_100_percent_cash(self, client, sample_order):
        """Test 100% cash payment for an order."""
        order_id = sample_order.id
        order_total = float(sample_order.total_amount)

        payment_request = {
            "payments": [
                {
                    "payment_method": "cash",
                    "amount": order_total
                }
            ]
        }

        response = client.post(
            f"/api/v1/orders/{order_id}/payments",
            json=payment_request
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Verify response structure
        assert data["order_id"] == order_id
        assert "payments" in data
        assert len(data["payments"]) == 1
        assert float(data["total_paid"]) == order_total
        assert float(data["order_total"]) == order_total
        assert data["fully_paid"] is True

        # Verify payment details
        payment = data["payments"][0]
        assert payment["payment_method"] == "cash"
        assert float(payment["amount"]) == order_total
        assert "id" in payment
        assert "created_at" in payment

    def test_single_payment_100_percent_card(self, client, sample_order):
        """Test 100% card payment for an order."""
        order_id = sample_order.id
        order_total = float(sample_order.total_amount)

        payment_request = {
            "payments": [
                {
                    "payment_method": "card",
                    "amount": order_total
                }
            ]
        }

        response = client.post(
            f"/api/v1/orders/{order_id}/payments",
            json=payment_request
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["fully_paid"] is True
        assert data["payments"][0]["payment_method"] == "card"


class TestSplitPayment:
    """Test POST /api/v1/orders/{id}/payments with split payment."""

    def test_split_payment_50_cash_50_card(self, client, sample_order):
        """Test split payment: 50% cash + 50% card."""
        order_id = sample_order.id
        order_total = float(sample_order.total_amount)
        half_amount = order_total / 2

        payment_request = {
            "payments": [
                {
                    "payment_method": "cash",
                    "amount": half_amount
                },
                {
                    "payment_method": "card",
                    "amount": half_amount
                }
            ]
        }

        response = client.post(
            f"/api/v1/orders/{order_id}/payments",
            json=payment_request
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Verify split payment was recorded
        assert data["order_id"] == order_id
        assert len(data["payments"]) == 2
        assert float(data["total_paid"]) == order_total
        assert data["fully_paid"] is True

        # Verify both payment methods are present
        payment_methods = [p["payment_method"] for p in data["payments"]]
        assert "cash" in payment_methods
        assert "card" in payment_methods

        # Verify amounts
        for payment in data["payments"]:
            assert float(payment["amount"]) == half_amount

    def test_split_payment_60_card_40_szep_card(self, client, sample_order):
        """Test split payment: 60% card + 40% SZÉP card."""
        order_id = sample_order.id
        order_total = float(sample_order.total_amount)

        # 60% card, 40% SZÉP card
        card_amount = order_total * 0.6
        szep_amount = order_total * 0.4

        payment_request = {
            "payments": [
                {
                    "payment_method": "card",
                    "amount": card_amount
                },
                {
                    "payment_method": "szep_card",
                    "amount": szep_amount
                }
            ]
        }

        response = client.post(
            f"/api/v1/orders/{order_id}/payments",
            json=payment_request
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert len(data["payments"]) == 2
        assert data["fully_paid"] is True

    def test_split_payment_three_methods(self, client, sample_order):
        """Test split payment with three different payment methods."""
        order_id = sample_order.id
        order_total = float(sample_order.total_amount)

        # 40% cash, 40% card, 20% SZÉP card
        payment_request = {
            "payments": [
                {
                    "payment_method": "cash",
                    "amount": order_total * 0.4
                },
                {
                    "payment_method": "card",
                    "amount": order_total * 0.4
                },
                {
                    "payment_method": "szep_card",
                    "amount": order_total * 0.2
                }
            ]
        }

        response = client.post(
            f"/api/v1/orders/{order_id}/payments",
            json=payment_request
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert len(data["payments"]) == 3
        assert data["fully_paid"] is True


class TestPaymentValidation:
    """Test validation rules for payment processing."""

    def test_overpayment_attempt_fails(self, client, sample_order):
        """Test that overpayment is rejected (total > order amount)."""
        order_id = sample_order.id
        order_total = float(sample_order.total_amount)

        # Try to pay MORE than the order total
        payment_request = {
            "payments": [
                {
                    "payment_method": "cash",
                    "amount": order_total + 1000.00
                }
            ]
        }

        response = client.post(
            f"/api/v1/orders/{order_id}/payments",
            json=payment_request
        )

        # Should return 400 Bad Request
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
        assert "nem egyezik" in data["detail"].lower() or "not match" in data["detail"].lower()

    def test_underpayment_attempt_fails(self, client, sample_order):
        """Test that underpayment is rejected (total < order amount)."""
        order_id = sample_order.id
        order_total = float(sample_order.total_amount)

        # Try to pay LESS than the order total
        payment_request = {
            "payments": [
                {
                    "payment_method": "cash",
                    "amount": order_total - 1000.00
                }
            ]
        }

        response = client.post(
            f"/api/v1/orders/{order_id}/payments",
            json=payment_request
        )

        # Should return 400 Bad Request
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
        assert "nem egyezik" in data["detail"].lower() or "not match" in data["detail"].lower()

    def test_payment_on_non_open_order_fails(self, client, db_session, sample_table):
        """Test that payment cannot be made on non-NYITOTT (non-OPEN) order."""
        from backend.service_orders.models.order import Order

        # Create order with LEZART (CLOSED) status
        closed_order = Order(
            order_type="Helyben",
            status="LEZART",  # Not NYITOTT!
            table_id=sample_table.id,
            total_amount=Decimal("5000.00"),
            final_vat_rate=Decimal("27.00")
        )
        db_session.add(closed_order)
        db_session.commit()
        db_session.refresh(closed_order)

        payment_request = {
            "payments": [
                {
                    "payment_method": "cash",
                    "amount": 5000.00
                }
            ]
        }

        response = client.post(
            f"/api/v1/orders/{closed_order.id}/payments",
            json=payment_request
        )

        # Should return 400 Bad Request
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
        assert "nyitott" in data["detail"].lower() or "open" in data["detail"].lower()

    def test_invalid_payment_method_fails(self, client, sample_order):
        """Test that invalid payment method is rejected."""
        order_id = sample_order.id
        order_total = float(sample_order.total_amount)

        payment_request = {
            "payments": [
                {
                    "payment_method": "bitcoin",  # Invalid method!
                    "amount": order_total
                }
            ]
        }

        response = client.post(
            f"/api/v1/orders/{order_id}/payments",
            json=payment_request
        )

        # Should return 400 Bad Request
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
        assert "érvénytelen" in data["detail"].lower() or "invalid" in data["detail"].lower()

    def test_payment_on_nonexistent_order_fails(self, client):
        """Test that payment on non-existent order returns 404."""
        payment_request = {
            "payments": [
                {
                    "payment_method": "cash",
                    "amount": 5000.00
                }
            ]
        }

        response = client.post(
            "/api/v1/orders/99999/payments",
            json=payment_request
        )

        # Should return 404 Not Found
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_empty_payments_list_fails(self, client, sample_order):
        """Test that empty payments list is rejected."""
        payment_request = {
            "payments": []
        }

        response = client.post(
            f"/api/v1/orders/{sample_order.id}/payments",
            json=payment_request
        )

        # Should return 422 Unprocessable Entity (Pydantic validation)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestPaymentRetrieval:
    """Test GET /api/v1/orders/{id}/payments endpoint."""

    def test_get_payments_after_recording(self, client, sample_order):
        """Test retrieving payments after they've been recorded."""
        order_id = sample_order.id
        order_total = float(sample_order.total_amount)

        # First, record a split payment
        payment_request = {
            "payments": [
                {
                    "payment_method": "cash",
                    "amount": order_total / 2
                },
                {
                    "payment_method": "card",
                    "amount": order_total / 2
                }
            ]
        }

        client.post(f"/api/v1/orders/{order_id}/payments", json=payment_request)

        # Now retrieve the payments
        response = client.get(f"/api/v1/orders/{order_id}/payments")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 2

        # Verify payment details
        payment_methods = [p["payment_method"] for p in data]
        assert "cash" in payment_methods
        assert "card" in payment_methods
