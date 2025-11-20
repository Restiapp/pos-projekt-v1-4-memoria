# Receipt Printing - Testing Guide

## Overview
Thermal receipt printing has been implemented for the POS system. This guide explains how to test the feature.

## Implementation Summary

### Backend Changes
1. **PrinterService** (`backend/service_orders/services/printer_service.py`)
   - Receipt formatting logic (48-character width for thermal printers)
   - File-based output to `printer_output/` directory
   - Console logging for development

2. **API Endpoint** (`backend/service_orders/routers/orders.py`)
   - `POST /api/v1/orders/{order_id}/print-receipt`
   - Returns: `{success, message, file_path, order_id}`

### Frontend Changes
1. **Payment Service** (`frontend/src/services/paymentService.ts`)
   - New `printReceipt(orderId)` function

2. **Payment Modal** (`frontend/src/components/payment/PaymentModal.tsx`)
   - "Print Receipt" button (🖨️ Blokk nyomtatása)
   - Automatic printing after successful order closure
   - Toast notifications for success/error

3. **Styling** (`frontend/src/components/payment/PaymentModal.css`)
   - Print button styling with purple gradient
   - Hover effects and disabled states

## Testing Steps

### Prerequisites
1. Backend service running on port 8002
2. Frontend service running (Vite dev server)
3. Valid order with items and payments in the database

### Test Case 1: Manual Print (Before Order Closure)
1. Navigate to an order with items
2. Open the Payment Modal
3. Click "🖨️ Blokk nyomtatása" button
4. **Expected Result:**
   - Alert: "Blokk sikeresen kinyomtatva: receipt_{order_id}_{timestamp}.txt"
   - File created in `backend/service_orders/printer_output/`
   - Receipt printed to console

### Test Case 2: Automatic Print (After Order Closure)
1. Navigate to an order with full payment
2. Open the Payment Modal
3. Click "✅ Rendelés lezárása"
4. **Expected Result:**
   - Order closed successfully
   - Receipt automatically printed (silent, logged to console)
   - File created in `printer_output/`

### Test Case 3: Verify Receipt Content
1. Open the generated receipt file
2. **Verify the following sections:**
   - Header: Restaurant name, address, tax ID, phone
   - Order info: Order number, type, table, date
   - Items: Product names, quantities, prices, totals
   - Modifiers: Listed under each item (if present)
   - Totals: VAT breakdown (net, VAT, gross)
   - Payments: Payment methods and amounts
   - Footer: "Köszönjük a vásárlást!" + timestamp

### Test Case 4: Error Handling
1. Try to print receipt for non-existent order ID
2. **Expected Result:**
   - Alert: "Rendelés nem található: ID={order_id}"
   - HTTP 404 error logged

## Receipt Format Example

```
================================================
              POS Étterem
        1051 Budapest, Alkotmány utca 12.
            Tel: +36 1 234 5678
          Adószám: 12345678-1-42
================================================

              SZÁMLA / RECEIPT

Rendelés száma: 42
Típus: Helyben
Asztal: 5
Dátum: 2025-11-20 14:30:00
------------------------------------------------
Tétel                                    Összeg
------------------------------------------------
Hamburger
  2 x 1,500 Ft                         3,000 Ft
    + Extra sajt (+200 Ft)

Pizza Margherita
  1 x 2,500 Ft                         2,500 Ft

================================================
VÉGÖSSZEG:                             5,500 Ft
------------------------------------------------
ÁFA kulcs: 27%
  Nettó:                               4,331 Ft
  ÁFA:                                 1,169 Ft
  Bruttó:                              5,500 Ft
------------------------------------------------
Fizetési módok:
  Készpénz                             5,500 Ft
------------------------------------------------
Befizetett:                            5,500 Ft
================================================

           Köszönjük a vásárlást!
                Thank you!

      Nyomtatva: 2025-11-20 14:35:00
================================================
```

## API Testing with curl

### Print Receipt
```bash
curl -X POST http://localhost:8002/api/v1/orders/42/print-receipt \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Blokk sikeresen kinyomtatva: receipt_42_20251120_143500.txt",
  "file_path": "/path/to/printer_output/receipt_42_20251120_143500.txt",
  "order_id": 42
}
```

## Future Enhancements
1. **ESC/POS Integration**: Replace file output with actual printer driver
2. **Receipt Templates**: Configurable receipt layouts
3. **Logo Support**: Add restaurant logo to receipt header
4. **QR Codes**: Add QR code for digital receipt
5. **Email/SMS**: Send digital receipts to customers
6. **Reprint**: Add ability to reprint old receipts

## Configuration

Restaurant information is hardcoded in `printer_service.py`:
```python
RESTAURANT_NAME = "POS Étterem"
RESTAURANT_ADDRESS = "1051 Budapest, Alkotmány utca 12."
RESTAURANT_TAX_ID = "12345678-1-42"
RESTAURANT_PHONE = "+36 1 234 5678"
RECEIPT_WIDTH = 48  # Characters (80mm thermal paper)
```

To customize, edit these constants or move them to a configuration file.

## Troubleshooting

### Issue: "printer_output" directory not found
**Solution**: The directory is created automatically on first PrinterService initialization.

### Issue: Receipt file is empty
**Solution**: Check backend logs for errors. Ensure order has items.

### Issue: Frontend button not working
**Solution**: Check browser console for API errors. Verify backend is running.

### Issue: Special characters not displaying correctly
**Solution**: Receipt files are saved with UTF-8 encoding. Ensure text editor supports UTF-8.
