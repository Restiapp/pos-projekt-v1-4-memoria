# Docker Deployment Guide - POS System

Complete guide for deploying the POS microservices architecture using Docker Compose.

## 📋 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Restiapp/pos-projekt-v1-4-memoria.git
cd pos-projekt-v1-4-memoria

# 2. Copy environment variables template
cp .env.example .env

# 3. Edit .env with your actual values
nano .env  # or use your preferred editor

# 4. Start all services
docker-compose up -d

# 5. View logs
docker-compose logs -f

# 6. Check service status
docker-compose ps
```

## 🏗️ Architecture Overview

The system consists of 5 Docker containers:

| Service | Container | Port | Description |
|---------|-----------|------|-------------|
| **PostgreSQL** | `pos-postgres` | 5432 | Main database |
| **Menu Service** | `pos-service-menu` | 8001 | Module 0 - Products, Categories |
| **Orders Service** | `pos-service-orders` | 8002 | Module 1 - Orders, Tables |
| **Inventory Service** | `pos-service-inventory` | 8003 | Module 5 - Inventory, OCR |
| **Admin Service** | `pos-service-admin` | 8008 | Module 6 & 8 - RBAC, NTAK |

## 🔧 Prerequisites

### Required Software

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher

```bash
# Check versions
docker --version
docker-compose --version
```

### Required Credentials

1. **Google Cloud Platform Service Account**
   - Create a service account with permissions for:
     - Cloud Storage (read/write)
     - Vertex AI Translation API
     - Document AI API
   - Download JSON key file
   - Place in `./credentials/gcp-key.json`

2. **NTAK API Credentials** (Optional for testing)
   - Register at Hungarian Tax Authority (NAV)
   - Obtain API key and merchant ID

## 📝 Configuration

### 1. Environment Variables (.env)

Copy the example file and customize:

```bash
cp .env.example .env
```

**Critical variables to change:**

```bash
# Database
POSTGRES_PASSWORD=your-strong-password

# JWT Secret (CRITICAL!)
JWT_SECRET_KEY=your-super-secret-jwt-key-min-32-chars

# GCP Project
VERTEX_PROJECT_ID=your-gcp-project-id
DOCUMENTAI_PROJECT_ID=your-gcp-project-id
GCS_BUCKET_NAME=your-gcs-bucket-name
DOCUMENTAI_PROCESSOR_ID=your-processor-id

# NTAK (Production)
NTAK_API_KEY=your-ntak-api-key
NTAK_MERCHANT_ID=your-merchant-id
```

### 2. Google Cloud Credentials

```bash
# Create credentials directory
mkdir -p credentials

# Copy your GCP service account key
cp ~/Downloads/your-gcp-key.json ./credentials/gcp-key.json

# Ensure proper permissions
chmod 600 ./credentials/gcp-key.json
```

### 3. Build Dockerfiles (if not created yet)

Each service needs a `Dockerfile`. Currently only `service_menu` has one. You'll need to create similar Dockerfiles for:

- `backend/service_orders/Dockerfile`
- `backend/service_inventory/Dockerfile`
- `backend/service_admin/Dockerfile`

Use `backend/service_menu/Dockerfile` as a template.

## 🚀 Deployment Commands

### Start All Services

```bash
# Start in background (detached mode)
docker-compose up -d

# Start with build (if Dockerfiles changed)
docker-compose up -d --build

# Start specific service
docker-compose up -d service_menu
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f service_menu

# Last 100 lines
docker-compose logs --tail=100 service_orders
```

### Stop Services

```bash
# Stop all services (keeps data)
docker-compose stop

# Stop and remove containers (keeps volumes)
docker-compose down

# Stop and remove everything including volumes
docker-compose down -v
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart service_admin
```

### Check Status

```bash
# Service status
docker-compose ps

# Resource usage
docker stats
```

## 🗄️ Database Management

### Run Database Seeding

```bash
# Execute seeding script in admin service container
docker-compose exec service_admin python -m backend.service_admin.seed_rbac
```

Expected output:
```
🚀 RBAC Database Seeding - Module 6
✅ 16 jogosultság feltöltve
✅ 3 szerepkör feltöltve
✅ Admin felhasználó létrehozva
🎉 SEEDING SIKERES!
```

### Access PostgreSQL

```bash
# Connect to database
docker-compose exec postgres psql -U pos_user -d pos_db

# Run SQL query
docker-compose exec postgres psql -U pos_user -d pos_db -c "SELECT * FROM employees;"

# Backup database
docker-compose exec postgres pg_dump -U pos_user pos_db > backup.sql

# Restore database
docker-compose exec -T postgres psql -U pos_user pos_db < backup.sql
```

### Database Migrations (Future)

```bash
# Run Alembic migrations (when implemented)
docker-compose exec service_admin alembic upgrade head
```

## 🧪 Testing Services

### Health Checks

```bash
# Check all services
curl http://localhost:8001/health  # Menu
curl http://localhost:8002/health  # Orders
curl http://localhost:8003/health  # Inventory
curl http://localhost:8008/health  # Admin
```

### API Documentation

Access Swagger UI for each service:

- Menu Service: http://localhost:8001/docs
- Orders Service: http://localhost:8002/docs
- Inventory Service: http://localhost:8003/docs
- Admin Service: http://localhost:8008/docs

### Test Authentication

```bash
# Login (get JWT token)
curl -X POST http://localhost:8008/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "pin_code": "1234"
  }'

# Use token for authenticated request
curl -X GET http://localhost:8001/api/v1/products \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🔍 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs service_name

# Check container inspect
docker inspect pos-service-menu

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Connection Issues

```bash
# Check if PostgreSQL is healthy
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Verify connection from service
docker-compose exec service_menu python -c "from backend.service_menu.models.database import engine; print(engine.execute('SELECT 1').scalar())"
```

### Port Conflicts

If ports 8001-8003, 8008, or 5432 are already in use:

```yaml
# Edit docker-compose.yml
ports:
  - "8081:8000"  # Change host port (left side)
```

### Permission Issues

```bash
# Fix credentials permissions
chmod 600 ./credentials/gcp-key.json

# Fix volume permissions
docker-compose down
sudo chown -R $USER:$USER ./credentials
docker-compose up -d
```

## 🔒 Security Considerations

### Production Deployment

1. **Change Default Passwords**
   - Admin PIN: Change from `1234`
   - Database password
   - JWT secret key

2. **Use Secrets Management**
   - Docker Swarm secrets
   - Kubernetes secrets
   - Cloud provider secret managers

3. **Network Security**
   - Use internal networks for inter-service communication
   - Expose only necessary ports
   - Use reverse proxy (nginx, traefik)

4. **SSL/TLS**
   - Enable HTTPS for all external endpoints
   - Use Let's Encrypt or cloud provider certificates

5. **Resource Limits**

```yaml
# Add to docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
    reservations:
      cpus: '0.25'
      memory: 256M
```

## 📊 Monitoring

### View Resource Usage

```bash
# Real-time stats
docker stats

# Container resource usage
docker-compose top
```

### Logging

```bash
# JSON structured logs
docker-compose logs --json

# Export logs
docker-compose logs > logs.txt
```

## 🆙 Updates and Maintenance

### Update Images

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Backup Strategy

```bash
# Backup script example
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec postgres pg_dump -U pos_user pos_db > backups/pos_db_$DATE.sql
tar -czf backups/volumes_$DATE.tar.gz -C /var/lib/docker/volumes pos-postgres-data
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [FastAPI in Docker](https://fastapi.tiangolo.com/deployment/docker/)

## 🆘 Support

For issues and questions:

1. Check logs: `docker-compose logs -f`
2. Review this guide's troubleshooting section
3. Consult ARCHITECTURE.md for system design
4. Open an issue on GitHub

---

**Last Updated**: 2025-01-16
**Version**: 1.0.0
**Maintained by**: Restiapp Development Team
