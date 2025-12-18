# HRIS Refactoring Guidelines

## Objective
Refactor the `arga-hris-backend` modules to follow the **Single Use Case** pattern with a **Service Facade**. This ensures separation of concern, better testability, and a consistent architecture across the application.

## Architectural Pattern

### 1. Use Cases (`use_cases/`)
*   **Purpose**: Encapsulate pure business logic for a single specific action.
*   **Naming**: `VerbNounUseCase` (e.g., `CreateEmployeeUseCase`, `ListOrgUnitsUseCase`).
*   **Structure**:
    *   Located in `app/modules/<module>/use_cases/`.
    *   Class-based with an `execute` method.
    *   Dependencies (Repositories, EventPublisher) injected via `__init__`.
    *   Return Pydantic models or ORM models (Facade handles mapping if needed).
*   **Rules**:
    *   One file per major use case (or group related small ones like `Get` and `List` if simple).
    *   NO direct database session management if possible (delegate to Repositories).
    *   Handle business validation and exceptions (`BadRequestException`, `NotFoundException`).

### 2. Service Facade (`services/`)
*   **Purpose**: Orchestrate Use Cases and provide a single entry point for Routers and gRPC Handlers.
*   **Naming**: `<Module>Service` (e.g., `EmployeeService`).
*   **Structure**:
    *   Located in `app/modules/<module>/services/`.
    *   Initializes all Use Cases in `__init__`.
    *   Methods delegate directly to `self.use_case.execute()`.
    *   Can handle final DTO mappings (e.g., `OrgUnitResponse.from_orm_with_head`) if not done in Use Case.
*   **Rules**:
    *   Avoid complex logic in the Service itself (move to Use Case).
    *   Keep backward compatibility with existing method signatures where possible to minimize Router changes.

### 3. Repositories
*   **Queries**: Read-only operations.
*   **Commands**: Write operations.
*   Injected into Use Cases via the Service Facade.

## Refactoring Checklist (Per Module)

1.  **Preparation**
    *   [ ] Analyze existing Service logic.
    *   [ ] Create `app/modules/<module>/use_cases/` directory.

2.  **Implementation**
    *   [ ] Create Use Case classes for each public method in the Service.
    *   [ ] Move logic from Service to Use Case.
    *   [ ] Ensure `PaginatedResponse` is imported from `app.core.schemas` (avoid circular imports).

3.  **Facade Construction**
    *   [ ] Rewrite `<Module>Service` to accept dependencies and initialize Use Cases.
    *   [ ] Replace method bodies with calls to Use Cases.

4.  **Wiring**
    *   [ ] Update `app/modules/<module>/dependencies.py` to construct the new Facade.
    *   [ ] Update `app/modules/<module>/routers/<router>.py` to use the Facade.
    *   [ ] Update `app/grpc/handlers/<handler>.py` to use the Facade (ensure all dependencies including other module repositories are injected).

## Progress Status

| Module | Status | Notes |
| :--- | :--- | :--- |
| **Employees** | ✅ Complete | Reference implementation. |
| **Org Units** | ✅ Complete | Reference implementation. |
| **Attendance** | ⏳ Pending | Next up. |
| **Leave Requests** | ⏳ Pending | |
| **Work Submissions** | ⏳ Pending | |

## Common Issues & Solutions
*   **Circular Imports**: Keep imports clean. Use `TYPE_CHECKING` for type hints if needed.
*   **Missing Dependencies**: gRPC handlers often manually construct the Service. Ensure new dependencies (like `EmployeeCommands` in `OrgUnitService`) are added to the gRPC handler's `_get_service` method.
*   **Schema Imports**: `PaginatedResponse` should come from `app.core.schemas`.
