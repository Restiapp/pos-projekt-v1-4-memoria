# 📋 FÁZIS 3 - IMPLEMENTÁCIÓS TERV ÉS TELJES KÓDOK

**V3.0 - Háttér Műveletek (NAV OSA és Zárások)**
**Verzió:** 1.0
**Dátum:** 2025-11-18
**Tervező Ágens:** Sonnet 4.5 (Planner)
**Branch:** `claude/phase-3-planning-01NsfmDJkXnHzNrCtujCi2Bt`

---

## 🎯 EXECUTIVE SUMMARY

A **Fázis 3** célja a V3.0 Master Plan háttérműveleteinek megvalósítása. A következő három fő területet fedezi le:

### **1. NAV OSA Valós API Integráció** (service_inventory)
**JAVASLAT:** A NAV OSA valós integráció rendkívül összetett feladat (XML schema, kriptográfia, NAV technikai user credentials szükséges). **Javasoljuk a Fázis 4-re halasztani**, mivel:
- Jelenleg MOCK implementáció teljesen funkcionális tesztelésre
- NAV technikai felhasználó credentials szükséges
- NAV teszt környezet hozzáférés szükséges
- A Fázis 3 többi modulja (Finance, Assets, Vehicles UI) nem függnek ettől

### **2. Finance UI (Komplex Zárások)** (frontend + service_admin)
✅ **IMPLEMENTÁLANDÓ EBBEN A FÁZISBAN**
- Backend API: **KÉSZ** (models, services, routers, schemas)
- Frontend UI: **HIÁNYZIK** → Teljes implementáció szükséges
- Komponensek: FinancePage, CashDrawer, DailyClosureList, DailyClosureEditor
- Funkciók: Készpénz be/kivétel, napi pénztárzárás, egyenleg nyomon követése

### **3. Assets & Vehicles (Tárgyi Eszközök és Járművek)** (Backend API + Frontend UI)
✅ **IMPLEMENTÁLANDÓ EBBEN A FÁZISBAN**
- Backend Models: **KÉSZ** (adatbázis struktúra)
- Backend API: **HIÁNYZIK** → Routers, Services, Schemas
- Frontend UI: **HIÁNYZIK** → Teljes implementáció
- Komponensek: AssetList, VehicleList, szerviz/tankolás nyilvántartás

---

## 📊 JELENLEGI ÁLLAPOT ELEMZÉSE

### ✅ **Kész Komponensek**
```
✓ service_inventory: NAV OSA MOCK (teljes infrastruktúra - osa_integration_router.py)
✓ service_admin: Finance Backend API (models/finance.py, routers/finance.py, services/finance_service.py, schemas/finance.py)
✓ service_admin: Assets Models (models/assets.py - AssetGroup, Asset, AssetService)
✓ service_admin: Vehicles Models (models/vehicles.py - Vehicle, VehicleRefueling, VehicleMaintenance)
✓ Frontend: Admin Dashboard struktúra (AdminPage.tsx, App.tsx routing)
✓ Frontend: CRM komponensek (CustomerList, CouponList, GiftCardList)
✓ Frontend: RBAC komponensek (EmployeeList, RoleList)
```

### ❌ **Hiányzó Komponensek**
```
✗ service_inventory: Valós NAV API implementáció → Fázis 4-re halasztva
✗ service_admin: Assets Backend API (routers/assets.py, services/asset_service.py, schemas/assets.py)
✗ service_admin: Vehicles Backend API (routers/vehicles.py, services/vehicle_service.py, schemas/vehicles.py)
✗ Frontend: Finance UI (teljes - services, types, komponensek)
✗ Frontend: Assets UI (teljes - services, types, komponensek)
✗ Frontend: Vehicles UI (teljes - services, types, komponensek)
```

---

## 🚀 RÉSZLETES FELADATLISTA (Prioritási Sorrend)

### **PRIORITÁS 1: MODUL 2 - Finance UI**

| # | Fájl | Feladat | Becslés | Státusz |
|---|------|---------|---------|---------|
| 2.1 | `frontend/src/types/finance.ts` | TypeScript típusok (CashMovement, DailyClosure) | 15 perc | TODO |
| 2.2 | `frontend/src/services/financeService.ts` | API wrapper (cash drawer, daily closures) | 30 perc | TODO |
| 2.3 | `frontend/src/pages/FinancePage.tsx` | Finance főoldal (dashboard, tabs) | 1 óra | TODO |
| 2.4 | `frontend/src/components/finance/CashDrawer.tsx` | Készpénz be/kivétel UI | 1.5 óra | TODO |
| 2.5 | `frontend/src/components/finance/DailyClosureList.tsx` | Napi zárások listázása | 1 óra | TODO |
| 2.6 | `frontend/src/components/finance/DailyClosureEditor.tsx` | Napi zárás szerkesztő modal | 1.5 óra | TODO |
| 2.7 | `frontend/src/components/finance/Finance.css` | Stílusok | 30 perc | TODO |
| 2.8 | `frontend/src/pages/AdminPage.tsx` | Finance menüpont hozzáadása | 5 perc | TODO |
| 2.9 | `frontend/src/App.tsx` | `/admin/finance` routing | 10 perc | TODO |

**Modul 2 Teljes Időbecslés:** ~6.5 óra

---

### **PRIORITÁS 2: MODUL 3 - Assets Backend API**

| # | Fájl | Feladat | Becslés | Státusz |
|---|------|---------|---------|---------|
| 3.1 | `backend/service_admin/schemas/assets.py` | Pydantic schemák | 45 perc | TODO |
| 3.2 | `backend/service_admin/services/asset_service.py` | Business logika (CRUD, groups, services) | 1.5 óra | TODO |
| 3.3 | `backend/service_admin/routers/assets.py` | API endpointok | 1 óra | TODO |
| 3.4 | `backend/service_admin/main.py` | Router regisztráció | 5 perc | TODO |

**Modul 3 Teljes Időbecslés:** ~3.5 óra

---

### **PRIORITÁS 3: MODUL 4 - Assets Frontend UI**

| # | Fájl | Feladat | Becslés | Státusz |
|---|------|---------|---------|---------|
| 4.1 | `frontend/src/types/asset.ts` | TypeScript típusok | 15 perc | TODO |
| 4.2 | `frontend/src/services/assetService.ts` | API wrapper | 30 perc | TODO |
| 4.3 | `frontend/src/components/admin/AssetList.tsx` | Eszközök listázása | 1.5 óra | TODO |
| 4.4 | `frontend/src/components/admin/AssetEditor.tsx` | Eszköz szerkesztő modal | 1.5 óra | TODO |
| 4.5 | `frontend/src/components/admin/AssetServiceList.tsx` | Szerviz előzmények | 1 óra | TODO |
| 4.6 | `frontend/src/components/admin/AssetList.css` | Stílusok | 30 perc | TODO |
| 4.7 | `frontend/src/pages/AdminPage.tsx` | Assets menüpont hozzáadása | 5 perc | TODO |
| 4.8 | `frontend/src/App.tsx` | `/admin/assets` routing | 10 perc | TODO |

**Modul 4 Teljes Időbecslés:** ~5.5 óra

---

### **PRIORITÁS 4: MODUL 5 - Vehicles Backend API**

| # | Fájl | Feladat | Becslés | Státusz |
|---|------|---------|---------|---------|
| 5.1 | `backend/service_admin/schemas/vehicles.py` | Pydantic schemák | 45 perc | TODO |
| 5.2 | `backend/service_admin/services/vehicle_service.py` | Business logika (CRUD, refueling, maintenance) | 1.5 óra | TODO |
| 5.3 | `backend/service_admin/routers/vehicles.py` | API endpointok | 1 óra | TODO |
| 5.4 | `backend/service_admin/main.py` | Router regisztráció | 5 perc | TODO |

**Modul 5 Teljes Időbecslés:** ~3.5 óra

---

### **PRIORITÁS 5: MODUL 6 - Vehicles Frontend UI**

| # | Fájl | Feladat | Becslés | Státusz |
|---|------|---------|---------|---------|
| 6.1 | `frontend/src/types/vehicle.ts` | TypeScript típusok | 15 perc | TODO |
| 6.2 | `frontend/src/services/vehicleService.ts` | API wrapper | 30 perc | TODO |
| 6.3 | `frontend/src/components/admin/VehicleList.tsx` | Járművek listázása | 1.5 óra | TODO |
| 6.4 | `frontend/src/components/admin/VehicleEditor.tsx` | Jármű szerkesztő modal | 1.5 óra | TODO |
| 6.5 | `frontend/src/components/admin/RefuelingList.tsx` | Tankolási előzmények | 1 óra | TODO |
| 6.6 | `frontend/src/components/admin/MaintenanceList.tsx` | Karbantartási előzmények | 1 óra | TODO |
| 6.7 | `frontend/src/components/admin/VehicleList.css` | Stílusok | 30 perc | TODO |
| 6.8 | `frontend/src/pages/AdminPage.tsx` | Vehicles menüpont hozzáadása | 5 perc | TODO |
| 6.9 | `frontend/src/App.tsx` | `/admin/vehicles` routing | 10 perc | TODO |

**Modul 6 Teljes Időbecslés:** ~5.5 óra

---

## ⏱️ ÖSSZESÍTETT IDŐBECSLÉS

```
Modul 2 (Finance UI):        ~6.5 óra
Modul 3 (Assets Backend):    ~3.5 óra
Modul 4 (Assets Frontend):   ~5.5 óra
Modul 5 (Vehicles Backend):  ~3.5 óra
Modul 6 (Vehicles Frontend): ~5.5 óra
─────────────────────────────────────
TELJES FÁZIS 3:              ~24.5 óra (≈3 munkanap)
```

---

## 📦 TELJES KÓDIMPLEMENTÁCIÓK

A következő szekciókban található **az összes új/módosított fájl teljes kódja**, amelyeket a Végrehajtó Ágens közvetlenül használhat.

---


## 💰 MODUL 2: FINANCE UI - TELJES IMPLEMENTÁCIÓ

---

### 📄 2.1. `frontend/src/types/finance.ts` (ÚJ FÁJL)

```typescript
/**
 * Finance Types - TypeScript típusdefiníciók a pénzügyi modulhoz
 */

export enum CashMovementType {
  OPENING_BALANCE = 'OPENING_BALANCE',
  CASH_IN = 'CASH_IN',
  CASH_OUT = 'CASH_OUT',
  SALE = 'SALE',
  REFUND = 'REFUND',
  CORRECTION = 'CORRECTION',
}

export enum ClosureStatus {
  OPEN = 'OPEN',
  IN_PROGRESS = 'IN_PROGRESS',
  CLOSED = 'CLOSED',
  RECONCILED = 'RECONCILED',
}

export interface CashMovement {
  id: number;
  movement_type: CashMovementType;
  amount: number;
  description?: string;
  order_id?: number;
  employee_id?: number;
  daily_closure_id?: number;
  created_at: string;
}

export interface DailyClosure {
  id: number;
  closure_date: string;
  status: ClosureStatus;
  opening_balance: number;
  expected_closing_balance?: number;
  actual_closing_balance?: number;
  difference?: number;
  notes?: string;
  closed_by_employee_id?: number;
  created_at: string;
  updated_at: string;
  closed_at?: string;
}

// Request payloads
export interface CashDepositRequest {
  amount: number;
  description?: string;
  employee_id?: number;
}

export interface CashWithdrawRequest {
  amount: number;
  description?: string;
  employee_id?: number;
}

export interface DailyClosureCreateRequest {
  opening_balance: number;
  notes?: string;
  closed_by_employee_id?: number;
}

export interface DailyClosureUpdateRequest {
  status?: ClosureStatus;
  actual_closing_balance?: number;
  notes?: string;
}

// API Responses
export interface CashBalanceResponse {
  balance: number;
  currency: string;
  timestamp: string;
}
```

---

### 📄 2.2. `frontend/src/services/financeService.ts` (ÚJ FÁJL)

```typescript
/**
 * Finance Service - API wrapper a pénzügyi műveletekhez
 */

import axios from 'axios';
import type {
  CashDepositRequest,
  CashWithdrawRequest,
  DailyClosureCreateRequest,
  DailyClosureUpdateRequest,
  CashMovement,
  DailyClosure,
  CashBalanceResponse,
} from '@/types/finance';

const API_URL = import.meta.env.VITE_ADMIN_API_URL || 'http://localhost:8008/api/v1';

// Helper: Authorization header
const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token');
  return {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  };
};

// ============================================================================
// Cash Drawer Operations
// ============================================================================

/**
 * Készpénz befizetés rögzítése
 */
export const cashDeposit = async (data: CashDepositRequest): Promise<CashMovement> => {
  const response = await axios.post<CashMovement>(
    `${API_URL}/finance/cash-drawer/deposit`,
    data,
    getAuthHeaders()
  );
  return response.data;
};

/**
 * Készpénz kivétel rögzítése
 */
export const cashWithdraw = async (data: CashWithdrawRequest): Promise<CashMovement> => {
  const response = await axios.post<CashMovement>(
    `${API_URL}/finance/cash-drawer/withdraw`,
    data,
    getAuthHeaders()
  );
  return response.data;
};

/**
 * Aktuális készpénz egyenleg lekérdezése
 */
export const getCashBalance = async (): Promise<CashBalanceResponse> => {
  const response = await axios.get<CashBalanceResponse>(
    `${API_URL}/finance/cash-drawer/balance`,
    getAuthHeaders()
  );
  return response.data;
};

// ============================================================================
// Daily Closure Operations
// ============================================================================

/**
 * Új napi zárás létrehozása
 */
export const createDailyClosure = async (
  data: DailyClosureCreateRequest
): Promise<DailyClosure> => {
  const response = await axios.post<DailyClosure>(
    `${API_URL}/finance/daily-closures`,
    data,
    getAuthHeaders()
  );
  return response.data;
};

/**
 * Napi zárás lezárása
 */
export const closeDailyClosure = async (
  closureId: number,
  data: DailyClosureUpdateRequest
): Promise<DailyClosure> => {
  const response = await axios.patch<DailyClosure>(
    `${API_URL}/finance/daily-closures/${closureId}/close`,
    data,
    getAuthHeaders()
  );
  return response.data;
};

/**
 * Napi zárások listázása (szűrőkkel)
 */
export const getDailyClosures = async (params?: {
  start_date?: string;
  end_date?: string;
  status?: string;
  limit?: number;
  offset?: number;
}): Promise<DailyClosure[]> => {
  const response = await axios.get<DailyClosure[]>(
    `${API_URL}/finance/daily-closures`,
    {
      ...getAuthHeaders(),
      params,
    }
  );
  return response.data;
};

/**
 * Egy adott napi zárás részleteinek lekérdezése
 */
export const getDailyClosureById = async (closureId: number): Promise<DailyClosure> => {
  const response = await axios.get<DailyClosure>(
    `${API_URL}/finance/daily-closures/${closureId}`,
    getAuthHeaders()
  );
  return response.data;
};
```

---

### 📄 2.3. `frontend/src/pages/FinancePage.tsx` (ÚJ FÁJL)

```typescript
/**
 * FinancePage - Pénzügyi adminisztráció főoldala
 * 
 * Funkciók:
 *   - Tab navigáció (Pénztár / Napi Zárások)
 *   - Aktuális egyenleg kijelzése
 *   - Sub-komponensek renderelése
 */

import { useState } from 'react';
import { CashDrawer } from '@/components/finance/CashDrawer';
import { DailyClosureList } from '@/components/finance/DailyClosureList';
import './FinancePage.css';

type FinanceTab = 'cash-drawer' | 'daily-closures';

export const FinancePage = () => {
  const [activeTab, setActiveTab] = useState<FinanceTab>('cash-drawer');

  return (
    <div className="finance-page">
      {/* Fejléc */}
      <header className="finance-header">
        <h1>💰 Pénzügy</h1>
        <p className="finance-description">Készpénz kezelése és napi pénztárzárások</p>
      </header>

      {/* Tab navigáció */}
      <div className="finance-tabs">
        <button
          className={`tab-button ${activeTab === 'cash-drawer' ? 'active' : ''}`}
          onClick={() => setActiveTab('cash-drawer')}
        >
          💵 Pénztár
        </button>
        <button
          className={`tab-button ${activeTab === 'daily-closures' ? 'active' : ''}`}
          onClick={() => setActiveTab('daily-closures')}
        >
          📊 Napi Zárások
        </button>
      </div>

      {/* Tab tartalom */}
      <div className="finance-content">
        {activeTab === 'cash-drawer' && <CashDrawer />}
        {activeTab === 'daily-closures' && <DailyClosureList />}
      </div>
    </div>
  );
};
```

---

### 📄 2.4. `frontend/src/components/finance/CashDrawer.tsx` (ÚJ FÁJL)

```typescript
/**
 * CashDrawer - Pénztár műveletek komponens
 * 
 * Funkciók:
 *   - Aktuális egyenleg megjelenítése
 *   - Készpénz befizetés rögzítése
 *   - Készpénz kivétel rögzítése
 *   - Automatikus frissítés művelet után
 */

import { useState, useEffect } from 'react';
import { getCashBalance, cashDeposit, cashWithdraw } from '@/services/financeService';
import type { CashDepositRequest, CashWithdrawRequest } from '@/types/finance';
import '../finance/Finance.css';

export const CashDrawer = () => {
  const [balance, setBalance] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);

  // Befizetés/Kivétel form state
  const [operation, setOperation] = useState<'deposit' | 'withdraw'>('deposit');
  const [amount, setAmount] = useState<string>('');
  const [description, setDescription] = useState<string>('');

  // Egyenleg betöltése
  const fetchBalance = async () => {
    try {
      setIsLoading(true);
      const response = await getCashBalance();
      setBalance(response.balance);
    } catch (error) {
      console.error('Hiba az egyenleg lekérdezésekor:', error);
      alert('Nem sikerült betölteni az egyenleget!');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchBalance();
  }, []);

  // Form submit kezelése
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const numAmount = parseFloat(amount);
    if (isNaN(numAmount) || numAmount <= 0) {
      alert('Érvénytelen összeg!');
      return;
    }

    try {
      setIsProcessing(true);

      if (operation === 'deposit') {
        const payload: CashDepositRequest = {
          amount: numAmount,
          description: description || undefined,
        };
        await cashDeposit(payload);
        alert('Befizetés sikeresen rögzítve!');
      } else {
        const payload: CashWithdrawRequest = {
          amount: numAmount,
          description: description || undefined,
        };
        await cashWithdraw(payload);
        alert('Kivétel sikeresen rögzítve!');
      }

      // Form reset és egyenleg frissítése
      setAmount('');
      setDescription('');
      await fetchBalance();
    } catch (error: any) {
      console.error('Hiba a művelet során:', error);
      alert(error.response?.data?.detail || 'Nem sikerült a művelet!');
    } finally {
      setIsProcessing(false);
    }
  };

  // Ár formázás
  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('hu-HU', {
      style: 'currency',
      currency: 'HUF',
      minimumFractionDigits: 0,
    }).format(price);
  };

  return (
    <div className="cash-drawer">
      {/* Aktuális egyenleg */}
      <div className="balance-card">
        <h2>💵 Aktuális Egyenleg</h2>
        {isLoading ? (
          <div className="loading">Betöltés...</div>
        ) : (
          <div className="balance-amount">{formatPrice(balance)}</div>
        )}
        <button onClick={fetchBalance} className="refresh-btn" disabled={isLoading}>
          🔄 Frissítés
        </button>
      </div>

      {/* Befizetés/Kivétel Form */}
      <div className="cash-operation-card">
        <h3>Pénzmozgás Rögzítése</h3>

        {/* Művelet választó */}
        <div className="operation-selector">
          <button
            type="button"
            className={`operation-btn ${operation === 'deposit' ? 'active' : ''}`}
            onClick={() => setOperation('deposit')}
          >
            ➕ Befizetés
          </button>
          <button
            type="button"
            className={`operation-btn ${operation === 'withdraw' ? 'active' : ''}`}
            onClick={() => setOperation('withdraw')}
          >
            ➖ Kivétel
          </button>
        </div>

        <form onSubmit={handleSubmit} className="cash-form">
          {/* Összeg */}
          <div className="form-group">
            <label htmlFor="amount">Összeg (Ft) *</label>
            <input
              id="amount"
              type="number"
              min="1"
              step="1"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="10000"
              required
              disabled={isProcessing}
            />
          </div>

          {/* Leírás */}
          <div className="form-group">
            <label htmlFor="description">Leírás</label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Pl. Bankból befizetés, Kiadások fedezése"
              rows={3}
              disabled={isProcessing}
            />
          </div>

          {/* Submit gomb */}
          <button
            type="submit"
            className={`submit-btn ${operation === 'withdraw' ? 'withdraw' : 'deposit'}`}
            disabled={isProcessing}
          >
            {isProcessing
              ? 'Feldolgozás...'
              : operation === 'deposit'
              ? '➕ Befizetés Rögzítése'
              : '➖ Kivétel Rögzítése'}
          </button>
        </form>
      </div>
    </div>
  );
};
```

