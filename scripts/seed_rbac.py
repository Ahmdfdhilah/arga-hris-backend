"""
RBAC Seeder Script

Seeds default roles and permissions for HRIS.
Run after migration: python scripts/seed_rbac.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.config.database import AsyncSessionLocal
from app.modules.users.rbac.models.role import Role
from app.modules.users.rbac.models.permission import Permission
from app.modules.users.rbac.models.role_permission import RolePermission
from app.modules.users.rbac.models.user_role import UserRole
from app.modules.users.users.models.user import User


# Default roles
ROLES = [
    {"name": "super_admin", "description": "Full system access", "is_system": True},
    {"name": "hr_admin", "description": "HR administrator with full HR access", "is_system": True},
    {"name": "org_unit_head", "description": "Organization unit head - can approve subordinates", "is_system": True},
    {"name": "employee", "description": "Regular employee", "is_system": True},
]

# Default permissions (resource:action format)
PERMISSIONS = [
    # Users
    {"code": "users:read", "description": "View users", "resource": "users", "action": "read"},
    {"code": "users:write", "description": "Create/update users", "resource": "users", "action": "write"},
    {"code": "users:delete", "description": "Delete users", "resource": "users", "action": "delete"},
    
    # Employees
    {"code": "employees:read", "description": "View employees", "resource": "employees", "action": "read"},
    {"code": "employees:write", "description": "Create/update employees", "resource": "employees", "action": "write"},
    {"code": "employees:delete", "description": "Delete employees", "resource": "employees", "action": "delete"},
    
    # Attendance
    {"code": "attendance:read", "description": "View attendance", "resource": "attendance", "action": "read"},
    {"code": "attendance:read_all", "description": "View all attendance", "resource": "attendance", "action": "read_all"},
    {"code": "attendance:write", "description": "Create/update attendance", "resource": "attendance", "action": "write"},
    {"code": "attendance:approve", "description": "Approve attendance", "resource": "attendance", "action": "approve"},
    
    # Leave requests
    {"code": "leave:read", "description": "View own leave requests", "resource": "leave", "action": "read"},
    {"code": "leave:read_all", "description": "View all leave requests", "resource": "leave", "action": "read_all"},
    {"code": "leave:write", "description": "Create/update leave requests", "resource": "leave", "action": "write"},
    {"code": "leave:approve", "description": "Approve leave requests", "resource": "leave", "action": "approve"},
    
    # Work submissions
    {"code": "work:read", "description": "View own work submissions", "resource": "work", "action": "read"},
    {"code": "work:read_all", "description": "View all work submissions", "resource": "work", "action": "read_all"},
    {"code": "work:write", "description": "Create/update work submissions", "resource": "work", "action": "write"},
    {"code": "work:review", "description": "Review work submissions", "resource": "work", "action": "review"},
    
    # Org units
    {"code": "org_units:read", "description": "View organization units", "resource": "org_units", "action": "read"},
    {"code": "org_units:write", "description": "Create/update org units", "resource": "org_units", "action": "write"},
    
    # Dashboard
    {"code": "dashboard:read", "description": "View dashboard", "resource": "dashboard", "action": "read"},
    {"code": "dashboard:read_all", "description": "View full dashboard stats", "resource": "dashboard", "action": "read_all"},
    
    # Roles
    {"code": "roles:read", "description": "View roles", "resource": "roles", "action": "read"},
    {"code": "roles:write", "description": "Create/update roles", "resource": "roles", "action": "write"},
]

# Role-permission mappings
ROLE_PERMISSIONS = {
    "super_admin": ["*"],  # All permissions
    "hr_admin": [
        "users:read", "users:write",
        "employees:read", "employees:write", "employees:delete",
        "attendance:read_all", "attendance:approve",
        "leave:read_all", "leave:approve",
        "work:read_all", "work:review",
        "org_units:read", "org_units:write",
        "dashboard:read_all",
        "roles:read", "roles:write",
    ],
    "org_unit_head": [
        "employees:read",
        "attendance:read", "attendance:read_all", "attendance:approve",
        "leave:read", "leave:read_all", "leave:approve",
        "work:read", "work:read_all", "work:review",
        "org_units:read",
        "dashboard:read",
    ],
    "employee": [
        "attendance:read", "attendance:write",
        "leave:read", "leave:write",
        "work:read", "work:write",
        "dashboard:read",
    ],
}


async def seed_rbac():
    """Seed roles and permissions."""
    async with AsyncSessionLocal() as session:
        print("Seeding RBAC...")
        
        # Create roles
        role_map = {}
        for role_data in ROLES:
            existing = await session.execute(
                select(Role).where(Role.name == role_data["name"])
            )
            role = existing.scalar_one_or_none()
            
            if not role:
                role = Role(**role_data)
                session.add(role)
                await session.flush()
                print(f"  Created role: {role_data['name']}")
            else:
                print(f"  Role exists: {role_data['name']}")
            
            role_map[role_data["name"]] = role

        # Create permissions
        perm_map = {}
        for perm_data in PERMISSIONS:
            existing = await session.execute(
                select(Permission).where(Permission.code == perm_data["code"])
            )
            perm = existing.scalar_one_or_none()
            
            if not perm:
                perm = Permission(**perm_data)
                session.add(perm)
                await session.flush()
                print(f"  Created permission: {perm_data['code']}")
            else:
                print(f"  Permission exists: {perm_data['code']}")
            
            perm_map[perm_data["code"]] = perm

        # Assign permissions to roles
        for role_name, perm_codes in ROLE_PERMISSIONS.items():
            role = role_map.get(role_name)
            if not role:
                continue

            if "*" in perm_codes:
                # All permissions
                perm_codes = [p["code"] for p in PERMISSIONS]

            for perm_code in perm_codes:
                perm = perm_map.get(perm_code)
                if not perm:
                    continue

                # Check if already assigned
                existing = await session.execute(
                    select(RolePermission).where(
                        RolePermission.role_id == role.id,
                        RolePermission.permission_id == perm.id
                    )
                )
                if not existing.scalar_one_or_none():
                    rp = RolePermission(role_id=role.id, permission_id=perm.id)
                    session.add(rp)
                    print(f"  Assigned {perm_code} to {role_name}")

        await session.commit()
        print("RBAC seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_rbac())
