# Service CRM Database Migrations

This directory contains database migration scripts for the Service CRM module.

## Available Migrations

### 1. Add Customer Tags and Last Visit (2025-11-20)
**Files:**
- `add_customer_tags_and_last_visit.sql` - SQL migration script
- `add_customer_tags_and_last_visit.py` - Python migration runner

**Changes:**
- Adds `tags` column (JSON) to `customers` table for customer labels/categorization
- Adds `last_visit` column (TIMESTAMP) to `customers` table for tracking last visit/order
- Creates index on `last_visit` for query performance

**How to run:**
```bash
# Option 1: Run Python script (recommended)
cd backend/service_crm
python migrations/add_customer_tags_and_last_visit.py

# Option 2: Run SQL directly
psql -U postgres -d pos_db -f migrations/add_customer_tags_and_last_visit.sql
```

## Notes

- For development/testing, the `init_db()` function in `models/database.py` will create tables automatically
- However, `create_all()` doesn't modify existing tables, so migrations are needed for schema changes
- In production, use proper migration tools like Alembic
- Always backup your database before running migrations
