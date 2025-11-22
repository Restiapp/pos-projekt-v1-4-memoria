/**
 * Customer típusok - Backend API sémákkal szinkronban
 * Backend: backend/service_crm/schemas/customer.py
 */

// Customer típusok

export interface Customer {
  id: number;
  customer_uid: string; // Vendégszám (pl. "CUST-123456")
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  marketing_consent: boolean;
  sms_consent: boolean;
  birth_date?: string; // ISO datetime string
  notes?: string;
  tags?: string[]; // Customer tags (e.g., ["VIP", "Vegetarian"])
  loyalty_points: number; // Decimal (2 places)
  total_spent: number; // Decimal (2 places) - HUF
  total_orders: number;
  is_active: boolean;
  last_visit?: string; // ISO datetime string
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

export interface CustomerCreate {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  marketing_consent: boolean;
  sms_consent: boolean;
  birth_date?: string; // ISO datetime string
  notes?: string;
  tags?: string[]; // Customer tags
}

export interface CustomerUpdate {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  marketing_consent?: boolean;
  sms_consent?: boolean;
  birth_date?: string; // ISO datetime string
  notes?: string;
  tags?: string[]; // Customer tags
  is_active?: boolean;
}

export interface CustomerListResponse {
  items: Customer[];
  total: number;
  page: number;
  page_size: number;
}

export interface LoyaltyPointsUpdate {
  points: number; // Decimal - positive to add, negative to subtract
  reason?: string;
}
