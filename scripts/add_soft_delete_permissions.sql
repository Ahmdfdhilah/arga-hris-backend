-- ============================================================
-- Add Soft Delete Permissions for Employee & Org Unit
-- Date: 2025-11-29
-- Description: Manual SQL to add soft delete permissions
--              without creating new alembic migration
-- ============================================================

-- Step 1: Insert new permissions
-- ============================================================
INSERT INTO permissions (code, description, resource, action, created_at, updated_at)
VALUES
    -- Employee soft delete permissions
    ('employee.soft_delete', 'Archive employee (soft delete)', 'employee', 'soft_delete', NOW(), NOW()),
    ('employee.restore', 'Restore archived employee', 'employee', 'restore', NOW(), NOW()),
    ('employee.view_deleted', 'View archived/deleted employees', 'employee', 'view_deleted', NOW(), NOW()),

    -- Org Unit soft delete permissions
    ('org_unit.soft_delete', 'Archive org unit (soft delete)', 'org_unit', 'soft_delete', NOW(), NOW()),
    ('org_unit.restore', 'Restore archived org unit', 'org_unit', 'restore', NOW(), NOW()),
    ('org_unit.view_deleted', 'View archived/deleted org units', 'org_unit', 'view_deleted', NOW(), NOW())
ON CONFLICT (code) DO NOTHING;

-- Step 2: Assign permissions to super_admin role
-- ============================================================
-- Note: super_admin should already have these via the CROSS JOIN in seeder,
-- but we add explicitly to be safe
INSERT INTO role_permissions (role_id, permission_id, created_at)
SELECT r.id, p.id, NOW()
FROM roles r
CROSS JOIN permissions p
WHERE r.name = 'super_admin'
  AND p.code IN (
      'employee.soft_delete', 'employee.restore', 'employee.view_deleted',
      'org_unit.soft_delete', 'org_unit.restore', 'org_unit.view_deleted'
  )
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- Step 3: Assign permissions to hr_admin role
-- ============================================================
-- hr_admin gets ONLY soft_delete permissions for employee & org_unit
-- restore and view_deleted are exclusive to super_admin
INSERT INTO role_permissions (role_id, permission_id, created_at)
SELECT r.id, p.id, NOW()
FROM roles r
CROSS JOIN permissions p
WHERE r.name = 'hr_admin'
  AND p.code IN (
      'employee.soft_delete',
      'org_unit.soft_delete'
  )
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- ============================================================
-- Verification Queries
-- ============================================================

-- Check if permissions were added (both employee and org_unit)
SELECT
    id,
    code,
    description,
    resource,
    action
FROM permissions
WHERE code IN (
    'employee.soft_delete', 'employee.restore', 'employee.view_deleted',
    'org_unit.soft_delete', 'org_unit.restore', 'org_unit.view_deleted'
)
ORDER BY resource, action, code;

-- Check super_admin permissions
SELECT
    r.name as role_name,
    p.code as permission_code,
    p.description,
    p.resource
FROM roles r
JOIN role_permissions rp ON r.id = rp.role_id
JOIN permissions p ON rp.permission_id = p.id
WHERE r.name = 'super_admin'
  AND p.code IN (
      'employee.soft_delete', 'employee.restore', 'employee.view_deleted',
      'org_unit.soft_delete', 'org_unit.restore', 'org_unit.view_deleted'
  )
ORDER BY p.resource, p.code;

-- Check hr_admin permissions
SELECT
    r.name as role_name,
    p.code as permission_code,
    p.description,
    p.resource
FROM roles r
JOIN role_permissions rp ON r.id = rp.role_id
JOIN permissions p ON rp.permission_id = p.id
WHERE r.name = 'hr_admin'
  AND p.code IN (
      'employee.soft_delete', 'employee.restore', 'employee.view_deleted',
      'org_unit.soft_delete', 'org_unit.restore', 'org_unit.view_deleted'
  )
ORDER BY p.resource, p.code;

-- Check all employee permissions for hr_admin (should include new soft delete ones)
SELECT
    r.name as role_name,
    p.code as permission_code,
    p.description,
    p.action
FROM roles r
JOIN role_permissions rp ON r.id = rp.role_id
JOIN permissions p ON rp.permission_id = p.id
WHERE r.name = 'hr_admin'
  AND p.resource = 'employee'
ORDER BY p.action, p.code;

-- Check all org_unit permissions for hr_admin (should include new soft delete ones)
SELECT
    r.name as role_name,
    p.code as permission_code,
    p.description,
    p.action
FROM roles r
JOIN role_permissions rp ON r.id = rp.role_id
JOIN permissions p ON rp.permission_id = p.id
WHERE r.name = 'hr_admin'
  AND p.resource = 'org_unit'
ORDER BY p.action, p.code;
