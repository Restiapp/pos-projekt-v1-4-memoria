-- Migration: Add courier_id to orders table
-- V3.0 / LOGISTICS-FIX: Connect Orders to Couriers from service_logistics
-- Date: 2025-11-20

-- Add courier_id column to orders table
ALTER TABLE orders
ADD COLUMN IF NOT EXISTS courier_id INTEGER;

-- Create index on courier_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_orders_courier_id ON orders(courier_id);

-- Add comment to explain the column
COMMENT ON COLUMN orders.courier_id IS 'V3.0: Futár hivatkozás (service_logistics courier ID)';
