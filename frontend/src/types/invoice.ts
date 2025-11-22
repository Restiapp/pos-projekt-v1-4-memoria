/**
 * Invoice (Számlázz.hu) típusdefiníciók
 * Backend API sémáknak megfelelően (service_admin:8008)
 */

// Számla tétel típus
export interface InvoiceItem {
  name: string; // Tétel neve
  quantity: number; // Mennyiség
  unit: string; // Mennyiségi egység (pl. "db", "kg", "l")
  unit_price: number; // Egységár (bruttó)
  vat_rate: number; // ÁFA kulcs (%)
}

// Számla létrehozás Request
export interface InvoiceCreateRequest {
  order_id: number; // Rendelés azonosító
  customer_name: string; // Vásárló neve
  customer_email?: string; // Vásárló email címe (opcionális)
  items: InvoiceItem[]; // Számla tételek listája
  payment_method: string; // Fizetési mód (pl. "CASH", "CARD", "TRANSFER")
  notes?: string; // Megjegyzések (opcionális)
}

// Számla létrehozás Response
export interface InvoiceCreateResponse {
  success: boolean; // Sikeres volt-e a művelet
  invoice_number?: string; // Generált számla azonosító
  pdf_url?: string; // Számla PDF URL-je
  message?: string; // Üzenet/Hibaüzenet
  order_id: number; // Kapcsolódó rendelés azonosító
}
