# WEB CLAUDE SKILLS & GUIDELINES

**Version:** 1.0
**Last Updated:** 2025-11-30
**Agent Type:** Frontend Developer (React, TypeScript, Mantine)

---

## 1. Fo specifikaciok - MINDIG EZEKET OLVASD EL ELOSZOR

| Dokumentum | Cel |
|------------|-----|
| `docs/spec/SYSTEM_MASTER_SPEC_V1.md` | Rendszer fo logika |
| `docs/ui-ux/UI_UX_FOUNDATION.md` | Design & UI elvek |
| `docs/spec/ARCHITECTURE_TARGET_V1.md` | Backend architektura |

### Modul-specifikus doksik:
- **Floorplan**: `docs/spec/FLOORPLAN_DOMAIN_V1.md`
- **Vendegter / felszolgalo**: `docs/spec/GUEST_FLOOR_ORDERS_SPEC_V1.md`
- **Fizetes / ÁFA**: `docs/spec/PAYMENT_FLOW_V1.md`

---

## 2. Frontend fokusz

### 2.1 Technologia stack
- **React 18+** - Funkcionalis komponensek, hooks
- **TypeScript** - Strict mode, tipus biztonsag
- **Mantine UI** - Komponens library (Button, Modal, Toast stb.)
- **Vite** - Build tool
- **Zustand** - State management (ahol szukseges)

### 2.2 UI/UX iranyelvek

**KOTELEZO:** Mindig tartsd be a `docs/ui-ux/UI_UX_FOUNDATION.md` iranyelveit!

- **Dark POS theme**: sotet hatter (`#050B10`)
- **Resti-zold primary**: `#16A085`
- **Min 44x44 px** touch target
- **Toast notification** hibakhoz (NEM alert())
- **ConfirmDialog** fontos muveletekheg (NEM confirm())

### 2.3 Komponens struktura

```
frontend/src/
  components/
    ui/           # Kozos UI komponensek (Button, Input, Modal stb.)
    layout/       # AppShell, Sidebar, TopBar
    kds/          # KDS-specifikus komponensek
    tables/       # Asztal komponensek
    bar/          # Barpult komponensek
  pages/          # Oldalak (BarPage, OperatorPage stb.)
  features/       # Feature-specifikus komponensek
  hooks/          # Custom React hooks
  stores/         # Zustand store-ok
  services/       # API hivo service-ek
```

---

## 3. Kodolasi szabalyok

### 3.1 TypeScript
- **Strict mode** kotelező
- Minden prop-nak legyen **interface/type**
- `import type` hasznalata tipus importokhoz (verbatimModuleSyntax)

### 3.2 React
- Funkcionalis komponensek
- `useMemo`, `useCallback` optimalizaciokhoz
- Custom hook-ok uzleti logikahoz

### 3.3 Stilusok
- Mantine UI komponensek preferalva
- CSS Modules vagy Mantine styles
- Responsiv: tablet/desktop layout

---

## 4. Tiltott muveletek

- **NE** hasznalj `alert()` vagy `confirm()` - Toast/Modal helyette
- **NE** tamaszkodj ARCHIVED doksikra
- **NE** modosits backend kodot
- **NE** hozz letre uj szolgaltatasokat backend reszen

---

## 5. Build ellenorzes

Minden valtoztatas utan:
```bash
cd frontend
npm run build
```

Ha TypeScript hiba van, javitsd meg mielott commitolsz.

---

## 6. Kapcsolodo Skill fajlok

- `docs/skills/JULES_SKILLS.md` - Backend ugynok
- `docs/skills/VS_CLAUDE_SKILLS.md` - Integracios ugynok

---

_END OF WEB_CLAUDE_SKILLS.md_
