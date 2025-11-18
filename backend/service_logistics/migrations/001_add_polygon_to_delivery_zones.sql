-- Migration: Add polygon field to delivery_zones table
-- V3.0 / Phase 4.2: Google Maps/GeoJSON Integration
-- Date: 2025-01-18
-- Description: Adds a JSON column to store GeoJSON polygon data for delivery zones

-- Add polygon column (JSON type for GeoJSON compatibility)
ALTER TABLE delivery_zones
ADD COLUMN IF NOT EXISTS polygon JSON DEFAULT NULL;

-- Add comment to the column
COMMENT ON COLUMN delivery_zones.polygon IS 'GeoJSON polygon defining the delivery zone boundary (V3.0 Phase 4.2)';

-- Example polygon structure:
-- {
--   "type": "Polygon",
--   "coordinates": [
--     [
--       [19.0402, 47.4979],
--       [19.0502, 47.4979],
--       [19.0502, 47.5079],
--       [19.0402, 47.5079],
--       [19.0402, 47.4979]
--     ]
--   ]
-- }
