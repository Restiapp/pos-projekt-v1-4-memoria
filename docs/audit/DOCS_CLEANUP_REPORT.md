# Docs & Skill Cleanup Report - V1

**Datum:** 2025-11-30
**Branch:** `docs/spec-refresh-v1`
**Keszitette:** VS Claude Code

---

## 1. Uj / frissitett master doksik

### Uj canonical specifikaciok

| Fajl | Leiras |
|------|--------|
| `docs/spec/SYSTEM_MASTER_SPEC_V1.md` | **FO SPECIFIKACIO** - Teljes rendszer attekintes, modulok, architektura, UI/UX, domain logika osszefoglalo |
| `docs/spec/GUEST_FLOOR_ORDERS_SPEC_V1.md` | Vendegter / Felszolgalo modul specifikacioja az uj **PIROS/SARGA/JELOLETLEN** hullam logikával |

### Meglevo canonical doksik (nem modositva)

| Fajl | Leiras |
|------|--------|
| `docs/spec/ARCHITECTURE_TARGET_V1.md` | Backend architektura |
| `docs/spec/FLOORPLAN_DOMAIN_V1.md` | Floorplan domain es API |
| `docs/spec/PAYMENT_FLOW_V1.md` | Fizetes es zaras flow |
| `docs/ui-ux/UI_UX_FOUNDATION.md` | UI/UX alapelvek |
| `docs/audit/MASTER_AUDIT_REPORT.md` | Audit osszefoglalo |
| `docs/roadmap/MASTER_ROADMAP.md` | Sprint roadmap |

---

## 2. Archivalt doksik

A kovetkezo dokumentumok tetejen ARCHIVED banner lett elhelyezve:

### Gyokerben levo dokumentumok

| Fajl | Ok |
|------|-----|
| `ROADMAP_V1.md` | Regi roadmap, a `docs/roadmap/MASTER_ROADMAP.md` a canonical |
| `SPRINT_PLAN.md` | Regi V3.0 terv, mar nem aktualis |
| `TODO_V3.md` | Regi TODO lista, mar nem aktualis |
| `SPRINT0_CONFLICT_CLEANUP_STATUS.md` | Torteneti log fajl (Sprint 0 cleanup) |
| `PR_SPRINT1_BAR_INTEGRATION.md` | Torteneti log fajl (Sprint 1 PR) |

### .claude/skills/ mappaban levo regi skill fajlok

| Fajl | Ok |
|------|-----|
| `skill-module-0-menu.md` | Regi skill format, uj: `docs/skills/` |
| `skill-module-1-orders.md` | Regi skill format |
| `skill-module-2-tables.md` | Regi skill format |
| `skill-module-3-kds.md` | Regi skill format |
| `skill-module-4-billing.md` | Regi skill format |
| `skill-module-5-inventory.md` | Regi skill format |
| `skill-module-6-employees.md` | Regi skill format |
| `skill-module-7-crm.md` | Regi skill format |
| `skill-module-8-ntak.md` | Regi skill format |

---

## 3. Uj / frissitett Skill fajlok

### Uj skill fajlok a `docs/skills/` mappaban

| Fajl | Leiras |
|------|--------|
| `WEB_CLAUDE_SKILLS.md` | **Frontend ugynok** - React, TypeScript, Mantine fokusz, UI/UX iranyelvek |
| `JULES_SKILLS.md` | **Backend ugynok** - Python, FastAPI, PostgreSQL, domain logika |
| `VS_CLAUDE_SKILLS.md` | **Integracios ugynok** - Git, Docker, build, teszt, merge |

### Kozos blokk minden skill fajlban

Minden ugynok skill fajl tartalmazza a kovetkezo referenciat:
```markdown
## 1. Fo specifikaciok - MINDIG EZEKET OLVASD EL ELOSZOR

| Dokumentum | Cel |
|------------|-----|
| `docs/spec/SYSTEM_MASTER_SPEC_V1.md` | Rendszer fo logika |
| `docs/ui-ux/UI_UX_FOUNDATION.md` | Design & UI elvek |
| `docs/spec/ARCHITECTURE_TARGET_V1.md` | Backend architektura |
```

---

## 4. Fontos valtozasok

### 4.1 PIROS/SARGA/JELOLETLEN hullam logika

A `docs/spec/GUEST_FLOOR_ORDERS_SPEC_V1.md` specifikacio bevezeti az uj hullam rendszert:

- **PIROS (FIRST)**: Elso kor - amit azonnal ker a vendeg
- **SARGA (SECOND)**: Masodik kor - kesobbi hullam
- **JELOLETLEN (DEFAULT)**: Maradek - egyben

**FONTOS:** Tobbe NEM hasznalunk fix "eloétel / foétel / desszert" kategoria alapu koroket!
A felszolgalo donti el, melyik tetel melyik hullamban menjen.

### 4.2 Palya hozzarendeles egyszerusites

A specifikacio szerint:
> "A palya-hozzarendeles a termekbeallitasoknal tortenik (Admin → Menu/Product).
> A felszolgalo NEM dont palyarol rendeles kozben."

---

## 5. Megjegyzesek

- **Nincs kodvaltoztatas** - csak .md dokumentumok modosultak
- **npm run build** nem szukseges - nincs TypeScript/JavaScript valtozas
- A regi `.claude/skills/` skill fajlok megmaradtak, de ARCHIVED bannerrel jelolve

---

## 6. Javasolt tovabbi finomitasok

1. A gyokerben levo tovabbi INTEGRATION_REPORT, PHASE_X_REPORT fajlokat is erdemes archivalasra jelolni
2. A `docs/DOCS_*.md` fajlok attekintese es szinkronizalasa a SYSTEM_MASTER_SPEC_V1.md-vel
3. A CLAUDE.md fajl frissitese, hogy a `docs/skills/` mappara hivatkozzon

---

## 7. Fajl statisztikak

| Tipus | Darab |
|-------|-------|
| Uj fajlok | 5 |
| Archivalt doksik | 14 |
| Modositott fajlok | 14 |

---

_END OF DOCS_CLEANUP_REPORT.md_
