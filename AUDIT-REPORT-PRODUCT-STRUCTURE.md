# AUDIT REPORT: Product Structure & Variations
**Date:** 2025-11-20
**Scope:** Deep analysis of `service_menu` and `service_orders` product handling

---

## EXECUTIVE SUMMARY

A rendszer **alap szinten támogatja** a komplex termékkezelést, de vannak hiányosságok egy professzionális pizzéria működéséhez.

**✅ JÓ HÍREK:**
- ModifierGroup és Modifier rendszer már implementálva van
- Option Groups támogatás min/max választással
- Rendelési tételek tárolják a kiválasztott módosítókat
- API végpontok készen állnak a frontend számára

**⚠️ HIÁNYOSSÁGOK:**
- Nincs dedikált ProductVariation modell (méretek külön kezelése)
- Nincs allergen nyilvántartás
- Nincs "kötelező választás" validáció az API-ban

---

## 1. PRODUCT VARIATIONS (VARIÁCIÓK)

### [STATUS: BASIC]

#### ✅ Amit TALÁLT a rendszer:
- **ModifierGroup model** létezik `selection_type` mezővel
- A modifierek tárolhatnak `price_modifier` értéket (pozitív vagy negatív)
- Példa a sémákban: `"Méret"` mint ModifierGroup

#### ❌ Amit NEM talált:
- **Nincs dedikált `ProductVariation` tábla**
- Nincs "base product + variant" struktúra (pl. Pizza → 32cm variant, 45cm variant)

#### 📍 Jelenlegi megoldás:
**Méretek mint Modifierek kezelése:**
```json
{
  "product_id": 1,
  "name": "Margarita Pizza",
  "base_price": 2000,
  "modifier_groups": [
    {
      "name": "Méret",
      "selection_type": "SINGLE_CHOICE_REQUIRED",
      "min_selection": 1,
      "max_selection": 1,
      "modifiers": [
        {"name": "32cm", "price_modifier": 0},
        {"name": "45cm", "price_modifier": 800}
      ]
    }
  ]
}
```

#### ⚠️ Problémák ezzel a megközelítéssel:
1. **SKU kezelés**: Nincs egyedi SKU a "Margarita 32cm" vs "Margarita 45cm" termékekhez
2. **Készletkezelés**: Nincs külön készlet nyilvántartás méretenként (ha releváns)
3. **Jelentések**: Nehezebb lekérdezni, hogy "hány db 32cm pizza kelt el"
4. **Csatorna-specifikus árak**: A `channel_visibility.price_override` csak a base_price-ra vonatkozik

#### ✅ ELŐNYÖK a modifier-alapú megközelítésnek:
1. **Flexibilitás**: Könnyen lehet módosítani a méreteket
2. **Kombinálhatóság**: Méretek + feltétek együtt kezelhetők
3. **UI építés**: Az API már támogatja a teljes adatstruktúrát

---

## 2. MODIFIERS / TOPPINGS (FELTÉTEK)

### [STATUS: OK]

#### ✅ Teljes támogatás:

**Modellek:**
- `ModifierGroup` (backend/service_menu/models/modifier_group.py:16)
- `Modifier` (backend/service_menu/models/modifier.py:16)
- `product_modifier_group_associations` many-to-many kapcsolat

**Funkciók:**
- ✅ Modifier hozzárendelése termékhez
- ✅ `price_modifier` mező (pozitív vagy negatív érték)
- ✅ `is_default` flag (alapértelmezett kiválasztás)
- ✅ Relationship: Product.modifier_groups

**API Végpontok:**
```
GET    /modifier-groups/{product_id}/modifier-groups?include_modifiers=true
POST   /modifier-groups/modifiers
PUT    /modifier-groups/modifiers/{id}
DELETE /modifier-groups/modifiers/{id}
```

**OrderItem tárolás:**
```python
# backend/service_orders/models/order_item.py:37
selected_modifiers = Column(JSONB, nullable=True)
# Format: [{'group_name': 'Extra feltétek', 'modifier_name': 'Extra sajt', 'price': 150.00}]
```

#### ✅ Példa használat (Pizzéria):
```json
{
  "group_name": "Extra feltétek",
  "selection_type": "MULTIPLE_CHOICE_OPTIONAL",
  "min_selection": 0,
  "max_selection": 8,
  "modifiers": [
    {"name": "Extra sajt", "price_modifier": 150},
    {"name": "Sonka", "price_modifier": 200},
    {"name": "Gomba", "price_modifier": 150}
  ]
}
```

---

## 3. OPTION GROUPS (VÁLASZTÓK)

### [STATUS: OK]

#### ✅ Teljes támogatás a ModifierGroup szinten:

**SelectionType Enum (backend/service_menu/schemas/modifier.py:17):**
```python
class SelectionType(str, Enum):
    SINGLE_CHOICE_REQUIRED = "SINGLE_CHOICE_REQUIRED"
    SINGLE_CHOICE_OPTIONAL = "SINGLE_CHOICE_OPTIONAL"
    MULTIPLE_CHOICE_OPTIONAL = "MULTIPLE_CHOICE_OPTIONAL"
    MULTIPLE_CHOICE_REQUIRED = "MULTIPLE_CHOICE_REQUIRED"
```

**Constraint mezők:**
- `min_selection` (integer, default: 0)
- `max_selection` (integer, default: 1)
- Pydantic validáció: `max_selection >= min_selection`

#### ✅ Use Case példák:

**1. Steak átsütése (Kötelező egyválasztás):**
```json
{
  "name": "Átsütés",
  "selection_type": "SINGLE_CHOICE_REQUIRED",
  "min_selection": 1,
  "max_selection": 1,
  "modifiers": [
    {"name": "Rare", "price_modifier": 0},
    {"name": "Medium", "price_modifier": 0},
    {"name": "Well-done", "price_modifier": 0}
  ]
}
```

**2. Választható köretek (Max 2):**
```json
{
  "name": "Köretek",
  "selection_type": "MULTIPLE_CHOICE_OPTIONAL",
  "min_selection": 0,
  "max_selection": 2,
  "modifiers": [
    {"name": "Hasábburgonya", "price_modifier": 0},
    {"name": "Rizs", "price_modifier": 0},
    {"name": "Sült zöldség", "price_modifier": 200}
  ]
}
```

#### ⚠️ HIÁNYZÓ FUNKCIÓ:
**Backend validáció a rendelés leadásakor:**
- Az `OrderItemCreate` schema NEM validálja, hogy:
  - Kötelező csoportból választottak-e (min_selection)
  - Ne léphessék túl a max_selection értéket

**Javasolt javítás:**
- Backend/service_orders/schemas/order_item.py-ban egyedi validator
- Lekéri a product modifier_groups-ot
- Ellenőrzi a selected_modifiers-t a szabályok alapján

---

## 4. ALLERGENS (ALLERGÉNEK)

### [STATUS: MISSING]

#### ❌ Nincs allergen támogatás:

**Keresési eredmény:**
```bash
grep -ri "allergen" backend/service_menu/
# No matches found
```

**Nincs:**
- `allergens` mező a Product modellben
- `Allergen` dedikált modell
- Many-to-many kapcsolat Product-Allergen között

#### 💡 Javasolt megoldás (Profi szint):

**1. Új modell (backend/service_menu/models/allergen.py):**
```python
class Allergen(Base):
    __tablename__ = 'allergens'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    icon_code = Column(String(50))  # pl. "gluten", "lactose", "nuts"

    # Relationships
    products = relationship(
        'Product',
        secondary='product_allergen_associations',
        back_populates='allergens'
    )
```

**2. Association table:**
```python
product_allergen_associations = Table(
    'product_allergen_associations',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True),
    Column('allergen_id', Integer, ForeignKey('allergens.id'), primary_key=True)
)
```

**3. Product modell bővítés:**
```python
class Product(Base):
    # ... existing fields ...
    allergens = relationship(
        'Allergen',
        secondary='product_allergen_associations',
        back_populates='products'
    )
```

**4. API végpontok:**
```
GET    /allergens
POST   /allergens
GET    /products/{id}/allergens
POST   /products/{id}/allergens/{allergen_id}
DELETE /products/{id}/allergens/{allergen_id}
```

---

## 5. UI READINESS (Frontend felkészültség)

### [STATUS: OK]

#### ✅ A Frontend kap minden szükséges adatot:

**Kritikus endpoint (backend/service_menu/routers/modifier_groups.py:540):**
```
GET /products/{product_id}/modifier-groups?include_modifiers=true
```

**Válasz struktúra:**
```json
[
  {
    "id": 1,
    "name": "Méret",
    "selection_type": "SINGLE_CHOICE_REQUIRED",
    "min_selection": 1,
    "max_selection": 1,
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-15T10:00:00Z",
    "modifiers": [
      {
        "id": 1,
        "group_id": 1,
        "name": "32cm",
        "price_modifier": 0.00,
        "is_default": true,
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-01-15T10:00:00Z"
      },
      {
        "id": 2,
        "group_id": 1,
        "name": "45cm",
        "price_modifier": 800.00,
        "is_default": false,
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-01-15T10:00:00Z"
      }
    ]
  },
  {
    "id": 2,
    "name": "Extra feltétek",
    "selection_type": "MULTIPLE_CHOICE_OPTIONAL",
    "min_selection": 0,
    "max_selection": 8,
    "modifiers": [...]
  }
]
```

#### ✅ Pizza Builder UI implementálható:

**A frontend ezekkel tudja építeni:**
1. **Selection Type alapján UI elem választás:**
   - SINGLE_CHOICE → Radio buttons
   - MULTIPLE_CHOICE → Checkboxes
   - REQUIRED → Kötelező jelölés (*) megjelenítése

2. **Min/Max validáció kliens oldalon:**
   - Gomb disable, ha min_selection nincs teljesítve
   - Checkbox disable, ha max_selection elérve

3. **Dinamikus árak:**
   - Base price + sum(selected_modifiers.price_modifier)
   - Real-time ár update a kiválasztás során

4. **Default kiválasztás:**
   - `is_default: true` modifierek előre bejelölve

---

## 6. ÖSSZEFOGLALÓ ÉRTÉKELÉS

| Funkció | Státusz | Megjegyzés |
|---------|---------|------------|
| **Product Variations** | ⚠️ BASIC | Modifierként működik, de nincs dedikált ProductVariation modell |
| **Modifiers / Toppings** | ✅ OK | Teljes támogatás, price_modifier, is_default |
| **Option Groups** | ✅ OK | SelectionType enum, min/max selection támogatás |
| **Backend Validation** | ⚠️ BASIC | OrderItem NEM validálja a modifier szabályokat |
| **Allergens** | ❌ MISSING | Nincs allergen nyilvántartás |
| **UI Readiness** | ✅ OK | API-k teljes mértékben támogatják a Pizza Builder UI-t |

---

## 7. JAVASLATOK A "PROFI" SZINTHEZ

### PRIORITÁS 1 (Kritikus hiányosságok):

#### A. Backend validáció OrderItem-ben
**Lokáció:** `backend/service_orders/schemas/order_item.py`

**Implementáció:**
```python
from pydantic import field_validator
from backend.service_menu.services.modifier_service import ModifierService

class OrderItemCreate(OrderItemBase):

    @field_validator('selected_modifiers')
    @classmethod
    def validate_modifiers(cls, v, info):
        """Validálja, hogy a kiválasztott modifierek megfelelnek a szabályoknak."""
        if not v:
            return v

        # Get product_id from the model
        product_id = info.data.get('product_id')
        if not product_id:
            return v

        # Fetch modifier groups for this product (requires DB session)
        # CRITICAL: Ez BackgroundTask-ban vagy route-ban kell történjen!
        # Pydantic validatorban nincs DB session!

        return v
```

**MEGJEGYZÉS:** A fenti megközelítés korlátozott, mert Pydantic validator-ban nincs DB session. Jobb megoldás:

**Route-szintű validáció (backend/service_orders/routers/order_items.py):**
```python
@router.post("/order-items")
def create_order_item(
    item_data: OrderItemCreate,
    db: Session = Depends(get_db_connection)
):
    # 1. Fetch product with modifier_groups
    product = ProductService.get_product_by_id(db, item_data.product_id)

    # 2. Validate selected_modifiers against modifier_groups rules
    validate_modifier_selection(product, item_data.selected_modifiers)

    # 3. Create order item
    return OrderItemService.create_order_item(db, item_data)
```

#### B. Allergen támogatás hozzáadása
**Lásd: Fejezet 4. "Javasolt megoldás"**

---

### PRIORITÁS 2 (Opcionális fejlesztések):

#### C. ProductVariation dedikált modell
**Cél:** Külön SKU és készlet méretekenként

**Modell struktúra:**
```python
class ProductVariation(Base):
    __tablename__ = 'product_variations'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    name = Column(String(100))  # "32cm", "45cm"
    sku = Column(String(100), unique=True)
    price_override = Column(Numeric(10, 2), nullable=True)
    is_default = Column(Boolean, default=False)
    stock_quantity = Column(Integer, default=0)  # Ha készletkezelés szükséges

    # Relationships
    product = relationship('Product', back_populates='variations')
```

**Előnyök:**
- Egyedi SKU méretenként
- Készletkezelés támogatása
- Könnyebb jelentések ("32cm pizza eladások")
- Channel-specifikus árazás variáns szinten

**Hátrányok:**
- Komplexebb adatmodell
- Migrálás szükséges a jelenlegi modifier-alapú rendszerből

---

#### D. Modifier Group sorrend
**Cél:** UI-ban meghatározott sorrendben jelenjenek meg a csoportok

**Megoldás:**
```python
class ModifierGroup(Base):
    # ... existing fields ...
    display_order = Column(Integer, default=0)  # Új mező
```

**API módosítás:**
```python
# backend/service_menu/services/modifier_service.py
def get_modifier_groups_by_product(db, product_id, include_modifiers=False):
    groups = product.modifier_groups
    # Rendezés display_order szerint
    groups = sorted(groups, key=lambda g: g.display_order)
    return groups
```

---

#### E. Modifier képek támogatása
**Cél:** Vizuális feltét kiválasztás

**Megoldás:**
```python
class Modifier(Base):
    # ... existing fields ...
    image_url = Column(String(500), nullable=True)
```

---

## 8. KONKLÚZIÓ

### ✅ A RENDSZER KÉPES-E PIZZÉRIA MŰKÖDTETÉSÉRE?

**IGEN**, de alapszinten.

**Ami működik most:**
- Pizza méretek kezelése modifierként (32cm/45cm)
- Extra feltétek hozzáadása árakkal
- Kötelező választások (pl. átsütés)
- Max feltét limit (pl. max 8 topping)
- Rendelések tárolják a kiválasztásokat

**Ami hiányzik a "profi" szinthez:**
- ❌ Allergen nyilvántartás
- ⚠️ Backend validáció a modifier szabályokra
- ⚠️ Dedikált produktum variációk (opcionális)

---

## 9. KÖVETKEZŐ LÉPÉSEK

### Ajánlott implementációs sorrend:

1. **[KRITIKUS]** Backend validáció hozzáadása OrderItem-hez
   - Fájl: `backend/service_orders/routers/order_items.py`
   - Funkció: `validate_modifier_selection()`

2. **[MAGAS]** Allergen modell és API hozzáadása
   - Új fájlok: `models/allergen.py`, `schemas/allergen.py`, `routers/allergens.py`
   - Migration script szükséges

3. **[KÖZEPES]** Modifier Group display_order mező
   - Migration + API módosítás

4. **[ALACSONY]** ProductVariation modell (csak ha készletkezelés szükséges)

---

**Készítette:** Claude Code Agent
**Audit ID:** AUDIT-MENU-DEEP-20251120
