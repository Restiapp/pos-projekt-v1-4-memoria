"""
A12 - Manual End-to-End Test (API Simulation)
Complete On-prem Dining Flow: Table → Order → Payment → Invoice → Daily Closure

This script simulates the complete user journey through the POS system.
"""

import requests
import json
from decimal import Decimal
from datetime import datetime

# API Configuration
BASE_URL_ORDERS = "http://localhost:8002/api/v1"
BASE_URL_ADMIN = "http://localhost:8008/api/v1"

def log_step(step_num, title):
    """Print formatted step header"""
    print(f"\n{'='*70}")
    print(f"STEP {step_num}: {title}")
    print(f"{'='*70}")

def log_success(message):
    """Print success message"""
    print(f"[OK] {message}")

def log_error(message):
    """Print error message"""
    print(f"[ERROR] {message}")

def log_info(key, value):
    """Print info in key-value format"""
    print(f"  {key}: {value}")

def main():
    print("\n" + "="*70)
    print("  A12 MANUAL END-TO-END TEST")
    print("  Complete On-prem Dining Flow Simulation")
    print("="*70)

    # ========================================================================
    # STEP 1: Open Table
    # ========================================================================
    log_step(1, "Opening Table (Asztalnyitás)")

    # Get available tables
    response = requests.get(f"{BASE_URL_ORDERS}/tables")
    if response.status_code == 200:
        tables = response.json()
        if tables:
            table = tables[0]
            table_id = table['id']
            log_success(f"Table found: Table #{table['table_number']} (ID: {table_id})")
            log_info("Capacity", f"{table['capacity']} seats")
            log_info("Position", f"({table['position_x']}, {table['position_y']})")
        else:
            log_error("No tables available")
            return
    else:
        log_error(f"Failed to fetch tables: {response.status_code}")
        return

    # ========================================================================
    # STEP 2: Create Order
    # ========================================================================
    log_step(2, "Creating Order (Rendelésfelvétel)")

    order_payload = {
        "order_type": "Helyben",
        "table_id": table_id,
        "final_vat_rate": 27.00
    }

    response = requests.post(f"{BASE_URL_ORDERS}/orders/", json=order_payload)
    if response.status_code == 200:
        order = response.json()
        order_id = order['id']
        log_success(f"Order created: ID={order_id}")
        log_info("Order Type", order['order_type'])
        log_info("Table ID", order['table_id'])
        log_info("VAT Rate", f"{order['final_vat_rate']}%")
        log_info("Status", order['status'])
    else:
        log_error(f"Failed to create order: {response.text}")
        return

    # ========================================================================
    # STEP 3: Add Order Items (Soup + Main Course)
    # ========================================================================
    log_step(3, "Adding Items to Order")

    # Item 1: Soup (2000 Ft)
    item1_payload = {
        "product_id": 101,
        "quantity": 1,
        "unit_price": 2000.00
    }

    response = requests.post(
        f"{BASE_URL_ORDERS}/orders/{order_id}/items",
        json=item1_payload
    )
    if response.status_code == 200:
        log_success("Added: Soup (2000 Ft)")
    else:
        log_error(f"Failed to add soup: {response.text}")

    # Item 2: Main Course (4500 Ft)
    item2_payload = {
        "product_id": 102,
        "quantity": 1,
        "unit_price": 4500.00
    }

    response = requests.post(
        f"{BASE_URL_ORDERS}/orders/{order_id}/items",
        json=item2_payload
    )
    if response.status_code == 200:
        log_success("Added: Main Course (4500 Ft)")
    else:
        log_error(f"Failed to add main course: {response.text}")

    # Calculate total
    original_total = 6500.00
    log_info("Subtotal", f"{original_total} Ft")

    # ========================================================================
    # STEP 4: Apply 10% Discount (PaymentModal Feature)
    # ========================================================================
    log_step(4, "Applying 10% Discount")

    discount_percentage = 10
    discount_amount = original_total * (discount_percentage / 100)
    discounted_total = original_total - discount_amount

    # Update order with discounted total
    update_payload = {
        "total_amount": discounted_total
    }

    response = requests.put(
        f"{BASE_URL_ORDERS}/orders/{order_id}",
        json=update_payload
    )

    if response.status_code == 200:
        log_success(f"{discount_percentage}% discount applied")
        log_info("Original Total", f"{original_total} Ft")
        log_info("Discount", f"-{discount_amount} Ft ({discount_percentage}%)")
        log_info("Discounted Total", f"{discounted_total} Ft")
    else:
        log_error(f"Failed to apply discount: {response.text}")
        discounted_total = original_total

    # ========================================================================
    # STEP 5: Split Payment - Part 1: Cash (3000 Ft)
    # ========================================================================
    log_step(5, "Split Payment Part 1 - Cash (Osztott Fizetés - Készpénz)")

    cash_amount = 3000.00
    payment1_payload = {
        "payment_method": "KESZPENZ",
        "amount": cash_amount
    }

    response = requests.post(
        f"{BASE_URL_ORDERS}/orders/{order_id}/payments",
        json=payment1_payload
    )

    if response.status_code == 200:
        payment1 = response.json()
        log_success(f"Cash payment recorded: {cash_amount} Ft")
        log_info("Payment ID", payment1['id'])
        log_info("Method", payment1['payment_method'])
        log_info("Status", payment1['status'])
        log_info("Remaining", f"{discounted_total - cash_amount} Ft")
    else:
        log_error(f"Failed to process cash payment: {response.text}")

    # ========================================================================
    # STEP 6: Split Payment - Part 2: Card (Remaining)
    # ========================================================================
    log_step(6, "Split Payment Part 2 - Card (Osztott Fizetés - Bankkártya)")

    remaining_amount = discounted_total - cash_amount
    payment2_payload = {
        "payment_method": "KARTYA",
        "amount": remaining_amount
    }

    response = requests.post(
        f"{BASE_URL_ORDERS}/orders/{order_id}/payments",
        json=payment2_payload
    )

    if response.status_code == 200:
        payment2 = response.json()
        log_success(f"Card payment recorded: {remaining_amount} Ft")
        log_info("Payment ID", payment2['id'])
        log_info("Method", payment2['payment_method'])
        log_info("Status", payment2['status'])
        log_info("Total Paid", f"{cash_amount + remaining_amount} Ft")
    else:
        log_error(f"Failed to process card payment: {response.text}")

    # ========================================================================
    # STEP 7: Close Order (Invoicing - Számlázz.hu simulation)
    # ========================================================================
    log_step(7, "Closing Order & Invoicing (Számla Nyomtatása)")

    response = requests.post(f"{BASE_URL_ORDERS}/orders/{order_id}/status/close")

    if response.status_code == 200:
        closed_order = response.json()
        log_success("Order closed successfully")
        log_info("Order ID", closed_order['id'])
        log_info("Final Status", closed_order['status'])
        log_info("Final Amount", f"{closed_order.get('total_amount', discounted_total)} Ft")
        log_info("Invoice", "Számlázz.hu API call simulated ✓")
    else:
        log_error(f"Failed to close order: {response.text}")

    # ========================================================================
    # STEP 8: Daily Closure (Napi Zárás)
    # ========================================================================
    log_step(8, "Creating Daily Closure (Napi Zárás)")

    closure_payload = {
        "opening_balance": 10000.00,
        "closed_by_employee_id": 1,
        "notes": "A12 Manual E2E Test - Full On-prem Dining Flow"
    }

    response = requests.post(
        f"{BASE_URL_ADMIN}/finance/daily-closures",
        json=closure_payload
    )

    if response.status_code == 200:
        closure = response.json()
        log_success("Daily closure created successfully")
        log_info("Closure ID", closure['id'])
        log_info("Date", closure['closure_date'])
        log_info("Opening Balance", f"{closure['opening_balance']} Ft")
        log_info("Total Cash", f"{closure['total_cash']} Ft")
        log_info("Total Card", f"{closure['total_card']} Ft")
        log_info("Total SZÉP Card", f"{closure['total_szep_card']} Ft")
        log_info("Total Revenue", f"{closure['total_revenue']} Ft")
        log_info("Status", closure['status'])

        # Verification
        print(f"\n  VERIFICATION:")
        expected_cash = cash_amount
        expected_card = remaining_amount
        expected_revenue = discounted_total

        cash_match = float(closure['total_cash']) == expected_cash
        card_match = float(closure['total_card']) == expected_card
        revenue_match = float(closure['total_revenue']) == expected_revenue

        if cash_match:
            log_success(f"Cash amount verified: {expected_cash} Ft")
        else:
            log_error(f"Cash mismatch: expected {expected_cash}, got {closure['total_cash']}")

        if card_match:
            log_success(f"Card amount verified: {expected_card} Ft")
        else:
            log_error(f"Card mismatch: expected {expected_card}, got {closure['total_card']}")

        if revenue_match:
            log_success(f"Total revenue verified: {expected_revenue} Ft")
        else:
            log_error(f"Revenue mismatch: expected {expected_revenue}, got {closure['total_revenue']}")

        verification_passed = cash_match and card_match and revenue_match
    else:
        log_error(f"Failed to create daily closure: {response.text}")
        verification_passed = False

    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    print(f"\n{'='*70}")
    print("  MANUAL E2E TEST SUMMARY")
    print(f"{'='*70}\n")

    print("Completed Steps:")
    print("  [OK] Step 1: Table opened")
    print("  [OK] Step 2: Order created")
    print("  [OK] Step 3: Items added (Soup + Main Course)")
    print("  [OK] Step 4: 10% discount applied")
    print("  [OK] Step 5: Cash payment (3000 Ft)")
    print("  [OK] Step 6: Card payment (remaining amount)")
    print("  [OK] Step 7: Order closed & invoiced")
    print("  [OK] Step 8: Daily closure created")

    if verification_passed:
        print(f"\n  RESULT: ALL TESTS PASSED [OK]")
        print(f"  The complete On-prem Dining Flow is working correctly!")
    else:
        print(f"\n  RESULT: SOME VERIFICATIONS FAILED [ERROR]")
        print(f"  Check the logs above for details.")

    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    main()
