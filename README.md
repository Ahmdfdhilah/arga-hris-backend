# HRIS Service

HRIS (Human Resource Information System) service built with FastAPI, PostgreSQL, Redis, and gRPC integration with Workforce Service.

## Architecture

```
┌─────────────────┐
│   SSO Service   │
│  (Auth & Users) │
└────────┬────────┘
         │ JWT Token
         ↓
┌─────────────────┐      gRPC      ┌──────────────────┐
│  HRIS Service   │ ←──────────→  │ Workforce Service│
│  (HR Business)  │                │ (Employee & OrgU)│
└─────────────────┘                └──────────────────┘
         │
         ↓ PostgreSQL
┌─────────────────┐
│  HRIS Database  │
│ - Users         │
│ - Attendance    │
│ - Leave         │
│ - Payroll       │
└─────────────────┘
```

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (SQLAlchemy async)
- **Cache**: Redis
- **Auth**: JWT from SSO Service
- **gRPC Client**: Komunikasi dengan Workforce Service
- **ORM**: SQLAlchemy 2.0 (async)
- **Migration**: Alembic

## Features

- User management with SSO integration
- Employee data proxy via gRPC
- Organization Unit data proxy via gRPC
- JWT authentication
- Redis caching
- Async database operations
- Comprehensive error handling
- Request logging

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Workforce Service running (gRPC on port 50051)

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Generate gRPC Python code from proto files:
```bash
  python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. --mypy_out=. proto/**/*.proto
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Run the service:
```bash
uvicorn app.main:app --reload
```

## Docker Setup

### Using Docker Compose (Recommended)

```bash
docker-compose up -d
```

This will start:
- PostgreSQL on port 5433
- Redis on port 6380
- HRIS Service on port 8002

### Build Docker Image

```bash
docker build -t hris-service .
```

## API Endpoints

### Base URL
- Development: `http://localhost:8002`
- API Prefix: `/api/v1`

### Users Module

- `GET /api/v1/users/me` - Get current user with employee data
- `GET /api/v1/users/{id}` - Get user by ID
- `PUT /api/v1/users/{id}` - Update user
- `POST /api/v1/users/{id}/link-employee` - Link user to employee
- `POST /api/v1/users/{id}/link-employee-auto` - Auto-link by email
- `POST /api/v1/users/{id}/deactivate` - Deactivate user
- `POST /api/v1/users/{id}/activate` - Activate user

### Employees Module (gRPC Proxy)

- `GET /api/v1/employees/{id}` - Get employee details
- `GET /api/v1/employees` - List employees
- `GET /api/v1/employees/by-email/{email}` - Get by email
- `GET /api/v1/employees/by-number/{number}` - Get by employee number
- `GET /api/v1/employees/{id}/subordinates` - Get subordinates
- `GET /api/v1/employees/org-unit/{id}/employees` - Get employees in org unit

### Organization Units Module (gRPC Proxy)

- `GET /api/v1/org-units/{id}` - Get org unit details
- `GET /api/v1/org-units` - List org units
- `GET /api/v1/org-units/by-code/{code}` - Get by code
- `GET /api/v1/org-units/{id}/children` - Get child org units
- `GET /api/v1/org-units/{id}/hierarchy` - Get org unit hierarchy

## Authentication

All endpoints (except `/` and `/health`) require JWT authentication from SSO Service.

Add header:
```
Authorization: Bearer <jwt_token>
```

## Database Migrations

### Create new migration
```bash
alembic revision -m "description"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback migration
```bash
alembic downgrade -1
```

## Development

### Development Data Seeding

Seed development users with RBAC roles and employees:

```bash
# Make sure migrations are run first
alembic upgrade head

# Ensure Workforce service is running (gRPC port 50051)

# Run seeder script
python scripts/seed_dev_users.py
```

**Note:** Update `SSO_DB_URL` in `scripts/seed_dev_users.py` before running.

See `scripts/README.md` for details.

### RBAC Testing

Follow the comprehensive testing guide:
- `RBAC_TESTING_GUIDE.md` - Step-by-step permission testing
- `RBAC_IMPLEMENTATION_SUMMARY.md` - Implementation overview

### Run tests
```bash
pytest
```

### Code structure follows MODULAR_RULES.md

- Dependency injection pattern
- Repository pattern
- Service layer pattern
- No emoji in code
- Clear separation of concerns

## Integration Notes

### SSO Service Integration

- Users are auto-created on first login from SSO
- JWT tokens validated from SSO Service
- User `sso_id` maps to SSO user ID

### Workforce Service Integration

- Employee data fetched via gRPC
- `user.employee_id` is soft reference (not FK)
- Auto-linking by email on user creation
- Cache employee data in Redis for performance

## Troubleshooting

### gRPC Connection Issues

Ensure Workforce Service is running:
```bash
# Check if gRPC port is open
telnet localhost 50051
```

### Database Connection Issues

Check PostgreSQL connection:
```bash
psql -h localhost -p 5433 -U hris_user -d hris_db
```

### Redis Connection Issues

Check Redis:
```bash
redis-cli -p 6380 ping
```

## License

Proprietary - ARGA Web Backend
