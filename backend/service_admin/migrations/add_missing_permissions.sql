-- ============================================================================
-- RBAC Permissions Migration - V3.0 Phase X
-- ============================================================================
-- Hiányzó kritikus jogosultságok hozzáadása a permissions táblához
--
-- Használat:
--   psql -U postgres -d restiapp_admin < add_missing_permissions.sql
--
-- FIGYELEM: Ez a szkript idempotens - újrafuttatható.
-- ============================================================================

BEGIN;

-- Finance Management (Pénzügyek kezelése)
INSERT INTO permissions (name, display_name, description, resource, action, is_system, is_active, created_at, updated_at)
VALUES
    ('finance:manage', 'Pénzügyek kezelése', 'Számlák, kifizetések, pénzügyi tételek kezelése', 'finance', 'manage', TRUE, TRUE, NOW(), NOW()),
    ('finance:view', 'Pénzügyek megtekintése', 'Pénzügyi adatok és számlák megtekintése', 'finance', 'view', TRUE, TRUE, NOW(), NOW())
ON CONFLICT (name) DO NOTHING;

-- Asset Management (Eszköznyilvántartás)
INSERT INTO permissions (name, display_name, description, resource, action, is_system, is_active, created_at, updated_at)
VALUES
    ('assets:manage', 'Eszközök kezelése', 'Eszközök, berendezések, tárgyi eszközök nyilvántartása és kezelése', 'assets', 'manage', TRUE, TRUE, NOW(), NOW()),
    ('assets:view', 'Eszközök megtekintése', 'Eszköznyilvántartás megtekintése', 'assets', 'view', TRUE, TRUE, NOW(), NOW())
ON CONFLICT (name) DO NOTHING;

-- Vehicle Management (Gépjárműnyilvántartás)
INSERT INTO permissions (name, display_name, description, resource, action, is_system, is_active, created_at, updated_at)
VALUES
    ('vehicles:manage', 'Járművek kezelése', 'Járművek, tankolások, karbantartások kezelése', 'vehicles', 'manage', TRUE, TRUE, NOW(), NOW()),
    ('vehicles:view', 'Járművek megtekintése', 'Járművek és kapcsolódó adatok megtekintése', 'vehicles', 'view', TRUE, TRUE, NOW(), NOW())
ON CONFLICT (name) DO NOTHING;

-- Logistics Management (Logisztika)
INSERT INTO permissions (name, display_name, description, resource, action, is_system, is_active, created_at, updated_at)
VALUES
    ('logistics:manage', 'Logisztika kezelése', 'Futárok, kiszállítási zónák, szállítások kezelése', 'logistics', 'manage', TRUE, TRUE, NOW(), NOW()),
    ('logistics:view', 'Logisztika megtekintése', 'Logisztikai adatok megtekintése', 'logistics', 'view', TRUE, TRUE, NOW(), NOW())
ON CONFLICT (name) DO NOTHING;

-- Admin Role frissítése - új jogosultságok hozzáadása
-- (csak ha az Admin role ID = 1)
DO $$
DECLARE
    admin_role_id INT;
    perm_id INT;
BEGIN
    -- Admin role ID lekérése
    SELECT id INTO admin_role_id FROM roles WHERE name = 'Admin' LIMIT 1;

    IF admin_role_id IS NOT NULL THEN
        -- Finance permissions hozzáadása
        FOR perm_id IN SELECT id FROM permissions WHERE name IN ('finance:manage', 'assets:manage', 'vehicles:manage', 'logistics:manage')
        LOOP
            INSERT INTO role_permissions (role_id, permission_id)
            VALUES (admin_role_id, perm_id)
            ON CONFLICT (role_id, permission_id) DO NOTHING;
        END LOOP;

        RAISE NOTICE 'Admin role frissítve az új jogosultságokkal.';
    ELSE
        RAISE NOTICE 'Admin role nem található, role_permissions frissítés kihagyva.';
    END IF;
END $$;

COMMIT;

-- Ellenőrzés
SELECT
    COUNT(*) as total_permissions,
    COUNT(*) FILTER (WHERE resource IN ('finance', 'assets', 'vehicles', 'logistics')) as new_permissions
FROM permissions;
