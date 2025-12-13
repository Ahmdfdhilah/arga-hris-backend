"""
Employee Service - Business logic for Employee operations

Uses local repository for master data.
"""

from typing import Optional, List, Tuple, Dict, Any
from app.modules.employees.models.employee import Employee
from app.modules.employees.repositories.employee_repository import (
    EmployeeRepository,
    EmployeeFilters,
    PaginationParams,
)
from app.modules.org_units.repositories.org_unit_repository import OrgUnitRepository
from app.modules.employees.schemas.responses import EmployeeResponse
from app.modules.users.users.repositories.user_repository import UserRepository
from app.core.exceptions import NotFoundException, ConflictException, BadRequestException


class EmployeeService:
    """Service for employee business logic using local repository"""
    
    def __init__(
        self,
        employee_repo: EmployeeRepository,
        org_unit_repo: OrgUnitRepository,
        user_repo: Optional[UserRepository] = None
    ):
        self.employee_repo = employee_repo
        self.org_unit_repo = org_unit_repo
        self.user_repo = user_repo

    async def get_employee(self, employee_id: int) -> EmployeeResponse:
        """Get employee by ID"""
        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee:
            raise NotFoundException(f"Employee with ID {employee_id} not found")
        
        return EmployeeResponse.model_validate(employee)

    async def get_employee_by_email(self, email: str) -> Optional[EmployeeResponse]:
        """Get employee by email"""
        employee = await self.employee_repo.get_by_email(email)
        if not employee:
            return None
        
        return EmployeeResponse.model_validate(employee)

    async def get_employee_by_number(self, number: str) -> Optional[EmployeeResponse]:
        """Get employee by employee number"""
        employee = await self.employee_repo.get_by_number(number)
        if not employee:
            return None
        
        return EmployeeResponse.model_validate(employee)

    async def list_employees(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        org_unit_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        include_details: Optional[bool] = True
    ) -> Tuple[List[EmployeeResponse], Dict[str, Any]]:
        """List employees with filters and pagination"""
        params = PaginationParams(page=page, limit=limit)
        filters = EmployeeFilters(
            org_unit_id=org_unit_id,
            is_active=is_active,
            search=search
        )
        
        employees, pagination = await self.employee_repo.list(params, filters, include_details or True)
        
        items = [EmployeeResponse.model_validate(emp) for emp in employees]
        return items, pagination.to_dict()

    async def get_employee_subordinates(
        self,
        employee_id: int,
        page: int = 1,
        limit: int = 10,
        recursive: bool = False
    ) -> Tuple[List[EmployeeResponse], Dict[str, Any]]:
        """Get employee subordinates"""
        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee:
            raise NotFoundException(f"Employee with ID {employee_id} not found")
        
        params = PaginationParams(page=page, limit=limit)
        employees, pagination = await self.employee_repo.get_subordinates(employee_id, recursive, params)
        
        items = [EmployeeResponse.model_validate(emp) for emp in employees]
        return items, pagination.to_dict()

    async def get_employees_by_org_unit(
        self,
        org_unit_id: int,
        page: int = 1,
        limit: int = 10,
        include_children: bool = False
    ) -> Tuple[List[EmployeeResponse], Dict[str, Any]]:
        """Get employees by organization unit"""
        org_unit = await self.org_unit_repo.get_by_id(org_unit_id)
        if not org_unit:
            raise NotFoundException(f"OrgUnit with ID {org_unit_id} not found")
        
        params = PaginationParams(page=page, limit=limit)
        employees, pagination = await self.employee_repo.get_by_org_unit(org_unit_id, include_children, params)
        
        items = [EmployeeResponse.model_validate(emp) for emp in employees]
        return items, pagination.to_dict()

    async def _auto_assign_supervisor(self, org_unit_id: int) -> Optional[int]:
        """Auto-assign supervisor based on org unit head hierarchy"""
        org_unit = await self.org_unit_repo.get_by_id(org_unit_id)
        if not org_unit:
            return None
        
        # Use org unit head as supervisor
        if org_unit.head_id:
            return org_unit.head_id
        
        # If no head, try parent unit head
        if org_unit.parent_id:
            parent = await self.org_unit_repo.get_by_id(org_unit.parent_id)
            if parent and parent.head_id:
                return parent.head_id
        
        return None

    async def create_employee(
        self,
        number: str,
        name: str,
        email: str,
        phone: Optional[str],
        position: Optional[str],
        org_unit_id: Optional[int],
        created_by: int,
        supervisor_id: Optional[int] = None,
        employee_type: Optional[str] = None,
        employee_gender: Optional[str] = None,
    ) -> EmployeeResponse:
        """Create new employee"""
        # Check if number already exists
        existing = await self.employee_repo.get_by_number(number)
        if existing:
            raise ConflictException(f"Employee number '{number}' already exists")
        
        # Check if email already exists
        if email:
            existing_email = await self.employee_repo.get_by_email(email)
            if existing_email:
                raise ConflictException(f"Employee email '{email}' already exists")
        
        # Validate org unit
        if org_unit_id:
            org_unit = await self.org_unit_repo.get_by_id(org_unit_id)
            if not org_unit:
                raise BadRequestException(f"Organization unit with ID {org_unit_id} not found")
        
        # Validate or auto-assign supervisor
        if supervisor_id:
            sup = await self.employee_repo.get_by_id(supervisor_id)
            if not sup:
                raise BadRequestException(f"Supervisor with ID {supervisor_id} not found")
        elif org_unit_id:
            # Auto-assign supervisor based on org unit
            supervisor_id = await self._auto_assign_supervisor(org_unit_id)
        
        # Create employee
        employee = Employee(
            number=number,
            name=name,
            email=email,
            phone=phone,
            position=position,
            employee_type=employee_type,
            employee_gender=employee_gender,
            org_unit_id=org_unit_id,
            supervisor_id=supervisor_id,
            is_active=True
        )
        employee.set_created_by(created_by)
        
        created = await self.employee_repo.create(employee)
        
        # Reload with relationships
        created = await self.employee_repo.get_by_id(created.id)
        return EmployeeResponse.model_validate(created)

    async def update_employee(
        self,
        employee_id: int,
        updated_by: int,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        position: Optional[str] = None,
        employee_type: Optional[str] = None,
        employee_gender: Optional[str] = None,
        org_unit_id: Optional[int] = None,
        supervisor_id: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> EmployeeResponse:
        """Update employee"""
        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee:
            raise NotFoundException(f"Employee with ID {employee_id} not found")
        
        # Check email uniqueness if changed
        if email and email != employee.email:
            existing = await self.employee_repo.get_by_email(email)
            if existing and existing.id != employee_id:
                raise ConflictException(f"Employee email '{email}' already exists")
        
        # Track if org unit changed
        old_org_unit_id = employee.org_unit_id
        new_org_unit_id = org_unit_id if org_unit_id is not None else old_org_unit_id
        org_unit_changed = new_org_unit_id != old_org_unit_id
        
        # Validate new org unit
        if org_unit_id is not None:
            org_unit = await self.org_unit_repo.get_by_id(org_unit_id)
            if not org_unit:
                raise BadRequestException(f"Organization unit with ID {org_unit_id} not found")
        
        # Handle supervisor assignment
        new_supervisor_id = supervisor_id
        if supervisor_id is not None:
            if supervisor_id == employee_id:
                raise BadRequestException("Employee cannot be their own supervisor")
            
            sup = await self.employee_repo.get_by_id(supervisor_id)
            if not sup:
                raise BadRequestException(f"Supervisor with ID {supervisor_id} not found")
        elif org_unit_changed and new_org_unit_id:
            # Auto-assign supervisor when org unit changes
            new_supervisor_id = await self._auto_assign_supervisor(new_org_unit_id)
        
        # Update fields
        if name is not None:
            employee.name = name
        if email is not None:
            employee.email = email
        if phone is not None:
            employee.phone = phone
        if position is not None:
            employee.position = position
        if employee_type is not None:
            employee.employee_type = employee_type
        if employee_gender is not None:
            employee.employee_gender = employee_gender
        if org_unit_id is not None:
            employee.org_unit_id = org_unit_id
        if new_supervisor_id is not None or (org_unit_changed and supervisor_id is None):
            employee.supervisor_id = new_supervisor_id
        if is_active is not None:
            employee.is_active = is_active
        
        employee.set_updated_by(updated_by)
        
        await self.employee_repo.update(employee)
        
        # Reload with relationships
        updated = await self.employee_repo.get_by_id(employee_id)
        return EmployeeResponse.model_validate(updated)

    async def soft_delete_employee(
        self,
        employee_id: int,
        deleted_by_user_id: int
    ) -> EmployeeResponse:
        """Soft delete employee with auto-reassignment of subordinates"""
        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee:
            raise NotFoundException(f"Employee with ID {employee_id} not found")
        
        if employee.is_deleted():
            raise BadRequestException("Employee is already deleted")
        
        # Check if employee is org unit head
        is_head = await self.org_unit_repo.is_head_of_any_unit(employee_id)
        if is_head:
            raise BadRequestException(
                "Cannot delete employee: employee is org unit head. "
                "Reassign unit head first"
            )
        
        # Auto-reassign subordinates to this employee's supervisor
        subordinates = await self.employee_repo.get_all_by_supervisor(employee_id)
        if subordinates:
            subordinate_ids = [s.id for s in subordinates]
            await self.employee_repo.bulk_update_supervisor(
                subordinate_ids,
                employee.supervisor_id,
                deleted_by_user_id
            )
        
        # Soft delete
        await self.employee_repo.delete(employee_id, deleted_by_user_id)
        
        # Get updated employee
        deleted_emp = await self.employee_repo.get_by_id_with_deleted(employee_id)
        return EmployeeResponse.model_validate(deleted_emp)

    async def restore_employee(self, employee_id: int) -> EmployeeResponse:
        """Restore soft-deleted employee"""
        employee = await self.employee_repo.get_by_id_with_deleted(employee_id)
        if not employee:
            raise NotFoundException(f"Employee with ID {employee_id} not found")
        
        if not employee.is_deleted():
            raise BadRequestException("Employee is not deleted")
        
        restored = await self.employee_repo.restore(employee_id)
        return EmployeeResponse.model_validate(restored)

    async def list_deleted_employees(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None
    ) -> Tuple[List[EmployeeResponse], Dict[str, Any]]:
        """List soft-deleted employees"""
        params = PaginationParams(page=page, limit=limit)
        employees, pagination = await self.employee_repo.list_deleted(params, search)
        
        items = [EmployeeResponse.model_validate(emp) for emp in employees]
        return items, pagination.to_dict()
