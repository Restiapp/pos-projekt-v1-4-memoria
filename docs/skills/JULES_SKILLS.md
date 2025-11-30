# JULES SKILLS & GUIDELINES

**Version:** 1.0
**Last Updated:** 2025-11-30
**Agent Type:** Backend Developer / System Architect (Python, FastAPI, PostgreSQL)

---

## 1. Fo specifikaciok - MINDIG EZEKET OLVASD EL ELOSZOR

| Dokumentum | Cel |
|------------|-----|
| `docs/spec/SYSTEM_MASTER_SPEC_V1.md` | Rendszer fo logika |
| `docs/spec/ARCHITECTURE_TARGET_V1.md` | Backend architektura |
| `docs/ui-ux/UI_UX_FOUNDATION.md` | Design & UI elvek (frontend kontextushoz) |

### Modul-specifikus doksik:
- **Floorplan**: `docs/spec/FLOORPLAN_DOMAIN_V1.md`
- **Vendegter / felszolgalo**: `docs/spec/GUEST_FLOOR_ORDERS_SPEC_V1.md`
- **Fizetes / ÁFA**: `docs/spec/PAYMENT_FLOW_V1.md`

---

## 2. Backend fokusz

### 2.1 Technologia stack
- **Python 3.11+**
- **FastAPI** - REST API framework
- **SQLAlchemy 2.0** - ORM
- **PostgreSQL 15** - Adatbazis
- **Alembic** - Migraciok
- **Pydantic** - Validacio, schemak

### 2.2 Microservice architektura

| Service | Port | Felelosseg |
|---------|------|------------|
| `service_menu` | 8001 | Termekek, kategoriak, receptek |
| `service_orders` | 8002 | Rendelesek, asztalok, KDS, fizetesek |
| `service_inventory` | 8003 | Keszlet, mozgasok, hulladek |
| `service_crm` | 8004 | Vendegelek, husegpont |
| `service_logistics` | 8005 | Szallitas, zonak, futarok |
| `service_admin` | 8008 | RBAC, felhasznalok, penzugyi naplo |

### 2.3 Adatmodellek tulajdonlasa

- `service_orders` BIRTOKOL: Order, OrderItem, Table, Room, Bill, KdsTicket
- `service_menu` BIRTOKOL: Product, Category, ModifierGroup, Recipe
- `service_inventory` BIRTOKOL: Ingredient, StockLevel, StockMovement
- `service_admin` BIRTOKOL: User, Role, Permission, CashDrawer

---

## 3. Kodolasi szabalyok

### 3.1 API tervezes
- RESTful konvenciok
- Kebab-case endpoint-ok
- Trailing slash konzisztencia (hasznald vagy ne)
- OpenAPI/Swagger dokumentacio

### 3.2 SQLAlchemy
- Egyetlen `Base` az osszes modellhez
- `CompatibleJSON` hasznalata JSONB helyett (cross-DB kompat)
- Proper relationship definiciok

### 3.3 Error handling
- Sose hasznalj bare `except:`
- HTTPException megfelelő status kodokkal
- Logging minden hibához

---

## 4. Fontos domain logikak

### 4.1 Hullam rendszer (vendegter)
```python
class OrderWave(str, Enum):
    FIRST = "FIRST"      # PIROS - elso kor
    SECOND = "SECOND"    # SARGA - masodik kor
    DEFAULT = "DEFAULT"  # JELOLETLEN - maradek
```

**FONTOS:** NEM kategoria alapu (eloétel/foétel), hanem felszolgalo altal beallitott prioritas!

### 4.2 KDS allapotok
```python
class KdsStatus(str, Enum):
    QUEUED = "QUEUED"
    IN_PROGRESS = "IN_PROGRESS"
    READY = "READY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
```

### 4.3 Palya hozzarendeles
A palya-hozzarendeles a termek beallitasoknal tortenik (Product → station mapping).
A felszolgalo NEM valaszt palyat rendeles kozben.

---

## 5. Tiltott muveletek

- **NE** hozz letre uj `Base` osztalyt (hasznald a meglevo-t)
- **NE** importalj masik service kodjabol kozvetlenul (HTTP hivas helyette)
- **NE** tamaszkodj ARCHIVED doksikra
- **NE** modosits frontend kodot

---

## 6. Build es teszt

```bash
# Docker inditas
docker-compose up --build -d

# Migracio alkalmazas
docker-compose exec service_orders alembic upgrade head

# Logok ellenorzese
docker-compose logs service_orders --tail=50
```

---

## 7. Kapcsolodo Skill fajlok

- `docs/skills/WEB_CLAUDE_SKILLS.md` - Frontend ugynok
- `docs/skills/VS_CLAUDE_SKILLS.md` - Integracios ugynok

---

_END OF JULES_SKILLS.md_
