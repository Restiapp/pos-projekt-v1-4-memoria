-- Migration: Add tags and last_visit columns to customers table
-- Module 5: Service CRM
-- Date: 2025-11-20
-- Description: Enhances Customer model with tags (JSON) and last_visit (TIMESTAMP) fields

-- Add tags column (JSON array for customer labels/tags)
ALTER TABLE customers
ADD COLUMN IF NOT EXISTS tags JSON DEFAULT NULL;

-- Add last_visit column (timestamp for tracking last customer visit/order)
ALTER TABLE customers
ADD COLUMN IF NOT EXISTS last_visit TIMESTAMP WITH TIME ZONE DEFAULT NULL;

-- Add index on last_visit for performance (optional but recommended)
CREATE INDEX IF NOT EXISTS idx_customers_last_visit ON customers(last_visit);

-- Add comments for documentation
COMMENT ON COLUMN customers.tags IS 'Customer tags/labels stored as JSON array (e.g., ["VIP", "Regular", "New"])';
COMMENT ON COLUMN customers.last_visit IS 'Timestamp of customer last visit/order';
