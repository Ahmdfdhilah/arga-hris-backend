# Initial Deployment - Super Admin Setup

Dokumentasi ini menjelaskan cara setup super admin pertama kali saat deployment HRIS service ke server.

## Prerequisites

1. Database sudah di-setup dan running
2. SSO service sudah di-deploy dan akun Anda sudah terdaftar di SSO server
3. Anda sudah tahu **SSO ID** dan **email** akun Anda di SSO server

## Cara Mendapatkan SSO ID dan Email

Anda bisa mendapatkan SSO ID dan email Anda dengan:

### 1. Via SSO Service API
```bash
# Login ke SSO service
curl -X POST https://sso.yourdomain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "password": "your-password"
  }'

# Response akan berisi:
{
  "user": {
    "id": 123,          # <- Ini SSO ID Anda
    "email": "your-email@example.com"
  }
}
```

### 2. Via Database SSO Service
```sql
-- Connect ke database SSO service
SELECT id, email FROM users WHERE email = 'your-email@example.com';
```

## Steps untuk Initial Deployment

### 1. Configure Environment Variables

Edit file `.env` di root HRIS service dan set super admin credentials Anda:

```bash
# Super Admin Initial Setup (for deployment)
SUPER_ADMIN_EMAIL=your-email@example.com
SUPER_ADMIN_SSO_ID=123
SUPER_ADMIN_FIRST_NAME=Your
SUPER_ADMIN_LAST_NAME=Name
```

**PENTING:**
- `SUPER_ADMIN_EMAIL` harus **sama persis** dengan email yang terdaftar di SSO server
- `SUPER_ADMIN_SSO_ID` harus **sama persis** dengan user ID di SSO server
- Ini akan memastikan saat Anda login via SSO, sistem akan recognize Anda sebagai super admin

### 2. Run Database Migration

Jalankan migration untuk membuat tables dan seed roles/permissions:

```bash
cd /path/to/arga-hris-service
source venv/bin/activate  # atau venv\Scripts\activate di Windows

# Run migration
alembic upgrade head
```

Migration akan otomatis membuat:
- Tables: users, roles, permissions, user_roles, role_permissions
- Roles: super_admin, hr_admin, org_unit_head, employee, guest
- Permissions: semua permissions untuk setiap module
- Role-Permission mapping

### 3. Create Super Admin User

Jalankan script untuk membuat super admin user:

```bash
# Pastikan masih di virtual environment
python scripts/seed_super_admin.py
```

Script akan:
1. Membaca environment variables (`SUPER_ADMIN_EMAIL`, `SUPER_ADMIN_SSO_ID`, dll)
2. Check apakah user sudah ada
3. Jika belum ada, create user baru dengan role super_admin
4. Jika sudah ada tapi belum punya role super_admin, assign role super_admin

### 4. Verify Super Admin

Cek bahwa super admin sudah dibuat dengan benar:

```bash
# Via database
psql -U hris_user -d hris_db

# Query untuk check super admin
SELECT u.id, u.email, u.sso_id, u.first_name, u.last_name, r.name as role
FROM users u
JOIN user_roles ur ON u.id = ur.user_id
JOIN roles r ON ur.role_id = r.id
WHERE r.name = 'super_admin';
```

Expected output:
```
 id |        email          | sso_id | first_name | last_name |    role
----+-----------------------+--------+------------+-----------+-------------
  1 | your-email@example.com|   123  | Your       | Name      | super_admin
```

### 5. Test Login

Test login via SSO dengan akun super admin Anda:

```bash
# Request ke HRIS service dengan JWT token dari SSO
curl -X GET https://hris.yourdomain.com/api/v1/users/me \
  -H "Authorization: Bearer YOUR_SSO_JWT_TOKEN"
```

Response:
```json
{
  "id": 1,
  "email": "your-email@example.com",
  "sso_id": 123,
  "first_name": "Your",
  "last_name": "Name",
  "account_type": "regular",
  "is_active": true,
  "roles": ["super_admin"]
}
```

## Troubleshooting

### Error: SUPER_ADMIN_EMAIL environment variable tidak ditemukan

**Solution:**
- Pastikan file `.env` sudah ada dan berisi `SUPER_ADMIN_EMAIL`
- Restart terminal/shell Anda setelah edit `.env`

### Error: Role 'super_admin' tidak ditemukan di database

**Solution:**
- Jalankan migration: `alembic upgrade head`
- Migration akan otomatis seed roles

### Super admin sudah dibuat tapi tidak bisa login

**Solution:**
- Pastikan `SUPER_ADMIN_EMAIL` dan `SUPER_ADMIN_SSO_ID` **sama persis** dengan data di SSO server
- Check case sensitivity pada email
- Verify SSO ID adalah integer, bukan string

### Ingin menambah super admin lain

**Solution:**
1. Edit `.env`, ubah email dan SSO ID ke user lain
2. Jalankan `python scripts/seed_super_admin.py` lagi
3. Atau tambah manual via database:

```sql
-- Get user ID dari user yang ingin dijadikan super admin
SELECT id FROM users WHERE email = 'another-admin@example.com';

-- Get role ID super_admin
SELECT id FROM roles WHERE name = 'super_admin';

-- Assign role
INSERT INTO user_roles (user_id, role_id, created_at)
VALUES (2, 1, NOW());  -- user_id=2, role_id=1 (super_admin)
```

## Security Notes

1. **Jangan commit `.env` ke git** - File `.env` berisi credentials sensitive
2. **Gunakan email & SSO ID yang benar** - Pastikan hanya orang yang authorized yang dijadikan super admin
3. **Backup database** - Sebelum run migration di production, backup database terlebih dahulu
4. **Limit super admin** - Hanya buat super admin seperlunya (1-2 orang cukup)
5. **Use strong passwords** - Meskipun HRIS tidak store password (SSO yang handle), pastikan password SSO strong

## Next Steps

Setelah super admin berhasil dibuat:

1. Login ke frontend HRIS menggunakan SSO
2. Tambahkan user lain (HR Admin, employees, dll) via UI atau API
3. Assign roles yang sesuai ke user-user tersebut
4. Configure org units, employees, attendance settings, dll

## Quick Reference

```bash
# Environment Variables
SUPER_ADMIN_EMAIL=your-email@example.com
SUPER_ADMIN_SSO_ID=123
SUPER_ADMIN_FIRST_NAME=Your
SUPER_ADMIN_LAST_NAME=Name

# Commands
alembic upgrade head                    # Run migration
python scripts/seed_super_admin.py      # Create super admin
alembic downgrade -1                    # Rollback migration (if needed)

# Verify
psql -U hris_user -d hris_db -c "SELECT u.email, r.name FROM users u JOIN user_roles ur ON u.id=ur.user_id JOIN roles r ON ur.role_id=r.id WHERE r.name='super_admin';"
```
