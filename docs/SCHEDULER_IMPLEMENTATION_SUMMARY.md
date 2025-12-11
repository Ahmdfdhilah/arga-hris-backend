# Scheduler Framework - Implementation Summary

## Overview

Scheduler framework generic dan scalable untuk menjalankan scheduled jobs/tasks otomatis di HRIS Service.

**Tanggal Implementasi**: 2 November 2025

---

##  Fitur Utama

1. **Generic & Reusable** - Base class untuk semua scheduled jobs
2. **Distributed Lock** - Redis-based locking (multi-instance safe)
3. **Execution Logging** - Semua job execution logged ke PostgreSQL
4. **Error Handling** - Automatic retry & error tracking
5. **Admin API** - REST API untuk monitoring & manual trigger
6. **RBAC Protected** - Permission-based access control
7. **Scalable** - Mudah menambahkan job baru

---

## 📁 File Structure

```
app/
├── core/
│   └── scheduler/
│       ├── __init__.py               Package exports
│       ├── base.py                   BaseScheduledJob abstract class
│       ├── manager.py                SchedulerManager (APScheduler wrapper)
│       ├── decorators.py             Job registration decorators
│       └── redis_lock.py             Redis distributed locking
│
├── modules/
│   └── scheduled_jobs/
│       ├── models/
│       │   └── job_execution.py      JobExecution SQLAlchemy model
│       ├── schemas/
│       │   ├── requests.py           Request schemas
│       │   └── responses.py          Response schemas
│       ├── repositories/
│       │   └── job_execution_repository.py   Database operations
│       ├── services/
│       │   └── job_management_service.py     Business logic (follow RULES.MD)
│       ├── routers/
│       │   └── scheduled_jobs.py     Admin API endpoints (RBAC protected)
│       └── jobs/
│           ├── __init__.py
│           └── auto_create_daily_attendance.py   Implementasi job pertama
│
├── tasks/
│   └── scheduler_startup.py          Lifecycle integration
│
└── main.py                           FastAPI lifespan integration

alembic/versions/
└── b62610f54d65_add_job_executions_table.py   Migration

docs/
├── SCHEDULER_GUIDE.md                User guide lengkap
├── SCHEDULER_IMPLEMENTATION_SUMMARY.md   Dokumen ini
└── PERMISSIONS.md                    Updated dengan scheduled_job permissions

requirements.txt                      APScheduler==3.10.4 added
```

---

## 🔧 Tech Stack

| Component | Library/Tool | Version |
|-----------|--------------|---------|
| Scheduler | APScheduler | 3.10.4 |
| Distributed Lock | Redis | 5.2.0 |
| Database | PostgreSQL + SQLAlchemy | 2.0.36 |
| Framework | FastAPI | 0.115.0 |

---

## 📊 Database Schema

### Table: `job_executions`

```sql
CREATE TABLE job_executions (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(100) NOT NULL,  -- Index
    started_at TIMESTAMPTZ NOT NULL,
    finished_at TIMESTAMPTZ,
    duration_seconds NUMERIC(10,3),
    success BOOLEAN NOT NULL DEFAULT false,
    message TEXT,
    error_trace TEXT,
    result_data JSON,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX ix_job_executions_job_id ON job_executions(job_id);
```

---

## 🔐 RBAC Permissions

Ditambahkan 2 permissions baru di `docs/PERMISSIONS.md`:

| Permission | Description | Role |
|------------|-------------|------|
| `scheduled_job.read` | View jobs status & history | HR Admin, Super Admin |
| `scheduled_job.execute` | Manual trigger jobs | Super Admin only |

---

## 🚀 API Endpoints

Base URL: `/api/v1/scheduled-jobs`

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| GET | `/` | scheduled_job.read | List all jobs |
| GET | `/{job_id}` | scheduled_job.read | Get job status |
| POST | `/{job_id}/trigger` | scheduled_job.execute | Manual trigger |
| GET | `/{job_id}/history` | scheduled_job.read | Execution history |
| GET | `/executions/recent` | scheduled_job.read | Recent executions |

---

## 📝 Job Pertama: Auto Create Daily Attendance

### File
`app/modules/scheduled_jobs/jobs/auto_create_daily_attendance.py`

### Schedule
Setiap hari jam **00:30 WIB** (`30 0 * * *`)

### Business Logic

**Problem Statement**:
- Karyawan harus clock in terlebih dahulu baru ada row attendance
- Jika tidak clock in, tidak ada row = tidak bisa di-track
- Sulit monitoring siapa yang tidak masuk kerja

**Solution**:
1. Job berjalan setiap tengah malam (00:30)
2. Fetch semua karyawan aktif dari Workforce Service via gRPC
3. Create attendance record untuk hari ini dengan status **"absent"**
4. Jika karyawan clock in, status berubah menjadi **"present"**
5. Jika tidak clock in sampai akhir hari, tetap **"absent"** (trackable)

### Flow

```
00:30 WIB - Job Start
    │
    ├─> Fetch active employees (gRPC)
    │
    ├─> Loop each employee:
    │   ├─> Check if attendance exists for today
    │   ├─> If NOT exists:
    │   │   └─> Create attendance (status: "absent")
    │   └─> If exists: Skip
    │
    └─> Log result: created/skipped/errors
```

### Result Data

```json
{
  "success": true,
  "message": "Auto-create attendance selesai. Total: 150, Created: 150, Skipped: 0, Errors: 0",
  "data": {
    "date": "2025-11-02",
    "total_employees": 150,
    "created": 150,
    "skipped": 0,
    "errors": 0
  }
}
```

---

## 🔄 Lifecycle Integration

### FastAPI Startup

```python
# app/main.py

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize scheduler
    await setup_scheduler()
    
    yield
    
    # Shutdown: Stop scheduler
    await shutdown_scheduler()

app = FastAPI(lifespan=lifespan)
```

### Scheduler Setup

```python
# app/tasks/scheduler_startup.py

async def setup_scheduler():
    1. Connect to Redis (existing client)
    2. Initialize SchedulerManager
    3. Set log callback (save to DB)
    4. Register all jobs
    5. Start scheduler (non-blocking)
```

---

## 🔒 Distributed Locking

### Problem
Multiple service instances bisa menjalankan job yang sama secara bersamaan.

### Solution
Redis distributed lock dengan pattern:

```python
lock_key = f"scheduler_lock:{job_id}"

1. Before execute:
   - SET lock_key "locked" NX EX 600  # 10 min TTL
   - If success: Execute job
   - If fail: Skip (another instance running)

2. After execute:
   - DELETE lock_key
```

### Benefits
-  Single execution guarantee
-  Automatic lock release (TTL)
-  Works across multiple instances

---

## 📖 Documentation

### 1. SCHEDULER_GUIDE.md
Dokumentasi lengkap untuk developer:
- Quick start: Membuat job baru
- Cron expression reference
- Admin API usage
- Best practices
- Monitoring & troubleshooting
- FAQ

### 2. SCHEDULER_IMPLEMENTATION_SUMMARY.md
Dokumen ini - overview implementasi.

### 3. PERMISSIONS.md
Updated dengan scheduled_job permissions.

---

##  Testing Checklist

### Pre-Deployment

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run migration: `alembic upgrade head`
- [ ] Verify `job_executions` table created
- [ ] Check Redis connection
- [ ] Start service: `uvicorn app.main:app --reload`
- [ ] Verify scheduler logs: "Scheduler started successfully"

### Manual Testing

- [ ] GET `/api/v1/scheduled-jobs` - List jobs
- [ ] GET `/api/v1/scheduled-jobs/auto_create_daily_attendance` - Job status
- [ ] POST `/api/v1/scheduled-jobs/auto_create_daily_attendance/trigger` - Manual trigger
- [ ] Verify attendance records created in `attendances` table
- [ ] Check execution log in `job_executions` table
- [ ] GET `/api/v1/scheduled-jobs/auto_create_daily_attendance/history` - View history

### Permission Testing

- [ ] Super admin: Can read & execute jobs 
- [ ] HR admin: Can read jobs 
- [ ] Employee: Cannot access (403 Forbidden) 

---

## 🎯 Next Steps (Future Enhancement)

### Additional Jobs Ideas

1. **Daily Attendance Summary Email**
   - Schedule: `0 18 * * *` (6 PM)
   - Send summary ke HR: hadir, absent, late

2. **Weekly Report Generator**
   - Schedule: `0 8 * * 1` (Monday 8 AM)
   - Generate weekly attendance report

3. **Leave Request Auto-Expire**
   - Schedule: `0 1 * * *` (1 AM)
   - Expire pending leave requests > 7 days

4. **Job Execution Log Cleanup**
   - Schedule: `0 2 1 * *` (1st of month, 2 AM)
   - Delete logs older than 90 days

5. **Employee Birthday Reminder**
   - Schedule: `0 9 * * *` (9 AM)
   - Send birthday notifications

### Framework Enhancements

- [ ] Job dependencies (Job B runs after Job A)
- [ ] Job chaining & workflow
- [ ] Webhook notifications on failure
- [ ] Slack/Email alerting integration
- [ ] Job pause/resume via API
- [ ] Job history retention policy
- [ ] Metrics & monitoring dashboard

---

## 📌 Notes

### Design Decisions

1. **APScheduler vs Celery**
   - Pilih APScheduler: Lightweight, cukup untuk scheduled jobs
   - Celery: Overkill untuk use case ini (butuh RabbitMQ/Redis broker)

2. **In-Process vs Separate Worker**
   - Pilih in-process: Simpler deployment
   - Jobs ringan, tidak butuh dedicated worker

3. **Database Logging**
   - Semua execution logged untuk audit trail
   - Bisa di-query untuk analytics & debugging

4. **Redis Lock**
   - Essential untuk multi-instance deployment
   - Prevent duplicate execution

### Constraints

- Job tidak persistent: Jika service down saat scheduled time, job tidak execute
- Max 1000 employees per page (adjust jika lebih)
- Lock TTL 10 menit (adjust sesuai job duration)

---

## 🤝 Contributing

### Adding New Job

1. Create file di `app/modules/scheduled_jobs/jobs/`
2. Inherit dari `BaseScheduledJob`
3. Implement `execute()` method
4. Register di `scheduler_startup.py`
5. Restart service
6. Test via manual trigger API

### Code Review Checklist

- [ ] Follow `RULES.MD` patterns
- [ ] Idempotent job execution
- [ ] Proper error handling
- [ ] Logging statements
- [ ] Docstring lengkap
- [ ] Test manual trigger
- [ ] Verify execution logs

---

## 📞 Support

Untuk issue atau pertanyaan:
1. Check `SCHEDULER_GUIDE.md`
2. Review execution logs
3. Check `job_executions` table
4. Contact: Backend Team Lead

---

**Document Version**: 1.0
**Last Updated**: 2 November 2025
**Status**:  Ready for Production
