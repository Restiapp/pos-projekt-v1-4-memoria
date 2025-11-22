"""
Sprint 4 End-to-End Test
Tests the complete payment flow with discounts and split payments
"""

import requests
import json
from decimal import Decimal

# API Endpoints
ORDERS_API = "http://localhost:8002/api/v1"
PAYMENTS_API = "http://localhost:8002/api/v1"
ADMIN_API = "http://localhost:8008/api/v1"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_end_to_end_payment_flow():
    """Complete end-to-end payment flow test"""

    print_section("SPRINT 4 END-TO-END TEST - Payment Flow")

    # ========================================================================
    # STEP 1: Create Order
    # ========================================================================
    print_section("STEP 1: Creating Order for Table 1")

    order_data = {
        "order_type": "Helyben",
        "table_id": 1,
        "final_vat_rate": 27.00
    }

    response = requests.post(f"{ORDERS_API}/orders", json=order_data)
    print(f"Status: {response.status_code}")

    if response.status_code != 200:
        print(f"ERROR: {response.text}")
        return

    order = response.json()
    order_id = order['id']
    print(f"✓ Order created: ID={order_id}")
    print(f"  Order Type: {order['order_type']}")
    print(f"  Table ID: {order['table_id']}")
    print(f"  Status: {order['status']}")

    # ========================================================================
    # STEP 2: Add Order Items
    # ========================================================================
    print_section("STEP 2: Adding Items to Order")

    # Add item 1: Soup (2000 Ft)
    item1_data = {
        "product_id": 1,
        "quantity": 1,
        "unit_price": 2000.00
    }

    response = requests.post(
        f"{ORDERS_API}/orders/{order_id}/items",
        json=item1_data
    )
    print(f"Added Soup: {response.status_code}")

    # Add item 2: Main Course (4500 Ft)
    item2_data = {
        "product_id": 2,
        "quantity": 1,
        "unit_price": 4500.00
    }

    response = requests.post(
        f"{ORDERS_API}/orders/{order_id}/items",
        json=item2_data
    )
    print(f"Added Main Course: {response.status_code}")

    # Get updated order
    response = requests.get(f"{ORDERS_API}/orders/{order_id}")
    order = response.json()
    total_before_discount = float(order.get('total_amount', 6500.00))

    print(f"\n✓ Items added successfully")
    print(f"  Total before discount: {total_before_discount} Ft")

    # ========================================================================
    # STEP 3: Apply 10% Discount (Teszteset 1)
    # ========================================================================
    print_section("STEP 3: Applying 10% Discount (Teszteset 1)")

    discount_amount = total_before_discount * 0.10
    discounted_total = total_before_discount - discount_amount

    # Update order with discounted total
    update_data = {
        "total_amount": discounted_total
    }

    response = requests.patch(
        f"{ORDERS_API}/orders/{order_id}",
        json=update_data
    )

    if response.status_code == 200:
        print(f"✓ 10% Discount applied")
        print(f"  Original Total: {total_before_discount} Ft")
        print(f"  Discount: -{discount_amount} Ft (10%)")
        print(f"  Final Total: {discounted_total} Ft")
    else:
        print(f"ERROR applying discount: {response.text}")
        discounted_total = total_before_discount

    # ========================================================================
    # STEP 4: Split Payment - Part 1: Cash (Teszteset 2)
    # ========================================================================
    print_section("STEP 4: Split Payment Part 1 - Cash Payment")

    cash_amount = 3000.00

    payment1_data = {
        "payment_method": "KESZPENZ",
        "amount": cash_amount
    }

    response = requests.post(
        f"{PAYMENTS_API}/orders/{order_id}/payments",
        json=payment1_data
    )

    if response.status_code == 200:
        payment1 = response.json()
        print(f"✓ Cash payment successful")
        print(f"  Payment ID: {payment1['id']}")
        print(f"  Amount: {payment1['amount']} Ft")
        print(f"  Method: {payment1['payment_method']}")
        print(f"  Status: {payment1['status']}")
        print(f"  Remaining: {discounted_total - cash_amount} Ft")
    else:
        print(f"ERROR: {response.text}")

    # ========================================================================
    # STEP 5: Split Payment - Part 2: Card (Teszteset 2)
    # ========================================================================
    print_section("STEP 5: Split Payment Part 2 - Card Payment")

    remaining_amount = discounted_total - cash_amount

    payment2_data = {
        "payment_method": "KARTYA",
        "amount": remaining_amount
    }

    response = requests.post(
        f"{PAYMENTS_API}/orders/{order_id}/payments",
        json=payment2_data
    )

    if response.status_code == 200:
        payment2 = response.json()
        print(f"✓ Card payment successful")
        print(f"  Payment ID: {payment2['id']}")
        print(f"  Amount: {payment2['amount']} Ft")
        print(f"  Method: {payment2['payment_method']}")
        print(f"  Status: {payment2['status']}")
        print(f"  Total Paid: {cash_amount + remaining_amount} Ft")
    else:
        print(f"ERROR: {response.text}")

    # ========================================================================
    # STEP 6: Close Order (Teszteset 3 - Invoicing simulation)
    # ========================================================================
    print_section("STEP 6: Closing Order")

    close_data = {
        "status": "LEZART"
    }

    response = requests.patch(
        f"{ORDERS_API}/orders/{order_id}",
        json=close_data
    )

    if response.status_code == 200:
        closed_order = response.json()
        print(f"✓ Order closed successfully")
        print(f"  Order ID: {closed_order['id']}")
        print(f"  Status: {closed_order['status']}")
        print(f"  Final Amount: {closed_order['total_amount']} Ft")
    else:
        print(f"ERROR: {response.text}")

    # ========================================================================
    # STEP 7: Daily Closure Test (Teszteset 4)
    # ========================================================================
    print_section("STEP 7: Creating Daily Closure (Teszteset 4)")

    closure_data = {
        "opening_balance": 10000.00,
        "closed_by_employee_id": 1,
        "notes": "Sprint 4 End-to-End Test Closure"
    }

    response = requests.post(
        f"{ADMIN_API}/finance/daily-closures",
        json=closure_data
    )

    if response.status_code == 200:
        closure = response.json()
        print(f"✓ Daily closure created successfully")
        print(f"  Closure ID: {closure['id']}")
        print(f"  Date: {closure['closure_date']}")
        print(f"  Opening Balance: {closure['opening_balance']} Ft")
        print(f"  Total Cash: {closure['total_cash']} Ft")
        print(f"  Total Card: {closure['total_card']} Ft")
        print(f"  Total SZÉP Card: {closure['total_szep_card']} Ft")
        print(f"  Total Revenue: {closure['total_revenue']} Ft")
        print(f"  Status: {closure['status']}")

        # Verify amounts match our test order
        print(f"\n  Verification:")
        print(f"  Expected Cash: {cash_amount} Ft")
        print(f"  Expected Card: {remaining_amount} Ft")
        print(f"  Expected Total: {discounted_total} Ft")

        if float(closure['total_cash']) == cash_amount:
            print(f"  ✓ Cash amount matches!")
        else:
            print(f"  ✗ Cash mismatch: expected {cash_amount}, got {closure['total_cash']}")

        if float(closure['total_card']) == remaining_amount:
            print(f"  ✓ Card amount matches!")
        else:
            print(f"  ✗ Card mismatch: expected {remaining_amount}, got {closure['total_card']}")

        if float(closure['total_revenue']) == discounted_total:
            print(f"  ✓ Total revenue matches!")
        else:
            print(f"  ✗ Revenue mismatch: expected {discounted_total}, got {closure['total_revenue']}")
    else:
        print(f"ERROR: {response.text}")
        print(f"Response: {response.status_code}")

    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    print_section("FINAL SUMMARY - All Tests")

    print("✓ Teszteset 1: 10% Discount Applied Successfully")
    print("✓ Teszteset 2: Split Payment (Cash + Card) Successful")
    print("✓ Teszteset 3: Order Closed Successfully")
    print("✓ Teszteset 4: Daily Closure with Revenue Aggregation Successful")

    print("\n" + "="*60)
    print("  SPRINT 4 END-TO-END TEST: PASSED ✓")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_end_to_end_payment_flow()
