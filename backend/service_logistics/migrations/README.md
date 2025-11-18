# Service Logistics Database Migrations

## Overview
This directory contains SQL migration scripts for the `service_logistics` database schema.

## Migrations

### 001_add_polygon_to_delivery_zones.sql
**Version:** V3.0 / Phase 4.2
**Date:** 2025-01-18
**Status:** Applied

**Description:**
Adds GeoJSON polygon support to the `delivery_zones` table to enable Point-in-Polygon geographic lookups.

**Changes:**
- Adds `polygon` column (JSON type) to store GeoJSON Polygon geometries
- Enables real geographic boundary detection using Shapely library

**How to Apply:**
```bash
psql -U your_user -d your_database -f 001_add_polygon_to_delivery_zones.sql
```

**Example Polygon Data:**
```json
{
  "type": "Polygon",
  "coordinates": [
    [
      [19.0402, 47.4979],
      [19.0502, 47.4979],
      [19.0502, 47.5079],
      [19.0402, 47.5079],
      [19.0402, 47.4979]
    ]
  ]
}
```

## Migration Strategy

1. **Manual Application**: Currently, migrations are applied manually using SQL scripts
2. **Future Enhancement**: Consider integrating Alembic for automatic migration management
3. **Rollback**: Each migration should include rollback instructions in comments

## Notes

- All migrations should be idempotent (safe to run multiple times)
- Use `IF NOT EXISTS` clauses where applicable
- Always backup database before applying migrations
- Test migrations on staging environment first
