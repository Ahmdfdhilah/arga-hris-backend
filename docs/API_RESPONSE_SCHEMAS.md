# API Response Schemas untuk Frontend

Dokumentasi ini berisi ringkasan response schemas dari setiap API endpoint untuk membantu frontend developer dalam integrasi.

---

## Base Response Format

Semua API response mengikuti format berikut:

### Single Data Response

```typescript
interface DataResponse<T> {
  error: boolean;
  message: string;
  timestamp: string; // ISO 8601 format
  data: T | null;
}
```

### Paginated Response

```typescript
interface PaginatedResponse<T> {
  error: boolean;
  message: string;
  timestamp: string;
  data: T[];
  meta: {
    page: number;
    limit: number;
    total_items: number;
    total_pages: number;
    has_prev_page: boolean;
    has_next_page: boolean;
  };
}
```

---

## 1. Attendance Module

### Schemas

#### AttendanceResponse

```typescript
interface AttendanceResponse {
  id: number;
  employee_id: number;
  org_unit_id: number | null;
  attendance_date: string; // YYYY-MM-DD
  status: "present" | "absent" | "leave" | "hybrid" | "invalid";
  check_in_time: string | null; // ISO datetime
  check_out_time: string | null; // ISO datetime
  work_hours: number | null; // Decimal
  overtime_hours: number | null; // Decimal
  created_by: number | null;

  // Check-in fields
  check_in_submitted_at: string | null;
  check_in_submitted_ip: string | null;
  check_in_notes: string | null;
  check_in_latitude: number | null;
  check_in_longitude: number | null;
  check_in_location_name: string | null;

  // Check-out fields
  check_out_submitted_at: string | null;
  check_out_submitted_ip: string | null;
  check_out_notes: string | null;
  check_out_latitude: number | null;
  check_out_longitude: number | null;
  check_out_location_name: string | null;

  // Timestamps
  created_at: string;
  updated_at: string;

  // Signed URLs (generated)
  check_in_selfie_url: string | null;
  check_out_selfie_url: string | null;
}
```

#### AttendanceListResponse

```typescript
interface AttendanceListResponse {
  id: number;
  employee_id: number;
  employee_name: string | null;
  employee_number: string | null;
  org_unit_id: number | null;
  org_unit_name: string | null;
  attendance_date: string;
  status: "present" | "absent" | "leave" | "hybrid" | "invalid";
  check_in_time: string | null;
  check_out_time: string | null;
  work_hours: number | null;
  overtime_hours: number | null;
  check_in_notes: string | null;
  check_out_notes: string | null;
  created_at: string;
  updated_at: string;
}
```

#### AttendanceStatusCheckResponse

```typescript
interface AttendanceStatusCheckResponse {
  can_attend: boolean;
  reason: string | null;
  is_on_leave: boolean;
  is_working_day: boolean;
  employee_type: string | null;
  leave_details: {
    leave_type: string;
    start_date: string;
    end_date: string;
    total_days: number;
    reason: string | null;
  } | null;
}
```

#### BulkMarkPresentSummary

```typescript
interface BulkMarkPresentSummary {
  total_employees: number;
  created: number;
  updated: number;
  skipped: number;
  attendance_date: string;
  notes: string | null;
}
```

#### EmployeeAttendanceReport (untuk export Excel)

```typescript
interface EmployeeAttendanceReport {
  employee_id: number;
  employee_name: string;
  employee_number: string | null;
  employee_position: string | null;
  org_unit_id: number | null;
  org_unit_name: string | null;
  attendances: AttendanceRecordInReport[];
  total_present_days: number;
  total_work_hours: number | null;
  total_overtime_hours: number | null;
}

interface AttendanceRecordInReport {
  attendance_date: string;
  status: string;
  check_in_time: string | null;
  check_out_time: string | null;
  work_hours: number | null;
  overtime_hours: number | null;
}
```

#### EmployeeAttendanceOverview

```typescript
interface EmployeeAttendanceOverview {
  employee_id: number;
  employee_name: string;
  employee_number: string | null;
  employee_position: string | null;
  org_unit_id: number | null;
  org_unit_name: string | null;
  total_present: number;
  total_absent: number;
  total_leave: number;
  total_hybrid: number;
  total_work_hours: number | null;
  total_overtime_hours: number | null;
}
```

### Endpoints

| Method | Endpoint                               | Response Type                                   | Description              |
| ------ | -------------------------------------- | ----------------------------------------------- | ------------------------ |
| POST   | `/attendances/check-in`                | `DataResponse<AttendanceResponse>`              | Check-in (selfie wajib)  |
| POST   | `/attendances/check-out`               | `DataResponse<AttendanceResponse>`              | Check-out (selfie wajib) |
| GET    | `/attendances/check-attendance-status` | `DataResponse<AttendanceStatusCheckResponse>`   | Cek bisa absen           |
| GET    | `/attendances/my-attendance`           | `PaginatedResponse<AttendanceResponse>`         | History sendiri          |
| GET    | `/attendances/team`                    | `PaginatedResponse<AttendanceListResponse>`     | Attendance team          |
| GET    | `/attendances/`                        | `PaginatedResponse<AttendanceListResponse>`     | Semua attendance (admin) |
| GET    | `/attendances/{id}`                    | `DataResponse<AttendanceResponse>`              | By ID                    |
| GET    | `/attendances/reports`                 | `DataResponse<EmployeeAttendanceReport[]>`      | Report untuk export      |
| GET    | `/attendances/overview`                | `PaginatedResponse<EmployeeAttendanceOverview>` | Overview summary         |
| POST   | `/attendances/bulk-mark-present`       | `DataResponse<BulkMarkPresentSummary>`          | Bulk mark present        |

---

## 2. Organization Units Module

### Schemas

#### OrgUnitResponse

```typescript
interface OrgUnitResponse {
  id: number;
  code: string;
  name: string;
  type: string;
  parent_id: number | null;
  head_id: number | null;
  level: number;
  path: string;
  description: string | null;
  org_unit_metadata: Record<string, string> | null;
  is_active: boolean;
  employee_count: number;
  total_employee_count: number;
  created_at: string | null;
  updated_at: string | null;
  created_by: number | null;
  updated_by: number | null;
  parent: {
    id: number;
    code: string;
    name: string;
    type: string;
  } | null;
  head: {
    id: number;
    employee_number: string;
    name: string;
    position: string | null;
  } | null;
}
```

#### OrgUnitHierarchyResponse

```typescript
interface OrgUnitHierarchyResponse {
  root: OrgUnitResponse | null;
  hierarchy: OrgUnitHierarchyItem[];
}

interface OrgUnitHierarchyItem {
  org_unit: OrgUnitResponse;
  children: OrgUnitHierarchyItem[];
}
```

#### OrgUnitTypesResponse

```typescript
interface OrgUnitTypesResponse {
  types: string[];
}
```

#### OrgUnitDeleteResult

```typescript
interface OrgUnitDeleteResult {
  success: boolean;
  message: string;
}
```

### Endpoints

| Method | Endpoint                    | Response Type                            | Description       |
| ------ | --------------------------- | ---------------------------------------- | ----------------- |
| GET    | `/org-units/{id}`           | `DataResponse<OrgUnitResponse>`          | Get by ID         |
| GET    | `/org-units/by-code/{code}` | `DataResponse<OrgUnitResponse>`          | Get by code       |
| GET    | `/org-units/`               | `PaginatedResponse<OrgUnitResponse>`     | List with filters |
| GET    | `/org-units/{id}/children`  | `PaginatedResponse<OrgUnitResponse>`     | Get children      |
| GET    | `/org-units/{id}/hierarchy` | `DataResponse<OrgUnitHierarchyResponse>` | Get hierarchy     |
| GET    | `/org-units/types/all`      | `DataResponse<OrgUnitTypesResponse>`     | Get all types     |
| POST   | `/org-units/`               | `DataResponse<OrgUnitResponse>`          | Create (admin)    |
| PUT    | `/org-units/{id}`           | `DataResponse<OrgUnitResponse>`          | Update (admin)    |
| DELETE | `/org-units/{id}`           | `DataResponse<OrgUnitDeleteResult>`      | Delete (admin)    |

---

## 3. Employees Module

### Schemas

#### EmployeeResponse

```typescript
interface EmployeeResponse {
  id: number;
  employee_number: string;
  name: string;
  email: string | null;
  phone: string | null;
  position: string | null;
  employee_type: string | null;
  employee_gender: string | null;
  org_unit_id: number | null;
  supervisor_id: number | null;
  employee_metadata: Record<string, string> | null;
  is_active: boolean;
  created_at: string | null;
  updated_at: string | null;
  created_by: number | null;
  updated_by: number | null;
  user_id: number | null;
  org_unit: {
    id: number;
    code: string;
    name: string;
    type: string;
  } | null;
  supervisor: {
    id: number;
    employee_number: string;
    name: string;
    position: string | null;
  } | null;
}
```

#### EmployeeAccountData (untuk create)

```typescript
interface EmployeeAccountData {
  employee: EmployeeResponse;
  user: UserNestedResponse | null;
  guest_account: GuestAccountNestedResponse | null;
  temporary_password: string | null; // Generated password
  warnings: string[];
}
```

#### EmployeeAccountUpdateData (untuk update)

```typescript
interface EmployeeAccountUpdateData {
  employee: EmployeeResponse | null;
  user: UserNestedResponse;
  guest_account: GuestAccountNestedResponse | null;
  updated_fields: {
    user: string[];
    employee: string[];
    guest_account: string[];
  };
  warnings: string[];
}
```

#### EmployeeAccountListItem (untuk list)

```typescript
interface EmployeeAccountListItem {
  employee: EmployeeResponse | null;
  user: UserNestedResponse;
  guest_account: GuestAccountNestedResponse | null;
}
```

#### UserNestedResponse

```typescript
interface UserNestedResponse {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  org_unit_id: number | null;
  employee_id: number | null;
  is_active: boolean;
}
```

#### GuestAccountNestedResponse

```typescript
interface GuestAccountNestedResponse {
  id: number;
  user_id: number;
  guest_type: string;
  valid_from: string | null;
  valid_until: string | null;
  sponsor_id: number | null;
  notes: string | null;
}
```

### Endpoints

| Method | Endpoint                             | Response Type                                | Description         |
| ------ | ------------------------------------ | -------------------------------------------- | ------------------- |
| GET    | `/employees/with-account`            | `PaginatedResponse<EmployeeAccountListItem>` | List with account   |
| GET    | `/employees/{user_id}/with-account`  | `DataResponse<EmployeeAccountListItem>`      | Get with account    |
| POST   | `/employees/with-account`            | `DataResponse<EmployeeAccountData>`          | Create with account |
| PUT    | `/employees/{user_id}/with-account`  | `DataResponse<EmployeeAccountUpdateData>`    | Update with account |
| GET    | `/employees/{id}`                    | `DataResponse<EmployeeResponse>`             | Get by ID           |
| GET    | `/employees/by-email/{email}`        | `DataResponse<EmployeeResponse \| null>`     | Get by email        |
| GET    | `/employees/by-number/{number}`      | `DataResponse<EmployeeResponse \| null>`     | Get by number       |
| GET    | `/employees/`                        | `PaginatedResponse<EmployeeResponse>`        | List employees      |
| GET    | `/employees/{id}/subordinates`       | `PaginatedResponse<EmployeeResponse>`        | Get subordinates    |
| GET    | `/employees/org-unit/{id}/employees` | `PaginatedResponse<EmployeeResponse>`        | By org unit         |
| POST   | `/employees/`                        | `DataResponse<EmployeeResponse>`             | Create employee     |
| PUT    | `/employees/{id}`                    | `DataResponse<EmployeeResponse>`             | Update employee     |
| DELETE | `/employees/{id}`                    | `DataResponse<EmployeeResponse>`             | Deactivate          |
| POST   | `/employees/{user_id}/activate`      | `DataResponse<string[]>`                     | Activate account    |
| POST   | `/employees/{user_id}/deactivate`    | `DataResponse<string[]>`                     | Deactivate account  |
| POST   | `/employees/{user_id}/sync-to-sso`   | `DataResponse<string[]>`                     | Sync to SSO         |

---

## Catatan Penting untuk Frontend

### 1. Error Handling

Semua error response mengikuti format yang sama:

```typescript
interface ErrorResponse {
  error: true;
  message: string;
  timestamp: string;
  data: null;
}
```

### 2. Pagination

- Default `limit`: 10
- Maximum `limit`: 250
- Gunakan `meta.has_next_page` untuk load more

### 3. Date/Time Format

- Date: `YYYY-MM-DD` (contoh: "2024-01-15")
- DateTime: ISO 8601 with timezone (contoh: "2024-01-15T09:30:00+07:00")

### 4. File Upload (Attendance)

Check-in dan check-out memerlukan multipart/form-data dengan:

- `selfie`: File gambar (WAJIB)
- `notes`: string (opsional)
- `latitude`: number (opsional)
- `longitude`: number (opsional)

### 5. Authentication

Semua endpoint memerlukan Bearer token di header:

```
Authorization: Bearer <access_token>
```

### 6. Permission/Role Based

- Beberapa endpoint memerlukan permission tertentu (misal: `employee.read`)
- Beberapa endpoint memerlukan role tertentu (misal: `hr_admin`, `super_admin`)
