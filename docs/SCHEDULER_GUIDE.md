# Panduan Scheduler Framework

## Overview

Scheduler framework generic untuk menjalankan scheduled jobs/tasks secara otomatis dengan fitur:

-  **Generic & Reusable** - Base class untuk semua scheduled jobs
-  **Distributed Lock** - Redis-based locking untuk prevent duplicate execution (multi-instance safe)
-  **Execution Logging** - Semua job execution logged ke database
-  **Error Handling** - Automatic retry & error tracking
-  **Admin API** - REST API untuk monitoring & manual trigger
-  **RBAC Protected** - Permission-based access control
-  **Scalable** - Mudah menambahkan job baru

---

## Arsitektur

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Lifecycle                     │
│  (startup: init scheduler, shutdown: stop scheduler)    │
└──────────────────────┬──────────────────────────────────┘
                       │
         ┌─────────────▼──────────────┐
         │   Scheduler Manager         │
         │   (APScheduler wrapper)     │
         └─────────────┬───────────────┘
                       │
         ┌─────────────▼──────────────┐
         │  Redis Distributed Lock     │
         │  (prevent duplicate runs)   │
         └─────────────┬───────────────┘
                       │
         ┌─────────────▼──────────────┐
         │   BaseScheduledJob          │
         │   (abstract base class)     │
         └─────────────┬───────────────┘
                       │
      ┌────────────────┼────────────────┐
      │                │                │
┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
│   Job 1   │   │   Job 2   │   │   Job 3   │
│ Auto      │   │ Daily     │   │ Cleanup   │
│ Attendance│   │ Report    │   │ Logs      │
└───────────┘   └───────────┘   └───────────┘
```

---

## Quick Start: Membuat Job Baru

### 1. Buat Job Class

```python
# app/modules/scheduled_jobs/jobs/my_new_job.py

from typing import Dict, Any
from datetime import date
import logging

from app.core.scheduler.base import BaseScheduledJob
from app.config.database import get_db_context

logger = logging.getLogger(__name__)


class MyNewJob(BaseScheduledJob):
    """
    Deskripsi job dalam Bahasa Indonesia.
    """

    # REQUIRED: Unique identifier
    job_id = "my_new_job"
    
    # REQUIRED: Deskripsi job
    description = "Deskripsi singkat job ini"
    
    # SCHEDULE: Pilih salah satu (cron atau interval)
    cron = "0 9 * * *"  # Setiap hari jam 9 pagi
    # interval_seconds = 3600  # Atau setiap 1 jam
    
    # OPTIONAL: Configuration
    enabled = True
    max_retries = 3
    retry_delay_seconds = 60

    async def execute(self) -> Dict[str, Any]:
        """
        Method utama yang akan dijalankan scheduler.
        
        Returns:
            Dict dengan keys:
                - success: bool
                - message: str
                - data: Optional[Any]
        """
        logger.info("Memulai MyNewJob...")
        
        try:
            # Business logic di sini
            async with get_db_context() as db:
                # Gunakan repository/service pattern
                # repo = MyRepository(db)
                # result = await repo.do_something()
                pass
            
            return {
                "success": True,
                "message": "Job berhasil dijalankan",
                "data": {
                    "processed": 100,
                }
            }
        
        except Exception as e:
            logger.error(f"Error dalam MyNewJob: {e}")
            raise
```

### 2. Register Job

Edit `app/tasks/scheduler_startup.py`:

```python
# Import job baru
from app.modules.scheduled_jobs.jobs.my_new_job import MyNewJob

# Dalam function setup_scheduler()
jobs_to_register = [
    AutoCreateDailyAttendanceJob(),
    MyNewJob(),  #  Tambahkan job baru
    # ... job lainnya
]
```

### 3. Restart Service

Job akan auto-register saat service start:

```bash
uvicorn app.main:app --reload
```

---

## Cron Expression Reference

Format: `minute hour day month day_of_week`

| Schedule | Cron Expression | Deskripsi |
|----------|----------------|-----------|
| Setiap hari jam 00:30 | `30 0 * * *` | Midnight + 30 menit |
| Setiap hari jam 9 pagi | `0 9 * * *` | 09:00 WIB |
| Setiap Senin jam 8 pagi | `0 8 * * 1` | Weekly, Monday 08:00 |
| Setiap 1 jam | `0 * * * *` | Top of every hour |
| Setiap 15 menit | `*/15 * * * *` | Every 15 minutes |
| Akhir bulan jam 23:00 | `0 23 L * *` | Last day of month |
| Hari kerja jam 18:00 | `0 18 * * 1-5` | Weekdays only |

**Atau gunakan interval:**

```python
interval_seconds = 3600  # Setiap 1 jam
interval_seconds = 86400  # Setiap 1 hari
```

---

## Admin API Endpoints

Semua endpoints memerlukan RBAC permissions.

### 1. List All Jobs

```bash
GET /api/v1/scheduled-jobs
Authorization: Bearer <token>
Permission: scheduled_job.read
```

Response:
```json
{
  "status": "success",
  "message": "Ditemukan 3 scheduled jobs",
  "data": [
    {
      "job_id": "auto_create_daily_attendance",
      "name": "Auto-create attendance records...",
      "description": "...",
      "next_run": "2025-11-03T00:30:00+07:00",
      "trigger": "cron[hour='0', minute='30']",
      "enabled": true
    }
  ]
}
```

### 2. Get Job Status

```bash
GET /api/v1/scheduled-jobs/{job_id}
Authorization: Bearer <token>
Permission: scheduled_job.read
```

Response:
```json
{
  "status": "success",
  "message": "Detail job berhasil diambil",
  "data": {
    "job_id": "auto_create_daily_attendance",
    "name": "...",
    "next_run": "2025-11-03T00:30:00+07:00",
    "trigger": "cron[hour='0', minute='30']",
    "enabled": true,
    "latest_execution": {
      "id": 123,
      "job_id": "auto_create_daily_attendance",
      "started_at": "2025-11-02T00:30:00+07:00",
      "finished_at": "2025-11-02T00:30:15+07:00",
      "duration_seconds": 15.234,
      "success": true,
      "message": "Auto-create attendance selesai...",
      "result_data": {
        "created": 150,
        "skipped": 0
      }
    }
  }
}
```

### 3. Manual Trigger Job

```bash
POST /api/v1/scheduled-jobs/{job_id}/trigger
Authorization: Bearer <token>
Permission: scheduled_job.execute
```

Response:
```json
{
  "status": "success",
  "message": "Job berhasil dijalankan",
  "data": {
    "job_id": "auto_create_daily_attendance",
    "success": true,
    "result": { ... }
  }
}
```

### 4. Get Job Execution History

```bash
GET /api/v1/scheduled-jobs/{job_id}/history?page=1&limit=20
Authorization: Bearer <token>
Permission: scheduled_job.read
```

Response:
```json
{
  "status": "success",
  "message": "History eksekusi job auto_create_daily_attendance",
  "data": [ ... ],
  "meta": {
    "page": 1,
    "limit": 20,
    "total_items": 100,
    "total_pages": 5
  }
}
```

### 5. Get Recent Executions (All Jobs)

```bash
GET /api/v1/scheduled-jobs/executions/recent?hours=24
Authorization: Bearer <token>
Permission: scheduled_job.read
```

---

## Database Schema

### Table: `job_executions`

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| job_id | VARCHAR(100) | Unique job identifier |
| started_at | TIMESTAMP | Waktu mulai eksekusi |
| finished_at | TIMESTAMP | Waktu selesai eksekusi |
| duration_seconds | NUMERIC(10,3) | Durasi dalam detik |
| success | BOOLEAN | Status keberhasilan |
| message | TEXT | Pesan hasil |
| error_trace | TEXT | Stack trace jika error |
| result_data | JSON | Data hasil eksekusi |
| created_at | TIMESTAMP | Timestamp created |
| updated_at | TIMESTAMP | Timestamp updated |

---

## Distributed Locking (Multi-Instance)

Scheduler menggunakan Redis distributed lock untuk prevent duplicate execution ketika running multiple instances:

1. Sebelum execute job, acquire lock di Redis dengan TTL
2. Jika lock sudah ada (instance lain sedang menjalankan), skip execution
3. Setelah selesai, release lock

**Ini menjamin hanya 1 instance yang menjalankan job pada waktu yang sama.**

---

## Best Practices

### 1. Job Idempotency

**PENTING**: Job harus idempotent (aman dijalankan multiple kali).

```python
#  GOOD: Check existing sebelum create
existing = await repo.get_by_date(today)
if existing:
    logger.info("Data sudah ada, skip")
    return

await repo.create(new_data)
```

```python
#  BAD: Langsung create tanpa check
await repo.create(new_data)  # Bisa duplicate jika retry
```

### 2. Error Handling

```python
async def execute(self) -> Dict[str, Any]:
    try:
        # Business logic
        result = await do_something()
        
        return {
            "success": True,
            "message": "Berhasil",
            "data": result
        }
    except SpecificException as e:
        logger.error(f"Specific error: {e}")
        # Handle specific error
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise  # Will be caught by framework
```

### 3. Logging

```python
logger.info("Memulai job...")
logger.debug(f"Processing item {i}")
logger.warning("Kondisi tidak normal")
logger.error("Terjadi error", exc_info=True)
```

### 4. Database Transactions

```python
async with get_db_context() as db:
    repo = MyRepository(db)
    
    # Multiple operations dalam satu transaction
    item1 = await repo.create(data1)
    item2 = await repo.update(data2)
    
    # Auto commit saat exit context
```

### 5. Large Dataset Processing

```python
# Process dalam batch untuk avoid memory issues
limit = 100
page = 1

while True:
    items = await repo.list(page=page, limit=limit)
    if not items:
        break
    
    for item in items:
        await process_item(item)
    
    page += 1
    logger.info(f"Processed page {page}")
```

---

## Monitoring & Troubleshooting

### 1. Check Job Status

```bash
# Via API
curl -H "Authorization: Bearer <token>" \
  http://localhost:8002/api/v1/scheduled-jobs
```

### 2. View Logs

```bash
# Application logs
tail -f logs/app.log | grep "scheduler"
tail -f logs/app.log | grep "auto_create_daily_attendance"
```

### 3. Database Query

```sql
-- Recent executions
SELECT job_id, started_at, duration_seconds, success, message
FROM job_executions
ORDER BY started_at DESC
LIMIT 20;

-- Failed executions
SELECT *
FROM job_executions
WHERE success = false
  AND started_at >= NOW() - INTERVAL '24 hours'
ORDER BY started_at DESC;

-- Job statistics
SELECT 
  job_id,
  COUNT(*) as total_runs,
  SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_runs,
  AVG(duration_seconds) as avg_duration
FROM job_executions
WHERE started_at >= NOW() - INTERVAL '7 days'
GROUP BY job_id;
```

### 4. Manual Trigger (Testing)

```bash
# Via API
curl -X POST \
  -H "Authorization: Bearer <token>" \
  http://localhost:8002/api/v1/scheduled-jobs/auto_create_daily_attendance/trigger
```

---

## Example: Job yang Ada

### AutoCreateDailyAttendanceJob

**File**: `app/modules/scheduled_jobs/jobs/auto_create_daily_attendance.py`

**Schedule**: Setiap hari jam 00:30 WIB (`30 0 * * *`)

**Business Logic**:
1. Fetch semua karyawan aktif dari Workforce Service (gRPC)
2. Loop setiap karyawan
3. Check apakah attendance untuk hari ini sudah ada
4. Jika belum ada, create row baru dengan status "absent"
5. Log hasil: created, skipped, errors

**Use Case**:
- Karyawan wajib clock in untuk mengubah status dari "absent" menjadi "present"
- Jika tidak clock in, row tetap "absent" untuk tracking
- Menghindari situasi "tidak ada data attendance" yang tidak bisa di-track

---

## FAQ

### Q: Bagaimana jika service restart saat job sedang berjalan?

A: Redis lock akan tetap ada dengan TTL. Job tidak akan di-execute ulang sampai lock expire atau released.

### Q: Apakah job akan di-execute jika service down pada scheduled time?

A: Tidak. APScheduler tidak persistent. Job hanya execute jika service running pada scheduled time.

### Q: Bagaimana cara disable job sementara?

A: Set `enabled = False` di job class dan restart service.

### Q: Apakah bisa menjalankan job di specific timezone?

A: Ya, scheduler sudah di-set ke `Asia/Jakarta` timezone.

### Q: Bagaimana cara cleanup old execution logs?

A: Buat job baru dengan schedule mingguan/bulanan yang memanggil `job_execution_repo.cleanup_old_logs(days=30)`.

---

## Support

Untuk pertanyaan atau issue terkait scheduler framework:
1. Check dokumentasi ini
2. Review existing job implementations
3. Check execution logs di database
4. Konsultasi dengan team lead

---

**Dokumentasi ini adalah single source of truth untuk scheduler framework.**
