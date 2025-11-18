/**
 * Finance (Pénzügy) típusdefiníciók
 * Backend API sémáknak megfelelően
 * Backend: backend/service_admin/schemas/finance.py
 */

/**
 * CashMovement (Pénzmozgás) - Backend API response
 */
export interface CashMovement {
  id: number;
  movement_type: string; // "CASH_IN" | "CASH_OUT" | "OPENING_BALANCE"
  amount: number;
  description?: string | null;
  order_id?: number | null;
  employee_id?: number | null;
  daily_closure_id?: number | null;
  created_at: string;
}

/**
 * Készpénz befizetés (POST /api/finance/cash-drawer/deposit)
 * Backend: CashDepositRequest schema
 */
export interface CashDepositRequest {
  amount: number;
  description?: string;
  employee_id?: number;
}

/**
 * Készpénz kivétel (POST /api/finance/cash-drawer/withdraw)
 * Backend: CashWithdrawRequest schema
 */
export interface CashWithdrawRequest {
  amount: number;
  description?: string;
  employee_id?: number;
}

/**
 * DailyClosure (Napi Zárás) - Backend API response
 */
export interface DailyClosure {
  id: number;
  closure_date: string;
  status: string; // "OPEN" | "IN_PROGRESS" | "CLOSED" | "RECONCILED"
  opening_balance: number;
  expected_closing_balance?: number | null;
  actual_closing_balance?: number | null;
  difference?: number | null;
  notes?: string | null;
  closed_by_employee_id?: number | null;
  created_at: string;
  updated_at: string;
  closed_at?: string | null;
}

/**
 * Napi zárás létrehozása (POST /api/finance/daily-closures)
 * Backend: DailyClosureCreate schema
 */
export interface DailyClosureCreateRequest {
  opening_balance: number;
  notes?: string;
  closed_by_employee_id?: number;
}

/**
 * Napi zárás frissítése (PATCH /api/finance/daily-closures/{id}/close)
 * Backend: DailyClosureUpdate schema
 */
export interface DailyClosureUpdateRequest {
  status?: string;
  actual_closing_balance?: number;
  notes?: string;
}

/**
 * Aktuális készpénz egyenleg - Response
 */
export interface CashBalanceResponse {
  balance: number;
  currency: string;
  timestamp: string;
}
