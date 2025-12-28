#!/usr/bin/env python3
"""
Workforce Data Migration Script

Migrates data from old workforce database to new SSO + HRIS architecture.

Flow:
1. Read org units from workforce dump
2. Read employees from workforce dump
3. Create users in SSO (with UUID)
4. Assign HRIS application access
5. Create replica users in HRIS
6. Create org units in HRIS (PRESERVE original IDs)
7. Recalculate org unit paths using preserved IDs
8. Create employees in HRIS (PRESERVE original IDs, linked to users and org units)
9. Update org unit heads (after employees are created)

Usage:
    python scripts/migrate_workforce.py

Environment Variables Required:
    - SSO database connection (uses settings)
    - HRIS database connection (uses settings)
"""

import sys
import uuid
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session


WORKFORCE_DUMP = Path(__file__).parent.parent / "sql" / "dump" / "arga_workforce.sql"
SSO_DATABASE_URL = "postgresql://postgres:tanyafadil@localhost:5432/arga_sso_v2"
HRIS_DATABASE_URL = "postgresql://postgres:tanyafadil@localhost:5432/hris_2"
HRIS_APP_CODE = "hris-arga"
ADMIN_USER_ID = None


def parse_copy_data(content: str, table_name: str) -> List[Dict[str, Any]]:
    """Parse COPY data from SQL dump."""
    pattern = rf'COPY public\."{table_name}" \(([^)]+)\) FROM stdin;(.*?)\n\\.'
    match = re.search(pattern, content, re.DOTALL)

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
    content = WORKFORCE_DUMP.read_text()
    employees = parse_copy_data(content, "tblEmployees")
    org_units = parse_copy_data(content, "tblOrganizationUnits")
    return employees, org_units


def get_or_create_hris_app(session: Session) -> str:
    """Get or create HRIS application in SSO. Returns app_id as string."""
    result = session.execute(
        text("SELECT id FROM applications WHERE code = :code"), {"code": HRIS_APP_CODE}
    ).fetchone()

    if result:
        return str(result[0])

    app_id = str(uuid.uuid4())
    session.execute(
        text("""
            INSERT INTO applications (id, name, code, description, base_url, is_active, created_at, updated_at)
            VALUES (:id, :name, :code, :description, :base_url, true, NOW(), NOW())
        """),
        {
            "id": app_id,
            "name": "HRIS Argabumi",
            "code": HRIS_APP_CODE,
            "description": "Human Resource Information System",
            "base_url": "https://hris.argabumi.id",
        },
    )
    session.commit()
    return app_id


def create_sso_user(session: Session, employee: Dict, hris_app_id: str) -> str:
    """Create user in SSO and return UUID."""
    email = employee.get("employee_email")
    name = employee.get("employee_name", "")
    phone = employee.get("employee_phone")
    gender = employee.get("employee_gender")

    if not email:
        return None

    result = session.execute(
        text("SELECT id FROM users WHERE email = :email"), {"email": email}
    ).fetchone()

    if result:
        user_id = str(result[0])
    else:
        user_id = str(uuid.uuid4())

        if phone:
            phone_exists = session.execute(
                text("SELECT 1 FROM users WHERE phone = :phone"), {"phone": phone}
            ).fetchone()
            if phone_exists:
                phone = None

        session.execute(
            text("""
                INSERT INTO users (id, name, email, phone, gender, status, role, created_at, updated_at)
                VALUES (:id, :name, :email, :phone, :gender, 'active', 'user', NOW(), NOW())
            """),
            {
                "id": user_id,
                "name": name,
                "email": email,
                "phone": phone,
                "gender": gender,
            },
        )

    existing = session.execute(
        text(
            "SELECT 1 FROM user_applications WHERE user_id = :user_id AND application_id = :app_id"
        ),
        {"user_id": user_id, "app_id": hris_app_id},
    ).fetchone()

    if not existing:
        session.execute(
            text(
                "INSERT INTO user_applications (user_id, application_id) VALUES (:user_id, :app_id)"
            ),
            {"user_id": user_id, "app_id": hris_app_id},
        )

    return user_id


def create_hris_user(session: Session, sso_user_id: str, employee: Dict) -> str:
    """Create replica user in HRIS."""
    email = employee.get("employee_email")
    name = employee.get("employee_name", "")
    phone = employee.get("employee_phone")
    gender = employee.get("employee_gender")

    result = session.execute(
        text("SELECT id FROM users WHERE id = :id"), {"id": sso_user_id}
    ).fetchone()

    if result:
        return sso_user_id

    session.execute(
        text("""
            INSERT INTO users (id, name, email, phone, gender, is_active, synced_at, created_at, updated_at)
            VALUES (:id, :name, :email, :phone, :gender, true, NOW(), NOW(), NOW())
        """),
        {
            "id": sso_user_id,
            "name": name,
            "email": email,
            "phone": phone,
            "gender": gender,
        },
    )

    return sso_user_id


def calculate_path(org_unit_id: int, parent_id: Optional[int], parent_paths: Dict[int, str]) -> str:
    """Calculate path for an org unit based on parent's path."""
    if parent_id is None:
        return str(org_unit_id)
    
    parent_path = parent_paths.get(parent_id, str(parent_id))
    return f"{parent_path}.{org_unit_id}"


def create_hris_org_units(
    session: Session, org_units: List[Dict], admin_id: str
) -> Dict[int, int]:
    """
    Create org units in HRIS with PRESERVED original IDs.
    Returns mapping of old_id -> new_id (same in this case).
    """
    id_mapping = {}
    paths = {}  # Store calculated paths
    
    # Sort by level to ensure parents are created first
    sorted_units = sorted(org_units, key=lambda x: int(x.get("org_unit_level", 0)))

    # First pass: Create all org units with preserved IDs
    for unit in sorted_units:
        original_id = int(unit.get("org_unit_id"))
        code = unit.get("org_unit_code")
        name = unit.get("org_unit_name")
        unit_type = unit.get("org_unit_type")
        parent_id = int(unit.get("org_unit_parent_id")) if unit.get("org_unit_parent_id") else None
        level = int(unit.get("org_unit_level", 1))
        description = unit.get("org_unit_description")
        is_active = unit.get("is_active", "t") == "t"

        # Calculate proper path using the ORIGINAL ID (which we preserve)
        path = calculate_path(original_id, parent_id, paths)
        paths[original_id] = path

        result = session.execute(
            text("SELECT id FROM org_units WHERE code = :code"), {"code": code}
        ).fetchone()

        if result:
            id_mapping[original_id] = result[0]
            # Update path if already exists
            session.execute(
                text("UPDATE org_units SET path = :path WHERE id = :id"),
                {"path": path, "id": result[0]}
            )
            continue

        # Insert with explicit ID to preserve original
        session.execute(
            text("""
                INSERT INTO org_units (id, code, name, type, parent_id, level, path, description, is_active, created_by, created_at, updated_at)
                VALUES (:id, :code, :name, :type, :parent_id, :level, :path, :description, :is_active, :created_by, NOW(), NOW())
            """),
            {
                "id": original_id,  # PRESERVE original ID
                "code": code,
                "name": name,
                "type": unit_type,
                "parent_id": parent_id,  # Use original parent_id directly
                "level": level,
                "path": path,  # Use calculated path
                "description": description,
                "is_active": is_active,
                "created_by": admin_id,
            },
        )

        id_mapping[original_id] = original_id

    # Reset sequence to max ID + 1 to avoid conflicts for future inserts
    max_id = max(id_mapping.values()) if id_mapping else 0
    session.execute(
        text(f"SELECT setval('org_units_id_seq', :max_id, true)"),
        {"max_id": max_id}
    )

    return id_mapping


def create_hris_employees(
    session: Session,
    employees: List[Dict],
    user_id_mapping: Dict[str, str],  # email -> sso_user_id
    org_unit_mapping: Dict[int, int],
    admin_id: str,
) -> Dict[int, int]:
    """
    Create employees in HRIS with PRESERVED original IDs.
    Uses two-pass approach to handle supervisor FK constraint.
    Returns mapping of old_id -> new_id (same in this case).
    """
    id_mapping = {}
    supervisor_updates = []  # Store (employee_id, supervisor_id) for second pass

    # PASS 1: Insert employees WITHOUT supervisor_id
    for emp in employees:
        original_id = int(emp.get("employee_id"))
        email = emp.get("employee_email")

        if not email:
            continue

        sso_user_id = user_id_mapping.get(email)
        if not sso_user_id:
            continue

        code = emp.get("employee_number")
        name = emp.get("employee_name")
        position = emp.get("employee_position")
        
        # Type Mapping
        emp_type_raw = str(emp.get("employee_type", "")).lower()
        if "pkwt" in emp_type_raw or "contract" in emp_type_raw:
            emp_type = "contract"
        elif "intern" in emp_type_raw or "magang" in emp_type_raw:
            emp_type = "intern"
        else:
            emp_type = "fulltime"

        # Site Mapping
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

        result = session.execute(
            text("SELECT id FROM employees WHERE code = :code"), {"code": code}
        ).fetchone()

        if result:
            id_mapping[original_id] = result[0]
        else:
            # Insert with explicit ID, WITHOUT supervisor_id
            session.execute(
                text("""
                    INSERT INTO employees (id, user_id, name, email, code, position, type, site, org_unit_id, supervisor_id, is_active, created_by, created_at, updated_at)
                    VALUES (:id, :user_id, :name, :email, :code, :position, :type, :site, :org_unit_id, NULL, :is_active, :created_by, NOW(), NOW())
                """),
                {
                    "id": original_id,  # PRESERVE original ID
                    "user_id": sso_user_id,
                    "name": name,
                    "email": email,
                    "code": code,
                    "position": position,
                    "type": emp_type,
                    "site": site,
                    "org_unit_id": org_unit_id,
                    "is_active": is_active,
                    "created_by": admin_id,
                },
            )
            id_mapping[original_id] = original_id

        # Store supervisor update for second pass
        if supervisor_id:
            supervisor_updates.append((original_id, supervisor_id))

    # Reset sequence to max ID + 1
    max_id = max(id_mapping.values()) if id_mapping else 0
    session.execute(
        text(f"SELECT setval('employees_id_seq', :max_id, true)"),
        {"max_id": max_id}
    )

    print(f"   - Employees created with preserved IDs: {len(id_mapping)}")

    # PASS 2: Update supervisor_id now that all employees exist
    print(f"   - Updating {len(supervisor_updates)} supervisor relationships...")
    for emp_id, sup_id in supervisor_updates:
        session.execute(
            text("UPDATE employees SET supervisor_id = :sup_id WHERE id = :emp_id"),
            {"sup_id": sup_id, "emp_id": emp_id}
        )

    return id_mapping


def update_org_unit_heads(
    session: Session,
    org_units: List[Dict],
    org_unit_mapping: Dict[int, int],
    employee_mapping: Dict[int, int],
):
    """Update org unit heads after employees are created."""
    for unit in org_units:
        old_id = int(unit.get("org_unit_id"))
        old_head_id = unit.get("org_unit_head_id")

        if old_head_id:
            new_unit_id = org_unit_mapping.get(old_id)
            new_head_id = employee_mapping.get(int(old_head_id))

            if new_unit_id and new_head_id:
                session.execute(
                    text("UPDATE org_units SET head_id = :head_id WHERE id = :id"),
                    {"head_id": new_head_id, "id": new_unit_id},
                )


def assign_rbac_roles(session: Session, user_id_mapping: Dict[str, str]):
    """Assign 'employee' role to all migrated users."""
    result = session.execute(
        text("SELECT id FROM roles WHERE name = :name"), {"name": "employee"}
    ).fetchone()

    if not result:
        return 0

    employee_role_id = result[0]
    assigned_count = 0

    for email, user_id in user_id_mapping.items():
        existing = session.execute(
            text(
                "SELECT 1 FROM user_roles WHERE user_id = :user_id AND role_id = :role_id"
            ),
            {"user_id": user_id, "role_id": employee_role_id},
        ).fetchone()

        if not existing:
            session.execute(
                text("""
                    INSERT INTO user_roles (user_id, role_id, created_at)
                    VALUES (:user_id, :role_id, NOW())
                """),
                {"user_id": user_id, "role_id": employee_role_id},
            )
            assigned_count += 1

    return assigned_count


def main():
    print("Workforce Data Migration (PRESERVING ORIGINAL IDs)\n")

    employees, org_units = load_workforce_data()

    if not employees and not org_units:
        print("ERROR: No data found")
        return

    print(f"Loaded {len(employees)} employees, {len(org_units)} org units\n")

    sso_engine = create_engine(SSO_DATABASE_URL)
    hris_engine = create_engine(HRIS_DATABASE_URL)
    user_id_mapping = {}

    print("Creating SSO users...")
    with Session(sso_engine) as sso_session:
        hris_app_id = get_or_create_hris_app(sso_session)

        for emp in employees:
            email = emp.get("employee_email")
            if email:
                sso_user_id = create_sso_user(sso_session, emp, hris_app_id)
                if sso_user_id:
                    user_id_mapping[email] = sso_user_id

        sso_session.commit()

    if not user_id_mapping:
        print("ERROR: No users created")
        return

    global ADMIN_USER_ID
    ADMIN_USER_ID = list(user_id_mapping.values())[0]

    print(f"Created {len(user_id_mapping)} SSO users\n")

    print("Creating HRIS data (preserving original IDs)...")
    with Session(hris_engine) as hris_session:
        for emp in employees:
            email = emp.get("employee_email")
            if email and email in user_id_mapping:
                create_hris_user(hris_session, user_id_mapping[email], emp)
        hris_session.commit()

        org_unit_mapping = create_hris_org_units(hris_session, org_units, ADMIN_USER_ID)
        hris_session.commit()
        print(f"   - Org Units created with preserved IDs: {len(org_unit_mapping)}")

        employee_mapping = create_hris_employees(
            hris_session, employees, user_id_mapping, org_unit_mapping, ADMIN_USER_ID
        )
        hris_session.commit()
        print(f"   - Employees created with preserved IDs: {len(employee_mapping)}")

        update_org_unit_heads(
            hris_session, org_units, org_unit_mapping, employee_mapping
        )
        hris_session.commit()

        roles_assigned = assign_rbac_roles(hris_session, user_id_mapping)
        hris_session.commit()

    print(f"\nMigration Complete!")
    print(f"   - SSO Users: {len(user_id_mapping)}")
    print(f"   - Org Units: {len(org_unit_mapping)} (IDs preserved)")
    print(f"   - Employees: {len(employee_mapping)} (IDs preserved)")
    print(f"   - RBAC Roles: {roles_assigned}")
    print(f"\nNote: org_unit_path now correctly uses the preserved org_unit_id values")


if __name__ == "__main__":
    main()