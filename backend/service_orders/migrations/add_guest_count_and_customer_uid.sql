-- Migration: Add guest_count and customer_uid to orders table
-- Date: 2025-11-19
-- Feature: Task A2 - Vendégszám + CRM Integráció

-- Add customer_uid column (Vendégszám / Customer UID from CRM)
ALTER TABLE orders
ADD COLUMN IF NOT EXISTS customer_uid VARCHAR(50);

-- Add guest_count column (Number of guests for this order)
ALTER TABLE orders
ADD COLUMN IF NOT EXISTS guest_count INTEGER;

-- Create index on customer_uid for faster lookups
CREATE INDEX IF NOT EXISTS idx_orders_customer_uid ON orders(customer_uid);

-- Add comments for documentation
COMMENT ON COLUMN orders.customer_uid IS 'Customer UID (Vendégszám) from CRM system (e.g., CUST-123456)';
COMMENT ON COLUMN orders.guest_count IS 'Number of guests for this order';

-- Migration complete
