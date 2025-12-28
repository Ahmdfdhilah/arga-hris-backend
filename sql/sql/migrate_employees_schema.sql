-- ============================================
-- Manual Migration: employees table schema update
-- ============================================
-- Run this on existing databases that already have the old schema
-- This renames columns and adds new ones to match the updated model
-- ============================================

-- 1. Drop old constraints and indexes
DROP INDEX IF EXISTS ix_employees_number;
DROP INDEX IF EXISTS ix_employees_number_search;
ALTER TABLE employees DROP CONSTRAINT IF EXISTS ck_employees_type;

-- 2. Rename columns: number -> code, type -> site
ALTER TABLE employees RENAME COLUMN "number" TO code;
ALTER TABLE employees RENAME COLUMN "type" TO site;

-- 3. Add new columns
ALTER TABLE employees ADD COLUMN IF NOT EXISTS name VARCHAR(200);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS email VARCHAR(255);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS type VARCHAR(20);

-- 4. Populate denormalized name/email from users table
UPDATE employees e
SET 
    name = u.name,
    email = u.email
FROM users u
WHERE e.user_id = u.id;

-- 5. Add new constraints
ALTER TABLE employees ADD CONSTRAINT ck_employees_site 
    CHECK (site IN ('on_site', 'hybrid', 'ho') OR site IS NULL);

ALTER TABLE employees ADD CONSTRAINT ck_employees_type 
    CHECK (type IN ('fulltime', 'contract', 'intern') OR type IS NULL);

-- 6. Create new indexes
CREATE UNIQUE INDEX IF NOT EXISTS ix_employees_code ON employees(code);
CREATE INDEX IF NOT EXISTS ix_employees_code_search ON employees USING btree(code);
CREATE INDEX IF NOT EXISTS ix_employees_name ON employees(name);
CREATE INDEX IF NOT EXISTS ix_employees_name_search ON employees USING btree(name);
CREATE INDEX IF NOT EXISTS ix_employees_email ON employees(email);
CREATE INDEX IF NOT EXISTS ix_employees_email_search ON employees USING btree(email);

-- ============================================
-- Verification query (run after migration)
-- ============================================
-- SELECT id, user_id, code, name, email, site, type, position FROM employees LIMIT 10;
