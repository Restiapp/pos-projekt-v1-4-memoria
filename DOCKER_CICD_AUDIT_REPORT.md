# 🔍 Docker, DevOps & CI/CD Audit Jelentés
## POS Projekt v1.4 - Memoria

**Audit Dátum:** 2025-11-22
**Auditor:** Agent #4 - Docker & DevOps Specialist
**Projekt:** Restiapp POS Mikroszolgáltatás Architektúra

---

## 📋 Executive Summary

A projekt Docker-konfigurációja **alapvetően működőképes**, de **jelentős biztonsági, optimalizálási és production-ready hiányosságok** találhatók. **CI/CD pipeline egyáltalán nem létezik**, ami kritikus a modern fejlesztési workflow szempontjából.

### Összesített Értékelés

| Kategória | Értékelés | Súlyosság |
|-----------|-----------|-----------|
| **Docker Alapok** | ⚠️ Megfelelő | Közepes |
| **Biztonság** | 🔴 Kritikus Hiányosságok | KRITIKUS |
| **Optimalizálás** | ⚠️ Javítandó | Közepes |
| **CI/CD** | 🔴 Nem létezik | KRITIKUS |
| **Kubernetes Kompatibilitás** | 🔴 Nincs felkészítve | Magas |
| **Dokumentáció** | ✅ Megfelelő | Alacsony |

---

## 🚨 KRITIKUS PROBLÉMÁK (Azonnal javítandó)

### K1. Hiányzó Szolgáltatások a Docker Compose-ban

**Probléma:**
A következő szolgáltatások rendelkeznek Dockerfile-lal, de **NEM szerepelnek** a `docker-compose.yml`-ben:
- `service_crm` (Port: 8004)
- `service_logistics` (Port: 8005)

**Hatás:**
- Ezek a szolgáltatások nem indulnak el a `docker-compose up` paranccsal
- A teljes mikroszolgáltatás architektúra nem működőképes
- Függőségi kapcsolatok hiányoznak

**Megoldás:**
```yaml
# Hozzáadandó a docker-compose.yml-hez:
  service_crm:
    build:
      context: .
      dockerfile: backend/service_crm/Dockerfile
    container_name: pos-service-crm
    restart: unless-stopped
    ports:
      - "8004:8004"
    environment:
      DATABASE_URL: postgresql://pos_user:${POSTGRES_PASSWORD:-pos_password_dev}@postgres:5432/pos_db
      PORT: 8004
      JWT_SECRET_KEY: ${JWT_SECRET_KEY:-your-secret-key-change-in-production}
      NTAK_API_KEY: ${NTAK_API_KEY:-dummy-key}
      NTAK_TAX_NUMBER: ${NTAK_TAX_NUMBER:-00000000-0-00}
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8004/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - pos-network

  service_logistics:
    build:
      context: .
      dockerfile: backend/service_logistics/Dockerfile
    container_name: pos-service-logistics
    restart: unless-stopped
    ports:
      - "8005:8005"
    environment:
      DATABASE_URL: postgresql://pos_user:${POSTGRES_PASSWORD:-pos_password_dev}@postgres:5432/pos_db
      PORT: 8005
      JWT_SECRET_KEY: ${JWT_SECRET_KEY:-your-secret-key-change-in-production}
      NTAK_API_KEY: ${NTAK_API_KEY:-dummy-key}
      NTAK_TAX_NUMBER: ${NTAK_TAX_NUMBER:-00000000-0-00}
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8005/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - pos-network
```

---

### K2. Hiányzó .dockerignore Fájlok

**Probléma:**
Egyetlen `.dockerignore` fájl sem létezik a projektben.

**Hatás:**
- **Biztonsági kockázat:** Érzékeny fájlok (`.env`, `credentials/`, `.git/`) bekerülhetnek az image-ekbe
- **Megnövekedett image méret:** Felesleges fájlok (node_modules, __pycache__, .git stb.) az image-ben
- **Lassabb build:** Minden fájl átmásolásra kerül a build context-be
- **Adatszivárgás:** Helyi konfigurációk, credentials bekerülhetnek production image-ekbe

**Megoldás:**
Létrehozandó `.dockerignore` a projekt gyökérkönyvtárában:

```dockerignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/
*.egg
.pytest_cache/
.mypy_cache/
.coverage
htmlcov/

# Virtual environments
venv/
env/
ENV/
.venv

# Environment files (KRITIKUS!)
.env
.env.*
!.env.example

# Credentials (KRITIKUS!)
credentials/
*.json
service-account-key.json
gcp-key.json

# Git
.git/
.gitignore
.gitattributes

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite
*.sqlite3

# Node (frontend)
node_modules/
npm-debug.log
yarn-error.log

# Documentation (nem kell az image-ben)
*.md
docs/

# Docker
docker-compose*.yml
Dockerfile*
.dockerignore

# Tests (opcionális, production image-ben nem kell)
tests/
test_*.py
*_test.py
pytest.ini
.pytest_cache/

# Temporary files
tmp/
temp/
*.tmp
*.bak
```

---

### K3. Root User Használata a Konténerekben

**Probléma:**
Az összes Dockerfile **root user-ként** futtatja az alkalmazásokat.

**Hatás:**
- **KRITIKUS BIZTONSÁGI KOCKÁZAT:** Ha egy támadó kihasznál egy sérülékenységet az alkalmazásban, root jogosultságokat szerez a konténerben
- **Privilege Escalation:** Könnyebb kilépni a konténerből és hozzáférni a host rendszerhez
- **Nem felel meg az ipari szabványoknak:** CIS Docker Benchmarks, Kubernetes Security Best Practices
- **Production környezetben elfogadhatatlan**

**Megoldás:**
Minden Dockerfile-ban hozzáadandó non-root user:

```dockerfile
# Példa: backend/service_menu/Dockerfile módosítva
# Stage 3: Application
FROM dependencies as application

# SECURITY FIX: Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -u 1000 appuser

# Copy the entire backend directory (shared models/schemas)
COPY --chown=appuser:appuser backend/ /app/backend/

# Create directory for Google Cloud credentials with proper ownership
RUN mkdir -p /app/credentials && chown -R appuser:appuser /app/credentials

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER appuser

# Expose port 8001 (Menu Service)
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run the application as non-root
CMD ["uvicorn", "backend.service_menu.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

**Alkalmazandó minden szolgáltatásra:**
- service_menu
- service_orders
- service_inventory
- service_admin
- service_crm
- service_logistics

---

### K4. Titkos Kulcsok Környezeti Változókban

**Probléma:**
Érzékeny adatok (jelszavak, API kulcsok, JWT secret) **környezeti változókként** kerülnek átadásra a docker-compose.yml-ben.

**Hatás:**
- **Biztonsági kockázat:** `docker inspect` paranccsal bárki láthatja a titkos kulcsokat
- **Logokban megjelenhetnek** a környezeti változók
- **Process listing** révén láthatók (`ps aux | grep POSTGRES_PASSWORD`)
- **Nem felel meg a compliance követelményeknek** (SOC2, ISO27001)

**Jelenleg Veszélyeztetett Adatok:**
```yaml
POSTGRES_PASSWORD=pos_password_dev
JWT_SECRET_KEY=your-secret-key-change-in-production
NTAK_API_KEY=dummy-key
NTAK_TAX_NUMBER=00000000-0-00
```

**Megoldás (Docker Secrets - Docker Swarm):**

```yaml
version: '3.8'

services:
  service_admin:
    # ...
    secrets:
      - postgres_password
      - jwt_secret_key
      - ntak_api_key
    environment:
      # Secrets fájl útvonalak
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password
      JWT_SECRET_KEY_FILE: /run/secrets/jwt_secret_key
      NTAK_API_KEY_FILE: /run/secrets/ntak_api_key

secrets:
  postgres_password:
    file: ./secrets/postgres_password.txt
  jwt_secret_key:
    file: ./secrets/jwt_secret_key.txt
  ntak_api_key:
    file: ./secrets/ntak_api_key.txt
```

**Kód módosítás szükséges** az alkalmazásokban:
```python
# backend/service_admin/config/settings.py
import os

def read_secret(env_var: str, file_suffix: str = "_FILE") -> str:
    """Read secret from file if _FILE env var exists, otherwise from env var directly."""
    file_path_var = env_var + file_suffix
    if file_path := os.getenv(file_path_var):
        with open(file_path, 'r') as f:
            return f.read().strip()
    return os.getenv(env_var, "")

class Settings(BaseSettings):
    jwt_secret_key: str = read_secret("JWT_SECRET_KEY", "_FILE") or "default-dev-key"
    postgres_password: str = read_secret("POSTGRES_PASSWORD", "_FILE") or "pos_password_dev"
    ntak_api_key: str = read_secret("NTAK_API_KEY", "_FILE") or "dummy-key"
```

---

### K5. CI/CD Pipeline Teljes Hiánya

**Probléma:**
**Nincs egyetlen CI/CD pipeline sem** implementálva (GitHub Actions, GitLab CI, Jenkins stb.).

**Hatás:**
- Manuális tesztelés és deployment
- Nincs automatizált kód minőségellenőrzés
- Nincs automatizált build és image publikálás
- Nagyobb esély hibákra production környezetben
- Lassú fejlesztési ciklus
- Nincs verziókezelés az image-ekre

**Megoldás: GitHub Actions Workflow Implementálása**

Létrehozandó: `.github/workflows/ci-cd.yml`

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop, 'feature/**' ]
  pull_request:
    branches: [ main, develop ]

env:
  REGISTRY: ghcr.io
  IMAGE_PREFIX: restiapp/pos

jobs:
  # ============================================================================
  # JOB 1: Code Quality & Tests
  # ============================================================================
  code-quality:
    name: Code Quality & Unit Tests
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install flake8 black mypy pytest pytest-asyncio pytest-cov

      - name: Run Black (code formatting check)
        run: black --check backend/

      - name: Run Flake8 (linting)
        run: flake8 backend/ --count --select=E9,F63,F7,F82 --show-source --statistics

      - name: Run MyPy (type checking)
        run: mypy backend/ --ignore-missing-imports
        continue-on-error: true

      - name: Run Unit Tests
        run: |
          pytest backend/ -v --cov=backend --cov-report=xml --cov-report=term

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-umbrella
          fail_ci_if_error: false

  # ============================================================================
  # JOB 2: Build & Push Docker Images
  # ============================================================================
  build-images:
    name: Build Docker Images
    runs-on: ubuntu-latest
    needs: code-quality
    if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop')

    strategy:
      matrix:
        service:
          - service_menu
          - service_orders
          - service_inventory
          - service_admin
          - service_crm
          - service_logistics

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata (tags, labels)
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}-${{ matrix.service }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha,prefix={{branch}}-
            type=semver,pattern={{version}}
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: backend/${{ matrix.service }}/Dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}-${{ matrix.service }}:buildcache
          cache-to: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}-${{ matrix.service }}:buildcache,mode=max

  # ============================================================================
  # JOB 3: Security Scanning
  # ============================================================================
  security-scan:
    name: Security Vulnerability Scan
    runs-on: ubuntu-latest
    needs: build-images
    if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop')

    strategy:
      matrix:
        service:
          - service_menu
          - service_orders
          - service_inventory
          - service_admin
          - service_crm
          - service_logistics

    steps:
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}-${{ matrix.service }}:${{ github.ref_name }}
          format: 'sarif'
          output: 'trivy-results-${{ matrix.service }}.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload Trivy results to GitHub Security tab
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results-${{ matrix.service }}.sarif'

  # ============================================================================
  # JOB 4: Integration Tests (with docker-compose)
  # ============================================================================
  integration-tests:
    name: Integration Tests
    runs-on: ubuntu-latest
    needs: build-images

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Create .env file
        run: |
          cat > .env << EOF
          POSTGRES_PASSWORD=test_password
          JWT_SECRET_KEY=test-secret-key-for-ci-cd-only
          NTAK_API_KEY=dummy-key
          NTAK_TAX_NUMBER=00000000-0-00
          GCS_BUCKET_NAME=test-bucket
          GCP_PROJECT_ID=test-project
          VERTEX_AI_LOCATION=us-central1
          DOCUMENTAI_PROJECT_ID=test-project
          DOCUMENTAI_LOCATION=us
          DOCUMENTAI_PROCESSOR_ID=test-processor
          EOF

      - name: Start services with docker-compose
        run: |
          docker-compose up -d
          sleep 30  # Wait for services to be healthy

      - name: Check service health
        run: |
          curl -f http://localhost:8001/health || exit 1
          curl -f http://localhost:8002/health || exit 1
          curl -f http://localhost:8003/health || exit 1
          curl -f http://localhost:8008/health || exit 1

      - name: Run integration tests
        run: |
          # TODO: Implement integration tests
          echo "Integration tests would run here"

      - name: Collect logs on failure
        if: failure()
        run: |
          docker-compose logs > docker-compose-logs.txt
          cat docker-compose-logs.txt

      - name: Cleanup
        if: always()
        run: docker-compose down -v

  # ============================================================================
  # JOB 5: Deploy to Staging (optional)
  # ============================================================================
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: [build-images, integration-tests]
    if: github.ref == 'refs/heads/develop'
    environment:
      name: staging
      url: https://staging.restiapp.com

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy to staging
        run: |
          echo "Deployment to staging would happen here"
          # SSH to staging server and pull latest images
          # Or use cloud provider CLI (GCP, AWS, Azure)
          # Or use Kubernetes kubectl/helm

  # ============================================================================
  # JOB 6: Deploy to Production
  # ============================================================================
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: [build-images, integration-tests, security-scan]
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://restiapp.com

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy to production
        run: |
          echo "Production deployment would happen here"
          # This should require manual approval in GitHub
```

**GitHub Repository Beállítások:**
1. Settings → Secrets and Variables → Actions
2. Hozzáadandó secrets:
   - `GCP_SERVICE_ACCOUNT_KEY` (ha GCP-t használunk)
   - `PRODUCTION_SSH_KEY` (ha SSH deployment)
   - `KUBECONFIG` (ha Kubernetes)

---

## ⚠️ MAGAS PRIORITÁSÚ PROBLÉMÁK

### M1. Port Ütközések és Inconsistency

**Probléma:**
Port konfiguráció hibák a service_menu-nél:

```yaml
# docker-compose.yml
service_menu:
  ports:
    - "8001:8000"  # Host:Container - Menu runs on 8000 internally
  environment:
    PORT: 8000
  healthcheck:
    # CRITICAL FIX (C1.1 continued): service_menu runs on port 8001, not 8000
    test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
```

**Probléma:**
- A komment szerint a konténeren **belül** a 8000-es porton fut
- De a healthcheck a **8001**-es portot ellenőrzi
- Ez ellentmondás, és valószínűleg a healthcheck **hibás**

**Dockerfile szerint:**
```dockerfile
# backend/service_menu/Dockerfile
EXPOSE 8001
CMD ["uvicorn", "backend.service_menu.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

**Megoldás:**
```yaml
service_menu:
  ports:
    - "8001:8001"  # JAVÍTVA: Konzisztens port mapping
  environment:
    PORT: 8001      # JAVÍTVA: Egyező az uvicorn --port értékével
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
```

**Ugyanez a probléma az ÖSSZES szolgáltatásnál:**
- service_orders: 8002:8001 → kellene: 8002:8002
- service_inventory: 8003:8003 ✅ (ez jó)
- service_admin: 8008:8008 ✅ (ez jó)

---

### M2. Nincs Resource Limit (CPU, Memory)

**Probléma:**
Egyetlen szolgáltatás sem rendelkezik CPU és memória korlátokkal.

**Hatás:**
- Egy szolgáltatás monopolizálhatja a teljes host erőforrásokat
- Memory leak esetén a teljes rendszer összeomlhat
- Kubernetes-ben nem fog működni megfelelően (HPA, scheduling)

**Megoldás:**

```yaml
services:
  service_menu:
    # ... (többi konfiguráció)
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
```

**Ajánlott Resource Limits:**

| Service | CPU Limit | Memory Limit | CPU Reservation | Memory Reservation |
|---------|-----------|--------------|-----------------|-------------------|
| postgres | 2.0 | 2G | 1.0 | 1G |
| service_menu | 1.0 | 512M | 0.5 | 256M |
| service_orders | 1.0 | 512M | 0.5 | 256M |
| service_inventory | 1.5 | 1G | 0.75 | 512M |
| service_admin | 1.0 | 512M | 0.5 | 256M |
| service_crm | 1.0 | 512M | 0.5 | 256M |
| service_logistics | 1.0 | 512M | 0.5 | 256M |

---

### M3. PostgreSQL Port Nyilvánosan Elérhető

**Probléma:**
A PostgreSQL adatbázis **5432-es portja exposed** a host gépen:

```yaml
postgres:
  ports:
    - "5432:5432"  # ⚠️ VESZÉLYES production környezetben
```

**Hatás:**
- **Biztonsági kockázat:** Bárki a hálózaton elérheti az adatbázist
- **Brute-force támadások** a jelszó ellen
- **Port scanning** könnyen azonosítja
- **Nem szükséges:** A mikroszolgáltatások a Docker network-ön keresztül érhetik el

**Megoldás:**

```yaml
# FEJLESZTÉSI környezethez (docker-compose.dev.yml):
postgres:
  ports:
    - "5432:5432"  # OK fejlesztéshez (helyi hozzáférés pgAdmin-ból stb.)

# PRODUCTION környezethez (docker-compose.prod.yml):
postgres:
  # ports:
  #   - "5432:5432"  # NEM EXPOSED - csak internal network
  expose:
    - "5432"  # Csak Docker network-ön belül elérhető
```

**Különböző környezetekhez külön compose fájlok:**

```bash
# docker-compose.yml - base config
# docker-compose.dev.yml - development overrides
# docker-compose.prod.yml - production overrides

# Használat:
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d   # DEV
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d  # PROD
```

---

### M4. Nincs Logging Konfiguráció

**Probléma:**
Nincs explicit logging driver és konfiguráció a szolgáltatásokhoz.

**Hatás:**
- Alapértelmezett json-file driver **korlátlan méretű** logokat generál
- Disk space kifogyhat
- Nincs centralizált log aggregáció
- Nehéz debuggolni production környezetben

**Megoldás:**

```yaml
# docker-compose.yml - global logging config
x-logging: &default-logging
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
    labels: "service,environment"

services:
  service_menu:
    # ...
    logging: *default-logging
    labels:
      - "service=menu"
      - "environment=production"
```

**Production környezethez (opcionális - ha van centralizált logging):**

```yaml
# Fluentd, Loki, CloudWatch, Stackdriver stb.
logging:
  driver: "fluentd"
  options:
    fluentd-address: "localhost:24224"
    tag: "pos.{{.Name}}"
```

---

### M5. Version '3.8' Deprecated

**Probléma:**
A `docker-compose.yml` használja a `version: '3.8'` kulcsot, ami **deprecated** a Compose v2-től.

**Hatás:**
- Warning üzenetek
- Új funkciók nem elérhetők
- Jövőbeli kompatibilitási problémák

**Megoldás:**

```yaml
# ELTÁVOLÍTANDÓ a version kulcs
# version: '3.8'  # ❌ TÖRLENDŐ

# Modern Compose fájl formátum (nincs version kulcs)
services:
  postgres:
    # ...
```

---

## 🔧 KÖZEPES PRIORITÁSÚ PROBLÉMÁK

### K1. Dockerfile Multi-stage Build Optimalizálás

**Probléma:**
A Dockerfile-ok használnak multi-stage build-et (✅ jó), de **nem optimálisak**:

1. **Teljes backend mappa másolása** minden service-nél:
   ```dockerfile
   COPY backend/ /app/backend/  # ⚠️ Minden service látja a többi service kódját
   ```

2. **Layer caching nem optimális:**
   ```dockerfile
   # Rossz sorrend:
   COPY backend/ /app/backend/
   RUN pip install -r requirements.txt  # Requirements-et korábban kellene
   ```

**Hatás:**
- **Nagyobb image méret:** Minden service image-ben benne van az ÖSSZES többi service kódja
- **Lassabb build:** Bármely service módosítása mindent újra build-el
- **Biztonsági kockázat:** Service izolálás sérül

**Optimalizált Dockerfile (példa service_menu-re):**

```dockerfile
# ============================================================================
# OPTIMALIZÁLT Dockerfile - Service Menu
# ============================================================================

# Stage 1: Builder - Dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy ONLY requirements first (for layer caching)
COPY backend/service_menu/requirements.txt .

# Install Python dependencies to /root/.local
RUN pip install --no-cache-dir --user -r requirements.txt

# ============================================================================
# Stage 2: Runtime
FROM python:3.11-slim AS runtime

WORKDIR /app

# Install ONLY runtime dependencies (not gcc)
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user (SECURITY FIX)
RUN groupadd -r appuser && useradd -r -g appuser -u 1000 appuser

# Copy Python dependencies from builder
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Make sure scripts in .local are usable
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy ONLY service_menu code (not entire backend)
COPY --chown=appuser:appuser backend/service_menu/ /app/backend/service_menu/

# Copy ONLY shared dependencies (if any)
COPY --chown=appuser:appuser backend/__init__.py /app/backend/
# If there are shared models/schemas in backend/shared/:
# COPY --chown=appuser:appuser backend/shared/ /app/backend/shared/

# Create credentials directory
RUN mkdir -p /app/credentials && chown -R appuser:appuser /app/credentials

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8001

# Health check (as non-root user, curl must be installed)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run application
CMD ["uvicorn", "backend.service_menu.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

**Build méret csökkentés várható:**
- Jelenlegi: ~800-1000MB per service
- Optimalizált: ~400-500MB per service
- **~50% csökkentés**

---

### K2. Hiányzó Health Check Dependency Ordering

**Probléma:**
A `depends_on` használ condition: service_healthy-t, de **nem minden szolgáltatás rendelkezik health check-kel**.

**Például:**
```yaml
service_orders:
  depends_on:
    postgres:
      condition: service_healthy
    service_menu:
      condition: service_healthy  # ✅ service_menu HAS healthcheck
```

**De nincs dependency check a többi service-re**, pedig inter-service kommunikáció van:

```yaml
# service_orders environment:
INVENTORY_SERVICE_URL: http://service_inventory:8003  # De nincs depends_on!
```

**Megoldás:**

```yaml
service_orders:
  depends_on:
    postgres:
      condition: service_healthy
    service_menu:
      condition: service_healthy
    service_inventory:  # HOZZÁADANDÓ
      condition: service_healthy
    service_admin:      # HOZZÁADANDÓ
      condition: service_healthy
```

**Vagy használjunk init container pattern-t** vagy retry logikát az alkalmazásban.

---

### K3. GCP Credentials Volume Mount Biztonsági Problémák

**Probléma:**
A Google Cloud credentials **host fájlrendszerről van mount-olva**:

```yaml
volumes:
  - ${GOOGLE_CREDENTIALS_PATH:-./credentials}:/app/credentials:ro
```

**Hatás:**
- Ha a host credentials kompromittálódik, minden konténer hozzáfér
- Credentials a host fájlrendszeren van, könnyebb célpont
- Kubernetes-ben nem működik (más megközelítés kell)

**Megoldás Docker Compose-ban (fejlesztéshez):**

```yaml
# Maradhat, de szigorúbb permissions-ökkel
volumes:
  - ${GOOGLE_CREDENTIALS_PATH:-./credentials}:/app/credentials:ro

# .env fájlban:
GOOGLE_CREDENTIALS_PATH=./credentials
```

**Fájl jogosultságok:**
```bash
chmod 600 ./credentials/gcp-key.json
chmod 700 ./credentials/
```

**Kubernetes/GKE-hez (production):**

```yaml
# Használni kell Workload Identity-t GKE-ban
# Vagy Kubernetes Secrets-et:

apiVersion: v1
kind: Secret
metadata:
  name: gcp-credentials
type: Opaque
data:
  gcp-key.json: <base64-encoded-json>
---
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: app
    volumeMounts:
    - name: gcp-creds
      mountPath: /app/credentials
      readOnly: true
  volumes:
  - name: gcp-creds
    secret:
      secretName: gcp-credentials
```

---

### K4. Nincs Network Segmentation

**Probléma:**
Minden szolgáltatás **ugyanazon a pos-network bridge network-ön** van, nincs szegmentálás.

**Hatás:**
- Minden szolgáltatás eléri a másikat (nincs zero-trust)
- Ha egy service compromised, hozzáfér mindenhova
- Nincs network policy enforcement

**Jobb Architektúra (opcionális, komplex):**

```yaml
networks:
  frontend-network:
    driver: bridge
  backend-network:
    driver: bridge
  database-network:
    driver: bridge
    internal: true  # Nincs külső hozzáférés

services:
  postgres:
    networks:
      - database-network  # Csak database network

  service_menu:
    networks:
      - frontend-network  # API gateway-hez
      - backend-network   # Többi service-hez
      - database-network  # Adatbázishoz

  # API Gateway (később hozzáadandó)
  api-gateway:
    networks:
      - frontend-network  # Külső eléréshez
```

**Kubernetes-ben ezt Network Policies-szel kell megoldani.**

---

## 📊 KUBERNETES KOMPATIBILITÁS HIÁNYOSSÁGOK

### KUB1. Nincs Kubernetes Manifest

**Probléma:**
Nincs egyetlen Kubernetes manifest sem (Deployment, Service, ConfigMap, Secret, Ingress).

**Megoldás:**
Létrehozandó `k8s/` könyvtár a következő fájlokkal:

```
k8s/
├── base/
│   ├── namespace.yaml
│   ├── postgres-statefulset.yaml
│   ├── postgres-service.yaml
│   ├── postgres-pvc.yaml
│   ├── service-menu-deployment.yaml
│   ├── service-menu-service.yaml
│   ├── service-orders-deployment.yaml
│   ├── service-orders-service.yaml
│   ├── service-inventory-deployment.yaml
│   ├── service-inventory-service.yaml
│   ├── service-admin-deployment.yaml
│   ├── service-admin-service.yaml
│   ├── service-crm-deployment.yaml
│   ├── service-crm-service.yaml
│   ├── service-logistics-deployment.yaml
│   ├── service-logistics-service.yaml
│   ├── configmap.yaml
│   ├── secrets.yaml (NEVER commit - use sealed-secrets or external-secrets)
│   └── ingress.yaml
├── overlays/
│   ├── development/
│   │   └── kustomization.yaml
│   ├── staging/
│   │   └── kustomization.yaml
│   └── production/
│       └── kustomization.yaml
└── README.md
```

**Példa Deployment (service_menu):**

```yaml
# k8s/base/service-menu-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: service-menu
  namespace: pos-system
  labels:
    app: pos
    service: menu
    version: v1
spec:
  replicas: 2  # HA (High Availability)
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: pos
      service: menu
  template:
    metadata:
      labels:
        app: pos
        service: menu
        version: v1
    spec:
      # SECURITY: Non-root user
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
        seccompProfile:
          type: RuntimeDefault

      # Init container (wait for postgres)
      initContainers:
      - name: wait-for-postgres
        image: busybox:1.36
        command: ['sh', '-c', 'until nc -z postgres 5432; do echo waiting for postgres; sleep 2; done']

      containers:
      - name: app
        image: ghcr.io/restiapp/pos-service_menu:latest
        imagePullPolicy: Always

        # SECURITY: Container security context
        securityContext:
          allowPrivilegeEscalation: false
          capabilities:
            drop:
              - ALL
          readOnlyRootFilesystem: true  # Immutable container

        # Port configuration
        ports:
        - name: http
          containerPort: 8001
          protocol: TCP

        # Environment variables from ConfigMap
        envFrom:
        - configMapRef:
            name: pos-config

        # Secrets
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: connection-string
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: jwt-secret
              key: secret-key

        # Resource limits (CRITICAL for production)
        resources:
          requests:
            cpu: 250m
            memory: 256Mi
          limits:
            cpu: 1000m
            memory: 512Mi

        # Health checks (CRITICAL for K8s)
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 40
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3

        readinessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3

        # Volume mounts (credentials)
        volumeMounts:
        - name: gcp-credentials
          mountPath: /app/credentials
          readOnly: true
        - name: tmp
          mountPath: /tmp  # Writable temp directory

      # Volumes
      volumes:
      - name: gcp-credentials
        secret:
          secretName: gcp-service-account
      - name: tmp
        emptyDir: {}

      # Image pull secrets (if using private registry)
      # imagePullSecrets:
      # - name: ghcr-secret
```

---

### KUB2. Nincs Readiness/Liveness Probe Különbség

**Probléma:**
Bár vannak healthcheck-ek, **nincs különbség a readiness és liveness probe-ok között**.

**Kubernetes-ben:**
- **Liveness Probe:** Ellenőrzi, hogy az alkalmazás él-e (ha nem, restart)
- **Readiness Probe:** Ellenőrzi, hogy az alkalmazás kész-e forgalmat fogadni (ha nem, kikerül a load balancer-ből)

**Megoldás az alkalmazásban:**

Külön endpoint-ok létrehozása:
```python
# backend/service_menu/main.py

@app.get("/health")
async def health_check():
    """Liveness probe - csak azt ellenőrzi, hogy az app fut"""
    return {"status": "ok"}

@app.get("/ready")
async def readiness_check():
    """Readiness probe - ellenőrzi a függőségeket is"""
    try:
        # Check database connection
        db.execute("SELECT 1")

        # Check GCS connection (optional)
        # ...

        return {"status": "ready", "database": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Not ready: {str(e)}")
```

---

### KUB3. Nincs Horizontal Pod Autoscaler (HPA)

**Megoldás:**

```yaml
# k8s/base/service-menu-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: service-menu
  namespace: pos-system
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: service-menu
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 15
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 4
        periodSeconds: 15
      selectPolicy: Max
```

---

## 🎯 OPTIMALIZÁLÁSI JAVASLATOK

### OPT1. Multi-Architecture Build

**Javaslat:**
Támogatás ARM64 és AMD64 platformokra (Apple Silicon, AWS Graviton, stb.)

```yaml
# .github/workflows/ci-cd.yml módosítva
- name: Build and push multi-platform Docker image
  uses: docker/build-push-action@v5
  with:
    context: .
    file: backend/${{ matrix.service }}/Dockerfile
    platforms: linux/amd64,linux/arm64  # Multi-platform
    push: true
    tags: ${{ steps.meta.outputs.tags }}
```

---

### OPT2. Build Cache Optimization

```dockerfile
# Dockerfile-okban

# BEFORE (no cache optimization):
COPY backend/ /app/backend/

# AFTER (with cache optimization):
# 1. Copy only requirements first
COPY backend/service_menu/requirements.txt /app/requirements.txt

# 2. Install dependencies (cached if requirements unchanged)
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy code (this layer changes frequently)
COPY backend/service_menu/ /app/backend/service_menu/
```

---

### OPT3. Image Méret Csökkentése

**Jelenlegi problémák:**
- Teljes backend mappa másolása
- gcc és build tools a runtime image-ben
- __pycache__ fájlok

**Optimalizált megközelítés:**

```dockerfile
# Multi-stage build with smaller final image
FROM python:3.11-slim AS runtime

# SECURITY + SIZE: Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Remove unnecessary files
RUN find /usr/local -depth \
    \( \
        \( -type d -a \( -name test -o -name tests -o -name __pycache__ \) \) \
        -o \( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
    \) -exec rm -rf '{}' + \
    && rm -rf /usr/share/doc /usr/share/man /var/cache/apt/archives
```

---

### OPT4. Docker Compose Override Pattern

**Javaslat:**
Különböző környezetekhez külön override fájlok.

```bash
# Fájl struktúra:
docker-compose.yml           # Base config (közös minden környezethez)
docker-compose.dev.yml       # Development overrides
docker-compose.test.yml      # Testing overrides
docker-compose.prod.yml      # Production overrides

# Használat:
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

**Példa docker-compose.dev.yml:**

```yaml
services:
  postgres:
    ports:
      - "5432:5432"  # Exposed fejlesztéshez (pgAdmin hozzáférés)

  service_menu:
    build:
      target: development  # Development stage a Dockerfile-ban
    volumes:
      - ./backend/service_menu:/app/backend/service_menu:ro  # Hot reload
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG

  # pgAdmin hozzáadása fejlesztéshez
  pgadmin:
    image: dpage/pgadmin4:latest
    ports:
      - "5050:80"
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@pos.local
      PGADMIN_DEFAULT_PASSWORD: admin
    networks:
      - pos-network
```

**Példa docker-compose.prod.yml:**

```yaml
services:
  postgres:
    # ports:  # NEM EXPOSED production-ban
    expose:
      - "5432"
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G

  service_menu:
    build:
      target: production
    restart: always
    environment:
      - DEBUG=false
      - LOG_LEVEL=INFO
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
    logging:
      driver: "fluentd"
      options:
        fluentd-address: "fluentd:24224"
```

---

### OPT5. Healthcheck Improvement

**Jelenlegi problémák:**
- Egyszerű curl hívások
- Nincs dependency check
- Service_admin Python-nal hívja meg (lassú)

**Optimalizált healthcheck script:**

```bash
# scripts/healthcheck.sh (minden service-hez)
#!/bin/sh
set -e

# Quick HTTP check
if ! curl -f -s -o /dev/null http://localhost:${PORT:-8000}/health; then
    exit 1
fi

# Optional: Check database connection (only if critical)
# python -c "from backend.service_menu.models.database import engine; engine.execute('SELECT 1')" || exit 1

exit 0
```

```dockerfile
# Dockerfile-ban:
COPY scripts/healthcheck.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/healthcheck.sh

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh
```

---

## 📋 ÖSSZEFOGLALÓ CSELEKVÉSI TERV

### KRITIKUS (1-3 nap)

- [ ] **K1:** service_crm és service_logistics hozzáadása docker-compose.yml-hez
- [ ] **K2:** .dockerignore fájl létrehozása
- [ ] **K3:** Non-root user minden Dockerfile-ban
- [ ] **K4:** Docker Secrets implementálása JWT_SECRET_KEY, POSTGRES_PASSWORD, NTAK_API_KEY számára
- [ ] **K5:** GitHub Actions CI/CD pipeline alapok (build, test, push)

### MAGAS PRIORITÁS (1 hét)

- [ ] **M1:** Port inconsistency javítása (service_menu, service_orders)
- [ ] **M2:** Resource limits hozzáadása minden service-hez
- [ ] **M3:** PostgreSQL port eltávolítása production környezetben
- [ ] **M4:** Logging konfiguráció (max-size, max-file)
- [ ] **M5:** version: '3.8' eltávolítása docker-compose.yml-ből

### KÖZEPES PRIORITÁS (2-3 hét)

- [ ] **K1:** Dockerfile optimalizálás (csak szükséges fájlok másolása)
- [ ] **K2:** Health check dependency ordering javítása
- [ ] **K3:** GCP credentials jogosultságok szigorítása (chmod 600)
- [ ] **K4:** (Opcionális) Network segmentation implementálása
- [ ] **GitHub Actions:** Security scanning (Trivy)
- [ ] **GitHub Actions:** Integration tests docker-compose-zal

### ALACSONY PRIORITÁS / LONG-TERM (1-2 hónap)

- [ ] **KUB1:** Kubernetes manifests létrehozása (Deployment, Service, ConfigMap, Secret, Ingress)
- [ ] **KUB2:** Readiness/Liveness probe endpoint-ok létrehozása (/ready, /health)
- [ ] **KUB3:** HPA (Horizontal Pod Autoscaler) konfigurálása
- [ ] **OPT1:** Multi-architecture build (ARM64 + AMD64)
- [ ] **OPT2:** Build cache optimization finomhangolása
- [ ] **OPT3:** Image size további csökkentése (distroless image?)
- [ ] **OPT4:** Docker Compose override pattern (dev/test/prod)
- [ ] **OPT5:** Advanced healthcheck script-ek
- [ ] **Monitoring:** Prometheus exporter hozzáadása minden service-hez
- [ ] **Monitoring:** Grafana dashboard-ok
- [ ] **Observability:** OpenTelemetry integráció (distributed tracing)

---

## 🔒 BIZTONSÁGI ELLENŐRZŐ LISTA

- [ ] Nincs hardcoded password/secret a kódban
- [ ] .env fájl a .gitignore-ban
- [ ] Docker Secrets használata érzékeny adatokhoz
- [ ] Konténerek non-root user-ként futnak
- [ ] .dockerignore fájl létezik és helyes
- [ ] PostgreSQL port nincs exposed production-ban
- [ ] Resource limits beállítva (DoS elleni védelem)
- [ ] Image vulnerability scanning a CI/CD-ben
- [ ] HTTPS használata production-ban (még nincs implementálva)
- [ ] Network policies (Kubernetes)
- [ ] Pod Security Standards compliance (Kubernetes)
- [ ] Secrets encryption at rest

---

## 📚 TOVÁBBI DOKUMENTÁCIÓS IGÉNYEK

### Létrehozandó Dokumentumok:

1. **KUBERNETES_DEPLOYMENT.md**
   - Kubernetes deployment útmutató
   - Helm chart (opcionális)
   - ArgoCD / FluxCD GitOps workflow

2. **CI_CD_GUIDE.md**
   - GitHub Actions workflow részletes leírása
   - Branch strategy (main, develop, feature/*)
   - Release management

3. **SECURITY_GUIDELINES.md**
   - Secrets management best practices
   - Vulnerability scanning process
   - Incident response plan

4. **MONITORING_OBSERVABILITY.md**
   - Prometheus metrics
   - Grafana dashboards
   - Log aggregation (Loki, ELK stb.)
   - Distributed tracing (Jaeger, Zipkin)

5. **DOCKER_COMPOSE_ENVIRONMENTS.md**
   - Development setup
   - Testing setup
   - Production setup

---

## 🎓 KÉPZÉSI JAVASLATOK A FEJLESZTŐI CSAPATNAK

1. **Docker Best Practices Workshop**
   - Multi-stage builds
   - Layer caching
   - Security hardening

2. **Kubernetes Fundamentals**
   - Deployments, Services, ConfigMaps, Secrets
   - Health checks
   - Resource management

3. **CI/CD Pipeline Development**
   - GitHub Actions
   - GitOps principles
   - Blue-Green deployment, Canary releases

4. **Security-First Development**
   - OWASP Top 10
   - Container security
   - Secrets management

---

## 📞 KÖVETKEZŐ LÉPÉSEK

### Ajánlott Sorrend:

**1. Gyors Javítások (1-2 nap):**
   - .dockerignore létrehozása
   - service_crm és service_logistics hozzáadása docker-compose.yml-hez
   - Port inconsistency-k javítása

**2. Biztonság (3-5 nap):**
   - Non-root user minden Dockerfile-ban
   - Docker Secrets implementálása
   - PostgreSQL port eltávolítása production-ből

**3. CI/CD Alapok (1 hét):**
   - GitHub Actions alapvető workflow
   - Build és push image-ek
   - Automatizált tesztek

**4. Optimalizálás (2-3 hét):**
   - Dockerfile optimalizálás
   - Resource limits
   - Logging konfiguráció

**5. Production-Ready (1-2 hónap):**
   - Kubernetes manifests
   - Monitoring és observability
   - Full CI/CD pipeline (staging, production)

---

## ✅ AUDIT ZÁRSZÓ

A projekt Docker infrastruktúrája **alapvetően jó úton halad**, de **még nem production-ready**. A **legkritikusabb problémák a biztonság terén** vannak (root user, nincs secrets management, nincs CI/CD), amelyeket **sürgősen kezelni kell**.

**Pozitívumok:**
- ✅ Multi-stage Dockerfile-ok
- ✅ Health check-ek
- ✅ Dependency ordering (postgres)
- ✅ Részletes dokumentáció (DOCKER_DEPLOYMENT.md)

**Negatívumok:**
- ❌ Hiányzó szolgáltatások a compose-ból
- ❌ Root user használata
- ❌ Nincs .dockerignore
- ❌ Nincs CI/CD egyáltalán
- ❌ Nincs Kubernetes kompatibilitás

**Időbecslés a production-ready állapotra:**
- **Minimálisan működő (staging):** 2-3 hét
- **Production-ready (alapszintű):** 1-2 hónap
- **Fully optimized + Kubernetes:** 2-3 hónap

---

**Audit Készítette:**
Agent #4 - Docker, DevOps & CI/CD Specialist
**Dátum:** 2025-11-22
**Következő Felülvizsgálat:** 2026-01-22 (2 hónap múlva)
