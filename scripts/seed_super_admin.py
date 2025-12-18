#!/usr/bin/env python3
"""
Script untuk membuat super admin user pertama kali saat deployment.

Usage:
    python scripts/seed_super_admin.py

Environment Variables Required:
    - SUPER_ADMIN_EMAIL: Email super admin
    - SUPER_ADMIN_SSO_ID: SSO ID dari SSO server
    - SUPER_ADMIN_FIRST_NAME: First name super admin
    - SUPER_ADMIN_LAST_NAME: Last name super admin
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.modules.users.users.models.user import User
from app.modules.users.rbac.models.role import Role
from app.modules.users.rbac.models.user_role import UserRole
from app.modules.employees.models.employee import Employee  # noqa: F401
from app.modules.org_units.models.org_unit import OrgUnit  # noqa: F401


def create_super_admin():
    """
    Membuat super admin user berdasarkan environment variables.
    """
    # Get super admin info from settings
    email = settings.SUPER_ADMIN_EMAIL
    sso_id = settings.SUPER_ADMIN_SSO_ID
    first_name = settings.SUPER_ADMIN_FIRST_NAME or "Super"
    last_name = settings.SUPER_ADMIN_LAST_NAME or "Admin"

    # Validate required fields
    if not email:
        print(" Error: SUPER_ADMIN_EMAIL environment variable tidak ditemukan")
        print("   Silakan set SUPER_ADMIN_EMAIL di file .env")
        return False

    if not sso_id:
        print(" Error: SUPER_ADMIN_SSO_ID environment variable tidak ditemukan")
        print("   Silakan set SUPER_ADMIN_SSO_ID di file .env")
        return False

    # Validasi sso_id simple (cek panjang string atau format uuid kalau perlu)
    if len(str(sso_id)) < 30:
        print(
            f" Warning: SUPER_ADMIN_SSO_ID terlihat pendek ({sso_id}), pastikan ini UUID yang valid."
        )

    # Create database engine and session (use sync database URL)
    database_url = settings.sync_database_url
    engine = create_engine(database_url)

    with Session(engine) as session:
        try:
            # Check if super admin already exists
            existing_user = session.query(User).filter(User.id == str(sso_id)).first()

            if existing_user:
                print(f"⚠️  Super admin sudah ada:")
                print(f"   - ID: {existing_user.id}")

                # Check if user has super_admin role
                super_admin_role = (
                    session.query(Role).filter(Role.name == "super_admin").first()
                )
                if not super_admin_role:
                    print(" Error: Role 'super_admin' tidak ditemukan di database")
                    print("   Pastikan migration RBAC sudah dijalankan")
                    return False

                has_super_admin_role = (
                    session.query(UserRole)
                    .filter(
                        UserRole.user_id == existing_user.id,
                        UserRole.role_id == super_admin_role.id,
                    )
                    .first()
                )

                if has_super_admin_role:
                    print(" User sudah memiliki role super_admin")
                    return True
                else:
                    # Add super_admin role to existing user
                    print("📝 Menambahkan role super_admin ke user yang ada...")
                    user_role = UserRole(
                        user_id=existing_user.id, role_id=super_admin_role.id
                    )
                    session.add(user_role)
                    session.commit()
                    print(" Role super_admin berhasil ditambahkan!")
                    return True

            # Get super_admin role
            super_admin_role = (
                session.query(Role).filter(Role.name == "super_admin").first()
            )
            if not super_admin_role:
                print(" Error: Role 'super_admin' tidak ditemukan di database")
                print(
                    "   Pastikan migration RBAC sudah dijalankan (alembic upgrade head)"
                )
                return False

            # Create new super admin user
            print(f"📝 Membuat super admin user baru...")
            print(f"   - Email: {email}")
            print(f"   - SSO ID: {sso_id}")
            print(f"   - Name: {first_name} {last_name}")

            new_user = User(
                id=str(sso_id),  # SSO UUID as primary key
                name=f"{first_name} {last_name}",
                is_active=True,
            )
            session.add(new_user)
            session.flush()  # Get the user ID

            # Assign super_admin role
            user_role = UserRole(user_id=new_user.id, role_id=super_admin_role.id)
            session.add(user_role)

            session.commit()

            print(f"\n Super admin berhasil dibuat!")
            print(f"   - User ID: {new_user.id}")
            print(f"   - Role: super_admin")
            print(
                f"\n💡 User ini sudah bisa login menggunakan SSO dengan email: {email}"
            )

            return True

        except Exception as e:
            session.rollback()
            print(f"\n Error saat membuat super admin: {str(e)}")
            import traceback

            traceback.print_exc()
            return False


def main():
    print("=" * 60)
    print("🚀 HRIS - Super Admin Initial Setup")
    print("=" * 60)
    print()

    success = create_super_admin()

    print()
    print("=" * 60)

    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
