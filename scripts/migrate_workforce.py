#!/usr/bin/env python3
"""
Unified Workforce & Operational Data Migration Script - SQL Output Mode

Generates SQL files for complete HRIS migration including:
- Master data (users, employees, org units) from workforce dump
- Operational data (attendances, leave requests, etc.) from HRIS dump
- Automatic mapping of employee_id → user_id for created_by/updated_by fields

Flow:
1. Read workforce dump (org units, employees)
2. Read HRIS dump (attendances, leave_requests, work_submissions, etc.)
3. Generate master data SQL files with UUID mapping
4. Generate operational data SQL files with employee_id → user_id conversion

Output Structure:
    sql/migration_output/
        # Master Data
        00_sso_application.sql
        01_sso_users.sql
        02_sso_user_applications.sql
        03_hris_users.sql
        04_hris_org_units.sql
        05_hris_employees.sql
        06_hris_supervisor_updates.sql
        07_hris_org_unit_heads.sql
        08_hris_rbac_assignments.sql
        
        # Operational Data (with employee_id → user_id mapping)
        09_hris_attendances.sql
        10_hris_leave_requests.sql
        11_hris_work_submissions.sql
        12_hris_job_executions.sql
        13_hris_guest_accounts.sql

Usage:
    python scripts/migrate_workforce.py
"""

import sys
import uuid
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


WORKFORCE_DUMP = Path(__file__).parent.parent / "sql" / "dump" / "arga_workforce.sql"
HRIS_DUMP = Path(__file__).parent.parent / "sql" / "dump" / "arga_hris.sql"
OUTPUT_DIR = Path(__file__).parent.parent / "sql" / "migration_output"
HRIS_APP_CODE = "hris-arga"

# Operational tables to extract
OPERATIONAL_TABLES = [
    "attendances",
    "leave_requests",
    "work_submissions",
    "job_executions",
    "guest_accounts"
]


def parse_copy_data(content: str, table_name: str) -> List[Dict[str, Any]]:
    """Parse COPY data from SQL dump."""
    # Try with quotes first (workforce dump), then without (HRIS dump)
    pattern1 = rf'COPY public\."{table_name}" \(([^)]+)\) FROM stdin;(.*?)\n\\.'
    pattern2 = rf'COPY public\.{table_name} \(([^)]+)\) FROM stdin;(.*?)\n\\.'
    
    match = re.search(pattern1, content, re.DOTALL)
    if not match:
        match = re.search(pattern2, content, re.DOTALL)
    
    if not match:
        return []

    columns = [col.strip() for col in match.group(1).split(",")]
    data_block = match.group(2).strip()
    data_lines = data_block.split("\n")

    results = []
    for line in data_lines:
        if not line or line.startswith("\\"):
            continue
        values = line.split("\t")
        row = {}
        for i, col in enumerate(columns):
            if i < len(values):
                val = values[i]
                if val == "\\N":
                    val = None
                elif val == "{}":
                    val = {}
                row[col] = val
            else:
                row[col] = None
        results.append(row)

    return results


def load_workforce_data() -> tuple[List[Dict], List[Dict]]:
    """Load employees and org units from workforce dump."""
    if not WORKFORCE_DUMP.exists():
        print(f"Error: Dump file not found at {WORKFORCE_DUMP}")
        sys.exit(1)
        
    content = WORKFORCE_DUMP.read_text()
    employees = parse_copy_data(content, "tblEmployees")
    org_units = parse_copy_data(content, "tblOrganizationUnits")
    return employees, org_units


def load_hris_operational_data() -> Dict[str, List[Dict]]:
    """Load operational data from HRIS dump."""
    if not HRIS_DUMP.exists():
        print(f"Warning: HRIS dump not found at {HRIS_DUMP}, skipping operational data")
        return {}
    
    content = HRIS_DUMP.read_text()
    operational_data = {}
    
    for table in OPERATIONAL_TABLES:
        data = parse_copy_data(content, table)
        operational_data[table] = data
        
    return operational_data


def escape_sql_string(value: Any) -> str:
    """Escape string for SQL output."""
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    # Escape single quotes
    value_str = str(value).replace("'", "''")
    return f"'{value_str}'"


def escape_sql_value(value: str) -> str:
    """Escape value for SQL INSERT (for operational data)."""
    if value == "\\N" or value is None:
        return "NULL"
    
    # Check if it's likely a number
    try:
        if "." in str(value):
            float(value)
        else:
            int(value)
        return str(value)
    except (ValueError, TypeError):
        pass
    
    # Check for boolean
    if value == "t":
        return "true"
    if value == "f":
        return "false"
    
    # Check for UUID pattern
    if re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', str(value)):
        return f"'{value}'::uuid"
    
    # Check for timestamp pattern
    if re.match(r'^\d{4}-\d{2}-\d{2}', str(value)):
        escaped = str(value).replace("'", "''")
        return f"'{escaped}'"
    
    # Default: string
    escaped = str(value).replace("'", "''")
    escaped = escaped.replace("\\", "\\\\")
    return f"'{escaped}'"


def calculate_path(org_unit_id: int, parent_id: Optional[int], parent_paths: Dict[int, str]) -> str:
    """Calculate path for an org unit based on parent's path."""
    if parent_id is None:
        return str(org_unit_id)
    
    parent_path = parent_paths.get(parent_id, str(parent_id))
    return f"{parent_path}.{org_unit_id}"


def generate_sso_application_sql(hris_app_id: str) -> str:
    """Generate SQL for creating HRIS application in SSO."""
    sql = f"""-- Create HRIS Application in SSO
-- File: 00_sso_application.sql

INSERT INTO applications (id, name, code, description, base_url, is_active, created_at, updated_at)
SELECT 
    '{hris_app_id}'::uuid,
    'HRIS Argabumi',
    '{HRIS_APP_CODE}',
    'Human Resource Information System',
    'https://hris.argabumi.id',
    true,
    NOW(),
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM applications WHERE code = '{HRIS_APP_CODE}'
);
"""
    return sql


def generate_sso_users_sql(employees: List[Dict]) -> tuple[str, Dict[str, str], Dict[int, str]]:
    """
    Generate SQL for creating users in SSO. 
    Returns (SQL, email->uuid mapping, employee_id->uuid mapping)
    """
    user_mapping = {}
    employee_id_to_uuid = {}
    sql_lines = [
        "-- Create SSO Users",
        "-- File: 01_sso_users.sql",
        ""
    ]
    
    for emp in employees:
        email = emp.get("employee_email")
        if not email:
            continue
            
        employee_id = int(emp.get("employee_id"))
        name = emp.get("employee_name", "")
        phone = emp.get("employee_phone")
        gender = emp.get("employee_gender")
        
        # Convert empty phone to None to avoid unique constraint on empty string
        if not phone or phone.strip() == "":
            phone = None
        
        user_id = str(uuid.uuid4())
        user_mapping[email] = user_id
        employee_id_to_uuid[employee_id] = user_id  # IMPORTANT: map employee_id → user_id
        
        sql_lines.append(f"""-- User: {name} (employee_id: {employee_id})
INSERT INTO users (id, name, email, phone, gender, status, role, created_at, updated_at)
SELECT 
    '{user_id}'::uuid,
    {escape_sql_string(name)},
    {escape_sql_string(email)},
    {escape_sql_string(phone)},
    {escape_sql_string(gender)},
    'active',
    'user',
    NOW(),
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE email = {escape_sql_string(email)}
);
""")
    
    return "\n".join(sql_lines), user_mapping, employee_id_to_uuid


def generate_sso_user_applications_sql(user_mapping: Dict[str, str], hris_app_id: str) -> str:
    """Generate SQL for assigning users to HRIS application."""
    sql_lines = [
        "-- Assign Users to HRIS Application",
        "-- File: 02_sso_user_applications.sql",
        ""
    ]
    
    for email, user_id in user_mapping.items():
        sql_lines.append(f"""INSERT INTO user_applications (user_id, application_id)
SELECT '{user_id}'::uuid, '{hris_app_id}'::uuid
WHERE NOT EXISTS (
    SELECT 1 FROM user_applications 
    WHERE user_id = '{user_id}'::uuid AND application_id = '{hris_app_id}'::uuid
);
""")
    
    return "\n".join(sql_lines)


def generate_hris_users_sql(employees: List[Dict], user_mapping: Dict[str, str]) -> str:
    """Generate SQL for creating replica users in HRIS."""
    sql_lines = [
        "-- Create HRIS User Replicas",
        "-- File: 03_hris_users.sql",
        ""
    ]
    
    for emp in employees:
        email = emp.get("employee_email")
        if not email or email not in user_mapping:
            continue
            
        user_id = user_mapping[email]
        name = emp.get("employee_name", "")
        phone = emp.get("employee_phone")
        gender = emp.get("employee_gender")
        
        # Convert empty phone to None
        if not phone or phone.strip() == "":
            phone = None
        
        sql_lines.append(f"""INSERT INTO users (id, name, email, phone, gender, is_active, synced_at, created_at, updated_at)
SELECT 
    '{user_id}'::uuid,
    {escape_sql_string(name)},
    {escape_sql_string(email)},
    {escape_sql_string(phone)},
    {escape_sql_string(gender)},
    true,
    NOW(),
    NOW(),
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE id = '{user_id}'::uuid
);
""")
    
    return "\n".join(sql_lines)


def generate_hris_org_units_sql(org_units: List[Dict], admin_id: str) -> tuple[str, Dict[int, int]]:
    """Generate SQL for creating org units in HRIS with preserved IDs."""
    id_mapping = {}
    paths = {}
    sorted_units = sorted(org_units, key=lambda x: int(x.get("org_unit_level", 0)))
    
    sql_lines = [
        "-- Create Organization Units (Preserving Original IDs)",
        "-- File: 04_hris_org_units.sql",
        ""
    ]
    
    for unit in sorted_units:
        original_id = int(unit.get("org_unit_id"))
        code = unit.get("org_unit_code")
        name = unit.get("org_unit_name")
        unit_type = unit.get("org_unit_type")
        parent_id = int(unit.get("org_unit_parent_id")) if unit.get("org_unit_parent_id") else None
        level = int(unit.get("org_unit_level", 1))
        description = unit.get("org_unit_description")
        is_active = unit.get("is_active", "t") == "t"
        
        path = calculate_path(original_id, parent_id, paths)
        paths[original_id] = path
        id_mapping[original_id] = original_id
        
        parent_id_sql = str(parent_id) if parent_id else "NULL"
        
        sql_lines.append(f"""INSERT INTO org_units (id, code, name, type, parent_id, level, path, description, is_active, created_by, created_at, updated_at)
SELECT 
    {original_id},
    {escape_sql_string(code)},
    {escape_sql_string(name)},
    {escape_sql_string(unit_type)},
    {parent_id_sql},
    {level},
    {escape_sql_string(path)},
    {escape_sql_string(description)},
    {is_active},
    '{admin_id}'::uuid,
    NOW(),
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM org_units WHERE code = {escape_sql_string(code)}
);
""")
    
    if id_mapping:
        max_id = max(id_mapping.values())
        sql_lines.append(f"\nSELECT setval('org_units_id_seq', {max_id}, true);")
    
    return "\n".join(sql_lines), id_mapping


def generate_hris_employees_sql(employees: List[Dict], user_mapping: Dict[str, str], org_unit_mapping: Dict[int, int], admin_id: str) -> tuple[str, str, Dict[int, int]]:
    """Generate SQL for creating employees."""
    id_mapping = {}
    supervisor_updates = []
    
    insert_lines = [
        "-- Create Employees (Preserving Original IDs)",
        "-- File: 05_hris_employees.sql",
        ""
    ]
    
    for emp in employees:
        original_id = int(emp.get("employee_id"))
        email = emp.get("employee_email")
        
        if not email or email not in user_mapping:
            continue
            
        sso_user_id = user_mapping[email]
        code = emp.get("employee_number")
        name = emp.get("employee_name")
        position = emp.get("employee_position")
        
        emp_type_raw = str(emp.get("employee_type", "")).lower()
        if "pkwt" in emp_type_raw or "contract" in emp_type_raw:
            emp_type = "contract"
        elif "intern" in emp_type_raw or "magang" in emp_type_raw:
            emp_type = "intern"
        else:
            emp_type = "fulltime"
        
        site_raw = str(emp.get("employee_type", "") or emp.get("employee_location", "")).lower()
        if "ho" in site_raw or "head" in site_raw:
            site = "ho"
        elif "hybrid" in site_raw:
            site = "hybrid"
        else:
            site = "on_site"
        
        org_unit_id = int(emp.get("employee_org_unit_id")) if emp.get("employee_org_unit_id") else None
        supervisor_id = int(emp.get("employee_supervisor_id")) if emp.get("employee_supervisor_id") else None
        is_active = emp.get("is_active", "t") == "t"
        
        org_unit_id_sql = str(org_unit_id) if org_unit_id else "NULL"
        
        insert_lines.append(f"""INSERT INTO employees (id, user_id, name, email, code, position, type, site, org_unit_id, supervisor_id, is_active, created_by, created_at, updated_at)
SELECT 
    {original_id},
    '{sso_user_id}'::uuid,
    {escape_sql_string(name)},
    {escape_sql_string(email)},
    {escape_sql_string(code)},
    {escape_sql_string(position)},
    {escape_sql_string(emp_type)},
    {escape_sql_string(site)},
    {org_unit_id_sql},
    NULL,
    {is_active},
    '{admin_id}'::uuid,
    NOW(),
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM employees WHERE code = {escape_sql_string(code)}
);
""")
        
        id_mapping[original_id] = original_id
        if supervisor_id:
            supervisor_updates.append((original_id, supervisor_id))
    
    if id_mapping:
        max_id = max(id_mapping.values())
        insert_lines.append(f"\nSELECT setval('employees_id_seq', {max_id}, true);")
    
    update_lines = [
        "-- Update Supervisor Relationships",
        "-- File: 06_hris_supervisor_updates.sql",
        ""
    ]
    
    for emp_id, sup_id in supervisor_updates:
        update_lines.append(f"UPDATE employees SET supervisor_id = {sup_id} WHERE id = {emp_id};\n")
    
    return "\n".join(insert_lines), "\n".join(update_lines), id_mapping


def generate_org_unit_heads_sql(org_units: List[Dict], org_unit_mapping: Dict[int, int], employee_mapping: Dict[int, int]) -> str:
    """Generate SQL for updating org unit heads."""
    sql_lines = [
        "-- Update Organization Unit Heads",
        "-- File: 07_hris_org_unit_heads.sql",
        ""
    ]
    
    for unit in org_units:
        old_id = int(unit.get("org_unit_id"))
        old_head_id = unit.get("org_unit_head_id")
        
        if old_head_id and old_id in org_unit_mapping:
            new_unit_id = org_unit_mapping[old_id]
            new_head_id = employee_mapping.get(int(old_head_id))
            
            if new_head_id:
                sql_lines.append(f"UPDATE org_units SET head_id = {new_head_id} WHERE id = {new_unit_id};\n")
    
    return "\n".join(sql_lines)


def generate_rbac_assignments_sql(user_mapping: Dict[str, str]) -> str:
    """Generate SQL for assigning employee role."""
    sql_lines = [
        "-- Assign Employee Role to All Users",
        "-- File: 08_hris_rbac_assignments.sql",
        ""
    ]
    
    for email, user_id in user_mapping.items():
        sql_lines.append(f"""INSERT INTO user_roles (user_id, role_id, created_at)
SELECT 
    '{user_id}'::uuid,
    (SELECT id FROM roles WHERE name = 'employee'),
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM user_roles 
    WHERE user_id = '{user_id}'::uuid 
    AND role_id = (SELECT id FROM roles WHERE name = 'employee')
);
""")
    
    return "\n".join(sql_lines)


def generate_operational_data_sql(
    table_name: str, 
    data: List[Dict], 
    employee_to_user_map: Dict[int, str],
    file_number: int
) -> str:
    """
    Generate SQL for operational tables.
    Maps employee_id → user_id for created_by/updated_by fields.
    """
    if not data:
        return f"-- No data for table: {table_name}\n"
    
    sql_lines = [
        f"-- Insert operational data for table: {table_name}",
        f"-- File: {file_number:02d}_hris_{table_name}.sql",
        f"-- Total rows: {len(data)}",
        f"-- Note: created_by/updated_by mapped from employee_id to user_id (UUID)",
        ""
    ]
    
    # Get columns from first row
    columns = list(data[0].keys())
    col_list = ", ".join(columns)
    
    # Fields that need employee_id → user_id mapping
    fields_to_map = ["created_by", "updated_by"]
    
    # Generate INSERT statements (batch 100 rows)
    batch_size = 100
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        
        sql_lines.append(f"INSERT INTO {table_name} ({col_list}) VALUES")
        
        value_lines = []
        for row in batch:
            values = []
            for col in columns:
                value = row.get(col)
                
                # Map employee_id → user_id for created_by/updated_by
                if col in fields_to_map and value is not None:
                    try:
                        emp_id = int(value)
                        if emp_id in employee_to_user_map:
                            # Convert to UUID
                            user_uuid = employee_to_user_map[emp_id]
                            values.append(f"'{user_uuid}'::uuid")
                        else:
                            # Employee not found in mapping, set NULL
                            values.append("NULL")
                    except (ValueError, TypeError):
                        values.append(escape_sql_value(value))
                else:
                    values.append(escape_sql_value(value))
            
            value_lines.append("    (" + ", ".join(values) + ")")
        
        sql_lines.append(",\n".join(value_lines) + ";")
        sql_lines.append("")
    
    return "\n".join(sql_lines)


def main():
    print("=== HRIS Complete Migration - SQL Generation Mode ===\n")
    
    # Load workforce data
    employees, org_units = load_workforce_data()
    print(f"Loaded {len(employees)} employees, {len(org_units)} org units from workforce dump")
    
    # Load operational data
    operational_data = load_hris_operational_data()
    total_operational = sum(len(v) for v in operational_data.values())
    print(f"Loaded {total_operational} operational records from HRIS dump\n")
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR}\n")
    
    # Generate UUIDs
    hris_app_id = str(uuid.uuid4())
    
    print("Generating SQL files...")
    print("\n=== MASTER DATA ===")
    
    # 1. SSO Application
    print("  00. SSO Application")
    sql = generate_sso_application_sql(hris_app_id)
    (OUTPUT_DIR / "00_sso_application.sql").write_text(sql)
    
    # 2. SSO Users (with employee_id → user_id mapping!)
    print("  01. SSO Users")
    sql, user_mapping, employee_to_user_map = generate_sso_users_sql(employees)
    (OUTPUT_DIR / "01_sso_users.sql").write_text(sql)
    
    admin_id = list(user_mapping.values())[0] if user_mapping else str(uuid.uuid4())
    
    # 3. SSO User Applications
    print("  02. SSO User Applications")
    sql = generate_sso_user_applications_sql(user_mapping, hris_app_id)
    (OUTPUT_DIR / "02_sso_user_applications.sql").write_text(sql)
    
    # 4. HRIS Users
    print("  03. HRIS Users")
    sql = generate_hris_users_sql(employees, user_mapping)
    (OUTPUT_DIR / "03_hris_users.sql").write_text(sql)
    
    # 5. HRIS Org Units
    print("  04. HRIS Org Units")
    sql, org_unit_mapping = generate_hris_org_units_sql(org_units, admin_id)
    (OUTPUT_DIR / "04_hris_org_units.sql").write_text(sql)
    
    # 6. HRIS Employees
    print("  05. HRIS Employees")
    print("  06. Supervisor Updates")
    insert_sql, update_sql, employee_mapping = generate_hris_employees_sql(
        employees, user_mapping, org_unit_mapping, admin_id
    )
    (OUTPUT_DIR / "05_hris_employees.sql").write_text(insert_sql)
    (OUTPUT_DIR / "06_hris_supervisor_updates.sql").write_text(update_sql)
    
    # 7. Org Unit Heads
    print("  07. Org Unit Heads")
    sql = generate_org_unit_heads_sql(org_units, org_unit_mapping, employee_mapping)
    (OUTPUT_DIR / "07_hris_org_unit_heads.sql").write_text(sql)
    
    # 8. RBAC Assignments
    print("  08. RBAC Assignments")
    sql = generate_rbac_assignments_sql(user_mapping)
    (OUTPUT_DIR / "08_hris_rbac_assignments.sql").write_text(sql)
    
    # 9-13. Operational Data (with employee_id → user_id mapping!)
    print("\n=== OPERATIONAL DATA ===")
    file_num = 9
    for table in OPERATIONAL_TABLES:
        data = operational_data.get(table, [])
        if data:
            print(f"  {file_num:02d}. {table.title()} ({len(data)} rows)")
            sql = generate_operational_data_sql(table, data, employee_to_user_map, file_num)
            (OUTPUT_DIR / f"{file_num:02d}_hris_{table}.sql").write_text(sql)
        else:
            print(f"  {file_num:02d}. {table.title()} (no data)")
        file_num += 1
    
    print("\n=== SQL Generation Complete! ===")
    print(f"   - SSO Users: {len(user_mapping)}")
    print(f"   - Org Units: {len(org_unit_mapping)} (IDs preserved)")
    print(f"   - Employees: {len(employee_mapping)} (IDs preserved)")
    print(f"   - Employee→User mapping: {len(employee_to_user_map)} entries")
    print(f"   - Operational records: {total_operational}")
    print(f"\nAll SQL files generated in: {OUTPUT_DIR}")
    print("\nExecute files in order (00-13):")
    print("  1. Files 00-02: Execute on SSO database")
    print("  2. Files 03-13: Execute on HRIS database")
    print("\nNote: created_by/updated_by fields in operational data")
    print("      have been mapped from employee_id (INT) to user_id (UUID)")


if __name__ == "__main__":
    main()