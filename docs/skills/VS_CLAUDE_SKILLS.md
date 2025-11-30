# VS CLAUDE SKILLS & GUIDELINES

**Version:** 1.0
**Last Updated:** 2025-11-30
**Agent Type:** Integration Engineer / DevOps (Git, Docker, Build, Test)

---

## 1. Fo specifikaciok - MINDIG EZEKET OLVASD EL ELOSZOR

| Dokumentum | Cel |
|------------|-----|
| `docs/spec/SYSTEM_MASTER_SPEC_V1.md` | Rendszer fo logika |
| `docs/spec/ARCHITECTURE_TARGET_V1.md` | Backend architektura |
| `docs/ui-ux/UI_UX_FOUNDATION.md` | Design & UI elvek |

### Modul-specifikus doksik:
- **Floorplan**: `docs/spec/FLOORPLAN_DOMAIN_V1.md`
- **Vendegter / felszolgalo**: `docs/spec/GUEST_FLOOR_ORDERS_SPEC_V1.md`
- **Fizetes / ÁFA**: `docs/spec/PAYMENT_FLOW_V1.md`

---

## 2. Integracios fokusz

### 2.1 Fo feladatok
- Branch merge es conflict resolution
- Build ellenorzes (frontend + backend)
- Docker container management
- Teszt futtatás
- Dokumentacio karbantartas

### 2.2 Git workflow
```bash
# Uj feature branch
git checkout main
git pull
git checkout -b feature/xyz

# Merge conflict resolution
git merge origin/other-branch
# ... fix conflicts ...
git add .
git commit -m "resolve merge conflicts"

# Push
git push -u origin feature/xyz
```

---

## 3. Build ellenorzes

### 3.1 Frontend build
```bash
cd frontend
npm install
npm run build
```

**Ellenorizni:**
- 0 TypeScript hiba
- Sikeres Vite build
- Nincs warning ami hibat jelez

### 3.2 Backend build (Docker)
```bash
docker-compose up --build -d
docker-compose ps  # minden "healthy"
docker-compose logs --tail=50  # nincs hiba
```

**Ellenorizni:**
- Minden container "healthy" statuszban
- Nincs Python exception a logokban
- API endpoint-ok elerheto-ek

---

## 4. Konfliktus feloldas strategia

### 4.1 Altalanos szabalyok
1. Olvasd el **mindket** branch valtozasait
2. Ha nem vilagos melyik a "helyes", kerdezd meg a felhasznalot
3. Ne veszits el funkcionalitast egyik branch-bol sem

### 4.2 Tipikus konfliktus tipusok

**Import konfliktusok:**
```python
# Kombinalj, ha mindketto kell
from module import A, B  # HEAD
from module import C, D  # incoming
# Eredmeny:
from module import A, B, C, D
```

**Package.json verzio konfliktusok:**
- Altalaban a nagyobb/ujabb verzio nyer
- De ellenorizd a kompatibilitast

---

## 5. Dokumentacio karbantartas

### 5.1 NE modosits ezeket onhatalmulag:
- `docs/spec/SYSTEM_MASTER_SPEC_V1.md`
- `docs/spec/ARCHITECTURE_TARGET_V1.md`
- `docs/ui-ux/UI_UX_FOUNDATION.md`

### 5.2 Szabadon modosithato:
- FIXLOG fajlok (pl. `D3D4_FIXLOG.md`)
- Sprint riportok
- Build status dokumentumok

### 5.3 Archivalas
Ha regi dokumentumot talalsz ami ellenmond az aktualis specnek:
```markdown
> **ARCHIVED / ELAVULT DOKUMENTUM**
> Ez a dokumentum torteneti celokat szolgal.
> A fejleszteshez **NE** ezt hasznald specifikaciokent.
> Aktualis fo specifikacio: `docs/spec/SYSTEM_MASTER_SPEC_V1.md`
```

---

## 6. Tiltott muveletek

- **NE** modosits architekturalis doksikat kulon keres nelkul
- **NE** tamaszkodj ARCHIVED doksikra
- **NE** hagyj ki build ellenorzest merge utan
- **NE** pusholj force-csal production branch-re

---

## 7. Docker parancsok referencia

```bash
# Osszes service inditas
docker-compose up --build -d

# Egy service ujrainditas
docker-compose restart service_orders

# Logok nezese
docker-compose logs service_orders --tail=100 -f

# Shell belepes
docker-compose exec service_orders bash

# Minden leallitas
docker-compose down

# Minden leallitas + volume torles (FIGYELJ!)
docker-compose down -v

# Container statusz
docker-compose ps
```

---

## 8. Kapcsolodo Skill fajlok

- `docs/skills/WEB_CLAUDE_SKILLS.md` - Frontend ugynok
- `docs/skills/JULES_SKILLS.md` - Backend ugynok

---

_END OF VS_CLAUDE_SKILLS.md_
