# POS Projekt - Külső Memória v1.4

Ez a repository tartalmazza az Éttermi POS rendszer teljes tervezési dokumentációját, amelyet a 0. Fázis ("Az Építész") során generáltunk. Ez a "Külső Memória" szolgál alapul a későbbi fejlesztési fázisok számára.

## 📋 Tartalom

### Főbb Dokumentumok

- **[TECH_STACK.md](TECH_STACK.md)** - Technológiai választások és indoklásuk (2025 Q4)
- **[DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)** - Teljes PostgreSQL adatbázis séma
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Mikroszolgáltatás architektúra és AI integráció
- **[API_SPECS.md](API_SPECS.md)** - Magas szintű API specifikáció (OpenAPI kivonat)
- **[SPRINT_PLAN.md](SPRINT_PLAN.md)** - 48 órás hiperagresszív sprint terv

### Claude Skills

A `.claude/skills/` mappában találhatók a modulonkénti skill definíciók:

- `skill-module-0-menu.md` - Terméktörzs és Menü
- `skill-module-1-orders.md` - Rendeléskezelés
- `skill-module-5-inventory.md` - Készletkezelés
- `skill-module-8-ntak.md` - NTAK és Adminisztráció

### RAG Dokumentumok

A `docs/` mappában ChatGPT RAG-hez optimalizált dokumentumok:

- `DOCS_ARCHITECTURE.md` - Architektúra összefoglaló
- `DOCS_DATABASE.md` - Adatbázis összefoglaló
- `DOCS_MODULES.md` - Modulok és üzleti logika
- `DOCS_LIBRARIES.md` - Könyvtárak és verziók

## 🏗️ Projekt Architektúra

A rendszer 9 modulra van bontva:

0. **Terméktörzs és Menü** - AI fordítás (Vertex AI), képkezelés (GCS + Cloud Functions)
1. **Rendeléskezelés** - Többcsatornás rendelések, NTAK ÁFA váltás
2. **Asztalkezelés** - Vizuális térkép, személyenkénti tételek
3. **Konyhai Kijelző (KDS)** - Valós idejű rendelés-feldolgozás
4. **Számlázás és Fizetés** - SZÉP kártya integráció
5. **Készletkezelés** - Kettős rendszer: automatikus + manuális, AI számlaolvasás
6. **Munkatárs** - Jogosultságkezelés
7. **CRM és Integrációk** - Törzsvevő, hitelkeret
8. **Adminisztráció** - NTAK adatszolgáltatás, HACCP, offline sync

## 🚀 Tech Stack

| Komponens | Technológia | Verzió |
|-----------|-------------|---------|
| Backend | Python (FastAPI) | 0.115.x |
| Adatbázis | PostgreSQL | 17.x |
| Frontend | React (Vite) | 19.x / 6.x |
| AI Fordítás | Vertex AI Translation LLM | v2 |
| AI OCR | Google Document AI | v2 |
| Képkezelés | GCS + Cloud Functions + Pillow | N/A |

## 📁 Mappaszerkezet

```
/
├── .claude/skills/        # Claude Code skill definíciók
├── docs/                  # RAG dokumentumok
├── backend/               # Mikroszolgáltatások
│   ├── service_menu/
│   ├── service_orders/
│   ├── service_kds/
│   ├── service_billing/
│   ├── service_inventory/
│   ├── service_employees/
│   ├── service_crm/
│   ├── service_admin/
│   └── api_gateway/
├── frontend/              # React (Vite) frontend
├── scripts/               # Segédscriptek
└── [dokumentáció]         # Root szintű MD fájlok
```

## 🎯 Következő Lépések (1. Fázis - "A Raj")

1. Repository megosztása a fejlesztő ágensekkel
2. Claude Web Code ágensek inicializálása
3. Vertex AI Studio agent beállítása
4. Sprint indítása a SPRINT_PLAN.md alapján

## 📝 Verzióinformáció

- **Verzió**: 1.4
- **Létrehozva**: 2025-11-16
- **0. Fázis**: Az Építész (Vertex AI Gemini 2.5 Pro)
- **Koordinátor**: Gemini 2.5 Pro (1M token context)
- **Kivitelezők**: VS Code Claude Code, Claude Web Code, Vertex AI Studio

---

**Fontos**: Ez a repository a projekt "memóriája" - a tényleges kód a későbbi fázisokban egy másik repository-ban kerül kifejlesztésre.

## 📄 Licenc

Copyright © 2025 Resti Étterem. Minden jog fenntartva.
