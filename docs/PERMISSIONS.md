# HRIS Permissions List

## Permission Naming Convention

Format: `{resource}.{action}[_scope]`

- `resource`: nama resource (singular)
- `action`: operasi yang dilakukan (create, read, update, delete, dll)
- `scope` (optional): `own`, `team`, `all` untuk membedakan scope akses

## All Permissions

### 1. Employee Permissions

| Code | Description | Usage |
|------|-------------|-------|
| `employee.read` | View employee data (all employees) | Get employee by ID, list employees, search |
| `employee.create` | Create new employee | Super admin only - master data |
| `employee.update` | Update employee data | Super admin only - master data |
| `employee.delete` | Delete/deactivate employee | Super admin only - soft delete |
| `employee.export` | Export employee data | Generate reports, export to CSV/Excel |

### 2. Organization Unit Permissions

| Code | Description | Usage |
|------|-------------|-------|
| `org_unit.read` | View organization units | Get org unit, list org units, hierarchy |
| `org_unit.create` | Create organization unit | Admin/Super admin |
| `org_unit.update` | Update organization unit | Admin/Super admin |
| `org_unit.delete` | Delete organization unit | Super admin only |

### 3. Leave Request Permissions

| Code | Description | Usage |
|------|-------------|-------|
| `leave_request.read_own` | View own leave requests | Employee can see their own leave requests |
| `leave_request.read` | View specific leave request by ID | HR Admin/Super admin |
| `leave_request.read_all` | View all leave requests | HR Admin/Super admin - list all |
| `leave_request.create` | Create leave request | HR Admin/Super admin only |
| `leave_request.update` | Update leave request | HR Admin/Super admin only |
| `leave_request.delete` | Delete leave request | HR Admin/Super admin only |
| `leave_request.approve` | Approve/reject leave request | Manager/HR Admin (future) |

### 4. Attendance Permissions

| Code | Description | Usage |
|------|-------------|-------|
| `attendance.create` | Create attendance (check-in/check-out) | All employees |
| `attendance.read_own` | View own attendance history | Employee can see their own attendance |
| `attendance.read_team` | View team/subordinates attendance | Org unit head only |
| `attendance.read` | View specific attendance by ID | HR Admin/Super admin |
| `attendance.read_all` | View all attendances with filters | HR Admin/Super admin |
| `attendance.update` | Update attendance record | Admin/Super admin |
| `attendance.approve` | Approve attendance corrections | Manager/HR Admin |
| `attendance.export` | Export attendance data | Reports, payroll processing |

### 5. User Permissions

| Code | Description | Usage |
|------|-------------|-------|
| `user.read` | View user data | Admin/Super admin |
| `user.read_own` | View own user profile | All users |
| `user.update` | Update user data | Admin/Super admin |
| `user.update_own` | Update own basic profile | All users |
| `user.create` | Create new user | Super admin only |
| `user.delete` | Delete/deactivate user | Super admin only |

### 6. Guest Account Permissions

| Code | Description | Usage |
|------|-------------|-------|
| `guest.read` | View guest accounts | HR Admin/Super admin |
| `guest.create` | Create guest account | HR Admin/Super admin |
| `guest.update` | Update guest account | HR Admin/Super admin |
| `guest.delete` | Delete guest account | Super admin only |

### 7. Role & Permission Management

| Code | Description | Usage |
|------|-------------|-------|
| `role.read` | View roles | Admin/Super admin |
| `role.create` | Create custom roles | Super admin only |
| `role.update` | Update roles | Super admin only |
| `role.delete` | Delete custom roles | Super admin only |
| `role.assign` | Assign roles to users | Super admin only |

### 8. Scheduled Jobs Permissions

| Code | Description | Usage |
|------|-------------|-------|
| `scheduled_job.read` | View scheduled jobs status & history | HR Admin/Super admin |
| `scheduled_job.execute` | Manually trigger scheduled jobs | Super admin only |

---

## Role-Permission Matrix

### Super Admin
**Full system access** - ALL permissions

### HR Admin
- All `employee.*` permissions
- All `org_unit.*` permissions (except delete)
- All `leave_request.*` permissions
- All `attendance.*` permissions (except create)
- All `user.*` permissions (except create, delete)
- All `guest.*` permissions (except delete)
- `role.read`

### Org Unit Head
- `employee.read`
- `org_unit.read`
- `attendance.create`
- `attendance.read_own`
- `attendance.read_team`  Special permission
- `attendance.approve`
- `leave_request.read_own`
- `user.read_own`
- `user.update_own`

### Employee
- `employee.read` (limited - can view basic info)
- `org_unit.read` (view structure)
- `attendance.create` (check-in/check-out)
- `attendance.read_own`  Can only view own
- `leave_request.read_own`  Can only view own
- `user.read_own`
- `user.update_own`

### Guest
- `attendance.create` (check-in/check-out only)
- `attendance.read_own`
- `user.read_own`
- `user.update_own` (limited fields)

---

## Implementation Notes

### 1. Scope Suffixes
- `_own`: User can only access their own resources
- `_team`: User can access team/subordinates resources
- No suffix: Full access to resource

### 2. Endpoint to Permission Mapping

#### Employees
```python
GET    /employees                          -> employee.read
GET    /employees/{id}                     -> employee.read
POST   /employees                          -> employee.create
PUT    /employees/{id}                     -> employee.update
DELETE /employees/{id}                     -> employee.delete
```

#### Leave Requests
```python
GET    /leave-requests/my-leave-requests   -> leave_request.read_own
GET    /leave-requests                     -> leave_request.read_all
GET    /leave-requests/{id}                -> leave_request.read
POST   /leave-requests                     -> leave_request.create
PUT    /leave-requests/{id}                -> leave_request.update
DELETE /leave-requests/{id}                -> leave_request.delete
```

#### Attendance
```python
POST   /attendances/check-in               -> attendance.create
POST   /attendances/check-out              -> attendance.create
GET    /attendances/my-attendance          -> attendance.read_own
GET    /attendances/team                   -> attendance.read_team
GET    /attendances                        -> attendance.read_all
GET    /attendances/{id}                   -> attendance.read
POST   /attendances/bulk-mark-present      -> attendance.update (admin)
```

### 3. Context-Based Access Control

Beberapa endpoint perlu additional logic check:
- Employee dengan `employee.read` hanya bisa view basic info
- Org unit head dengan `attendance.read_team` hanya bisa view subordinates
- User dengan `_own` permissions harus validate `current_user.id == resource.user_id`
