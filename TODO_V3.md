# TODO_V3 - V3.0 Master Plan Technical Debt & Future Tasks

**Verzió:** 3.0
**Utolsó Frissítés:** 2025-01-18
**Státusz:** ACTIVE

---

## 📋 V3.0 Fázis 2 Lezárása - Fennmaradó Feladatok

A V3.0 Fázis 2 (Kiszállítási Ökoszisztéma) során három új branch került integrálásra:
- ✅ `claude/feature-v3-logistics-build-2a-01DDyG2W8LDhgaY96hb3tUdK` - service_logistics API/Service
- ✅ `claude/add-giftcard-schema-01LTRkkd5R29yNHYKv2sHhNV` - service_crm GiftCard Schema
- ✅ `claude/feature-v3-orders-change-type-01EbMzrmDGg4dNq1DzQSjiRN` - service_orders Change Type Logic

Az alábbi feladatok maradtak fel további fázisokra:

---

### TODO_V3 Frissítés (Service Logistics)

- [ ] **(Fázis 3)** A service_logistics `POST /zones/get-by-address` MOCK végpontját cserélje le valós Google Maps/GeoJSON logikára.
- [ ] **(Fázis 4)** A service_logistics courier modelljét bővíteni kell GPS koordinátákkal (a V3.0 terv 4.6-os pontja szerint).

---

### TODO_V3 Frissítés (Service CRM)

- [ ] **(Fázis 4)** A service_crm-ből még hiányzik a **GiftCard Service/Router réteg** implementációja.
- [ ] **(Fázis 4)** A service_crm-ből még hiányzik az **Address Service/Router réteg** implementációja.
- [ ] **(Fázis 4)** A Customer modellt bővíteni kell a `customer_uid` ("vendégszám") mezővel.

---

### TODO_V3 Frissítés (Service Orders)

- [ ] **(Fázis 3)** A `change_order_type` metódusban a **MOCK HTTP hívásokat** (service_inventory és service_logistics felé) valós hívásokra kell cserélni.

---

## 🎯 Összegzés

**Fázis 2 Statisztika:**
- 3 branch merged
- +2340 sor kód hozzáadva
- 16 új fájl létrehozva
- 6 jövőbeli TODO azonosítva

**Következő Fázis (Fázis 3 - Háttér Műveletek):**
- Inventory Recipe Engine
- Valós API integrációk (MOCK-ok lecserélése)
- Google Maps GeoJSON integráció
- Supplier Management

---

**Utoljára Frissítette:** Claude Code AI (Integrátor Protokoll)
**Git Branch:** main
**Commit Context:** Post-Fázis 2 Integration
