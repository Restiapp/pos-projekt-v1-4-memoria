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

## 📋 V3.0 Fázis 3 Lezárása - NAV OSA & Logistics Integration

A V3.0 Fázis 3 (Háttér Műveletek) során két új branch került integrálásra:
- ✅ `claude/feature-v3-nav-osa-inventory-trigger-01Y9VpDMbYkBhQajBaQRsfbB` - NAV OSA & Inventory Trigger
- ✅ `claude/feature-v3-logistics-zip-fix-01PEcN8oFpPVKc5Lr7W5WQMi` - Logistics Integration (Zip Code)

Az alábbi feladatok maradtak fel további fázisokra:

---

### TODO_V3 Frissítés (Service Logistics)

- [x] ~~**(Fázis 3)** A service_logistics `POST /zones/get-by-address` MOCK végpontját cserélje le valós Google Maps/GeoJSON logikára.~~ ✅ **DONE** (F3.B: ZIP kód alapú zóna keresés implementálva)
- [ ] **(Fázis 4)** A service_logistics courier modelljét bővíteni kell GPS koordinátákkal (a V3.0 terv 4.6-os pontja szerint).
- [ ] **(Fázis 4)** A service_logistics `get_zone_by_zip_code` funkciója jelenleg ZIP kód listát használ. Ezt cserélni kell valós GeoJSON/Google Maps API logikára.

---

### TODO_V3 Frissítés (Service CRM)

- [ ] **(Fázis 4)** A service_crm-ből még hiányzik a **GiftCard Service/Router réteg** implementációja.
- [ ] **(Fázis 4)** A service_crm-ből még hiányzik az **Address Service/Router réteg** implementációja.
- [ ] **(Fázis 4)** A Customer modellt bővíteni kell a `customer_uid` ("vendégszám") mezővel.

---

### TODO_V3 Frissítés (Service Orders)

- [x] ~~**(Fázis 3)** A `change_order_type` metódusban a **MOCK HTTP hívásokat** (service_inventory és service_logistics felé) valós hívásokra kell cserélni.~~ ✅ **DONE** (F3.B: service_logistics integráció elkészült)
- [ ] **(Fázis 4)** A service_orders `change_order_type` metódusa még nem hívja a service_inventory-t (ital/fagyi ellenőrzés).

---

### TODO_V3 Frissítés (Service Inventory/Orders)

- [ ] **(Fázis 4)** A service_inventory `nav_osa_service.py` MOCK végpontját valós NAV API hívásra kell cserélni.
- [ ] **(Fázis 3)** A service_orders `close_order` metódusában a készletcsökkentés hibakezelését (Graceful Failure) ellenőrizni kell.

---

## 🎯 Összegzés

**Fázis 2 Statisztika:**
- 3 branch merged
- +2,340 sor kód hozzáadva
- 16 új fájl létrehozva
- 6 jövőbeli TODO azonosítva

**Fázis 3 Statisztika:**
- 2 branch merged
- +1,334 sor kód hozzáadva
- 12 új fájl létrehozva
- 2 TODO befejezve, 4 új TODO azonosítva

**Következő Fázis (Fázis 4 - Finomhangolás):**
- GiftCard & Address Service/Router implementálása (CRM)
- Customer UID mező hozzáadása
- NAV OSA valós API integráció
- Google Maps GeoJSON valós API
- Courier GPS tracking

---

**Utoljára Frissítette:** Claude Code AI (Integrátor Protokoll)
**Git Branch:** main
**Commit Context:** Post-Fázis 3 Integration
**Dátum:** 2025-01-18
