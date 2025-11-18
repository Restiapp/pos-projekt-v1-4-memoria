### Audit Jelentés: service_crm / Vendégszám (Customer UID) Integráció
* Állapot: STABIL
* Részletes Elemzés:
    * **backend/service_crm/models/customer.py**: A `customer_uid` mező helyesen van definiálva `String(50)` típussal, `unique=True` és `nullable=False` megszorításokkal. Az adatbázis-séma konzisztens.
    * **backend/service_crm/services/customer_service.py**: A `create_customer` metódus sikeresen generál egyedi `customer_uid`-t a `_generate_customer_uid` privát metódus segítségével. A `get_customer_by_uid` metódus szintén helyesen működik.
    * **frontend/src/components/admin/CustomerList.tsx**: A "Vendégszám" oszlop helyesen jeleníti meg a `customer_uid`-t a vásárlói listában.
    * **service_orders/models/order.py**: A `Order` modell helyesen, a `customer_id` mezőn keresztül hivatkozik a vásárlóra, ami konzisztens a `Customer` modell `id` elsődleges kulcsával.

* Következtetés: A `customer_uid` integrációja a `service_crm` és a `service_orders` mikroszolgáltatások, valamint a frontend komponensek között konzisztens és stabil. Nem találtam hibát.
