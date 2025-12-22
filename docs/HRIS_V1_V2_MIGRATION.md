# HRIS v1 vs v2 Migration & Comparison Guide

> **Tujuan**: Dokumentasi perbedaan endpoints dan schemas antara HRIS v1 (`arga_web/arga_web_backend/arga-hris-service`) dan HRIS v2 (`arga-backend/arga-hris-backend`) untuk keperluan implementasi frontend.

---

## Overview

| Aspek | v1 (Legacy) | v2 (New) |
|-------|-------------|----------|
| **Base URL** | `/api/v1` | `/api/v1` |
| **Auth Service** | SSO External | SSO External (same) |
| **Architecture** | Monolith + gRPC | Microservice + RabbitMQ Events |

---

## Module Comparison Summary

| Module | v1 | v2 | Status |
|--------|----|----|--------|
| Auth | ✅ | ✅ | **CHANGED** - Simplified |
| Employees | ✅ | ✅ | **CHANGED** - Enhanced |
| Attendances | ✅ | ✅ | **SAME** |
| Leave Requests | ✅ | ✅ | **CHANGED** - Added replacement |
| Org Units | ✅ | ✅ | **CHANGED** - Enhanced |
| RBAC/Roles | ✅ | ✅ | **CHANGED** - Simplified |
| Scheduled Jobs | ✅ | ✅ | **SAME** |
| Dashboard | ✅ | ✅ | **SAME** |
| Work Submissions | ✅ | ❌ | **REMOVED** |
| Employee Assignments | ❌ | ✅ | **NEW** |

---

## 1. AUTH MODULE

### v1 Endpoints
| Method | Endpoint | Status |
|--------|----------|--------|
| POST | `/auth/logout` | ❌ Removed |
| POST | `/auth/logout-all` | ❌ Removed |
| POST | `/auth/validate-token` | ❌ Removed |
| GET | `/auth/token-info` | ❌ Removed |
| POST | `/auth/refresh-user-cache` | ❌ Removed |
| GET | `/auth/blacklist-stats` | ❌ Removed |
| GET | `/auth/me` | ✅ Kept |

### v2 Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/auth/me` | Get current user info |

> **Breaking Change**: Semua endpoint logout dan token management dipindahkan ke SSO Service. Frontend harus call SSO langsung untuk logout. login pun nanti harus ke sso dengan kirim client_id dari frontend hris agar bisa mekanisme redirect ke hris.

---

## 2. EMPLOYEES MODULE

### v1 Endpoints
| Method | Endpoint | Status |
|--------|----------|--------|
| GET | `/employees/deleted` | ✅ Kept |
| GET | `/employees/with-account` | ❌ Removed |
| POST | `/employees/bulk-insert` | ✅ Kept |
| POST | `/{user_id}/activate` | ❌ Removed |
| POST | `/{user_id}/deactivate` | ❌ Removed |
| POST | `/{user_id}/sync-to-sso` | ❌ Removed |
| DELETE | `/{user_id}` (soft delete) | ✅ Kept |
| POST | `/{user_id}/restore` | ✅ Kept |
| GET | `/employees` | ✅ Kept |
| GET | `/employees/{id}` | ✅ Kept |
| POST | `/employees` | ✅ Kept |
| PUT | `/employees/{id}` | ✅ Changed to PATCH |

### v2 Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/employees` | List employees (paginated) |
| GET | `/employees/deleted` | List deleted employees |
| GET | `/employees/{id}` | Get employee by ID |
| PATCH | `/employees/{id}` | Update employee |
| DELETE | `/employees/{id}` | Soft delete employee |
| POST | `/employees/{id}/restore` | Restore deleted employee |
| POST | `/employees` | Create employee (Admin only) |
| POST | `/employees/bulk-insert` | Bulk create from Excel |
| GET | `/employees/{id}/subordinates` | Get subordinates |
| GET | `/employees/org-unit/{org_unit_id}` | List by org unit |
| GET | `/employees/by-email/{email}` | Get by email |
| GET | `/employees/by-code/{code}` | Get by code |

> **Note**: Meskipun create employee bisa via SSO event (RabbitMQ), endpoint POST `/employees` tetap tersedia untuk Super Admin/HR Admin.

---

## 3. ATTENDANCES MODULE

### Status: **UNCHANGED** ✅

| Method | Endpoint | v1 | v2 |
|--------|----------|----|----|
| POST | `/attendances/check-in` | ✅ | ✅ |
| POST | `/attendances/check-out` | ✅ | ✅ |
| GET | `/attendances/reports` | ✅ | ✅ |
| GET | `/attendances/overview` | ✅ | ✅ |
| GET | `/attendances/check-attendance-status` | ✅ | ✅ |
| GET | `/attendances/my-attendance` | ✅ | ✅ |
| GET | `/attendances/team` | ✅ | ✅ |
| GET | `/attendances` | ✅ | ✅ |
| GET | `/attendances/{id}` | ✅ | ✅ |
| POST | `/attendances/bulk-mark-present` | ✅ | ✅ |
| PATCH | `/attendances/{id}/mark-present` | ✅ | ✅ |

---

## 4. LEAVE REQUESTS MODULE

### v1 → v2 Changes

| Method | Endpoint | Change |
|--------|----------|--------|
| POST | `/leave-requests` | **CHANGED** - Added `replacement_employee_id` field |
| GET | `/leave-requests` | **CHANGED** - Added `replacement_employee_name` in response |
| GET | `/leave-requests/{id}` | **CHANGED** - Added `replacement` object in response |
| GET | `/leave-requests/team/leave-requests` | **NEW** - Get team leave requests |

### New Request Field (Create)
```json
{
  "employee_id": 1,
  "leave_type": "leave",
  "start_date": "2025-12-19",
  "end_date": "2025-12-20",
  "reason": "Cuti tahunan",
  "replacement_employee_id": 2  // NEW - Optional
}
```

### New Response Fields
```json
{
  "id": 1,
  "employee_id": 32,
  "leave_type": "leave",
  "start_date": "2025-12-19",
  "end_date": "2025-12-20",
  "total_days": 2,
  "reason": "string",
  "replacement": {  // NEW
    "employee_id": 31,
    "employee_name": "John Doe",
    "employee_number": "IT-001",
    "assignment_id": 1,
    "assignment_status": "active"
  },
  "created_by": "uuid",
  "created_at": "...",
  "updated_at": "..."
}
```

### New Validation
- Jika employee sedang menjadi replacement (ada active assignment), tidak bisa mengajukan cuti yang overlap dengan periode assignment.

---

## 5. ORG UNITS MODULE

### Status: **CHANGED** (Enhanced) ✅

| Method | Endpoint | v1 | v2 |
|--------|----------|----|----|
| GET | `/org-units` | ✅ | ✅ |
| GET | `/org-units/deleted` | ❌ | ✅ (New) |
| GET | `/org-units/{id}` | ✅ | ✅ |
| GET | `/org-units/by-code/{code}` | ✅ | ✅ |
| GET | `/org-units/tree` (Check hierarchy endpoint) | ✅ | ✅ (Exposed via `{id}/hierarchy` or standard list with parent filter) |
| POST | `/org-units` | ✅ | ✅ |
| POST | `/org-units/bulk-insert` | ❌ | ✅ (New) |
| PUT | `/org-units/{id}` | ✅ | ✅ |
| DELETE | `/org-units/{id}` | ✅ | ✅ |
| POST | `/org-units/{id}/restore` | ❌ | ✅ (New) |
| GET | `/org-units/types/all` | ❌ | ✅ (New) |
| GET | `/org-units/{id}/children` | ✅ | ✅ |
| GET | `/org-units/{id}/hierarchy` | ✅ | ✅ |

---

## 6. RBAC/ROLES MODULE

### v1 → v2 Changes

| Method | Endpoint | Status |
|--------|----------|--------|
| GET | `/roles/permissions` | ✅ Kept |
| GET | `/roles` | ✅ Kept |
| GET | `/roles/{user_id}` | ✅ Kept |
| POST | `/roles/{user_id}/assign` | ✅ Kept |
| POST | `/roles/{user_id}/remove` | ✅ Kept |
| POST | `/roles/bulk-assign` | ❌ Removed |
| POST | `/roles/{user_id}/assign-multiple` | ✅ NEW |

---

## 7. SCHEDULED JOBS MODULE

### Status: **UNCHANGED** ✅

| Method | Endpoint | v1 | v2 |
|--------|----------|----|----|
| GET | `/scheduled-jobs/health` | ✅ | ✅ |
| GET | `/scheduled-jobs` | ✅ | ✅ |
| GET | `/scheduled-jobs/{id}` | ✅ | ✅ |
| GET | `/scheduled-jobs/{id}/history` | ✅ | ✅ |
| POST | `/scheduled-jobs/{id}/trigger` | ✅ | ✅ |

---

## 8. DASHBOARD MODULE

### Status: **UNCHANGED** ✅

| Method | Endpoint | v1 | v2 |
|--------|----------|----|----|
| GET | `/dashboard/summary` | ✅ | ✅ |

---

## 9. WORK SUBMISSIONS MODULE

### Status: **REMOVED** ❌

Seluruh module work_submissions dihapus di v2.

| Method | Endpoint | Status |
|--------|----------|--------|
| GET | `/work-submissions` | ❌ Removed |
| GET | `/work-submissions/{id}` | ❌ Removed |
| POST | `/work-submissions` | ❌ Removed |
| PUT | `/work-submissions/{id}` | ❌ Removed |
| DELETE | `/work-submissions/{id}` | ❌ Removed |

---

## 10. EMPLOYEE ASSIGNMENTS MODULE (NEW)

### Status: **NEW** ✅

Module baru untuk mengelola penggantian sementara (temporary replacement) saat karyawan cuti.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/assignments` | Create assignment |
| GET | `/assignments` | List assignments (paginated) |
| GET | `/assignments/{id}` | Get assignment by ID |
| POST | `/assignments/{id}/cancel` | Cancel assignment |

### Create Request
```json
{
  "employee_id": 2,           // ID pengganti
  "replaced_employee_id": 1,  // ID yang digantikan
  "start_date": "2025-12-19",
  "end_date": "2025-12-20",
  "leave_request_id": 1,      // Linked leave request
  "reason": "Pengganti selama cuti"
}
```

### Response
```json
{
  "id": 1,
  "employee_id": 2,
  "replaced_employee_id": 1,
  "org_unit_id": 5,
  "start_date": "2025-12-19",
  "end_date": "2025-12-20",
  "status": "active",         // pending | active | expired | cancelled
  "leave_request_id": 1,
  "reason": "...",
  "employee": {
    "id": 2,
    "number": "IT-001",
    "name": "John Doe",
    "position": "Staff"
  },
  "replaced_employee": {
    "id": 1,
    "number": "IT-002",
    "name": "Jane Doe",
    "position": "Manager"
  },
  "org_unit": {
    "id": 5,
    "code": "IT",
    "name": "IT Department",
    "type": "department"
  }
}
```

### Assignment Status Flow
```
pending → active → expired
    ↓
 cancelled
```

- **pending**: Menunggu start_date
- **active**: Sedang berjalan (start_date <= today <= end_date)
- **expired**: Sudah selesai (end_date < today)
- **cancelled**: Dibatalkan manual

---

## Frontend Migration Checklist

### ❌ Remove These API Calls
- [ ] `POST /auth/logout` → Use SSO logout
- [ ] `POST /auth/logout-all` → Use SSO
- [ ] `POST /auth/validate-token` → Use SSO
- [ ] `GET /auth/token-info` → Use SSO
- [ ] `GET /employees/with-account` → Removed
- [ ] `POST /{user_id}/activate` & `deactivate` → Removed
- [ ] All `/work-submissions/*` → Module removed

### ✅ Update These API Calls
- [ ] `PUT /employees/{id}` → Change to `PATCH /employees/{id}`
- [ ] Leave request create → Add optional `replacement_employee_id`
- [ ] Leave request responses → Handle new `replacement` object
- [ ] Employee Management: Re-implement Create, Delete, Restore, Bulk Insert using accessible endpoints if Admin features are needed.

### ➕ Add New Features
- [ ] Implement Assignment Management UI (`/assignments`)
- [ ] Show replacement info in Leave Request detail
- [ ] Validate assignment conflicts when creating leave
- [ ] Add Org Unit Management: Bulk Insert, Restore, Types

---

## Response Format Changes

### v1 Response
```json
{
  "success": true,
  "message": "...",
  "data": {...}
}
```

### v2 Response (Same)
```json
{
  "error": false,
  "message": "...",
  "timestamp": "ISO8601",
  "data": {...}
}
```

> Note: Field `success` renamed to inverted `error` field.

---

## Permissions Changes

### New Permissions (v2)
| Permission | Description |
|------------|-------------|
| `assignment.create` | Create employee assignment |
| `assignment.read` | View assignments |
| `assignment.cancel` | Cancel assignment |

---

*Last Updated: 2025-12-22*
