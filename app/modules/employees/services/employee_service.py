"""
Employee Service - Business logic for Employee operations

Uses local repository for master data and publishes events to RabbitMQ.
Employee now links to User for profile data (name, email, phone, gender).
"""

from typing import Optional, List, Tuple, Dict, Any
import logging

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
from app.core.messaging.event_publisher import EventPublisher

logger = logging.getLogger(__name__)


class EmployeeService:
    """Service for employee business logic using local repository"""
    
    def __init__(
        self,
        employee_repo: EmployeeRepository,
        org_unit_repo: OrgUnitRepository,
        user_repo: Optional[UserRepository] = None,
        event_publisher: Optional[EventPublisher] = None,
    ):
        self.employee_repo = employee_repo
        self.org_unit_repo = org_unit_repo
        self.user_repo = user_repo
        self.event_publisher = event_publisher

    def _employee_to_event_data(self, employee: Employee) -> Dict[str, Any]:
        """Convert employee to event data dict"""
        data = {
            "id": employee.id,
            "user_id": employee.user_id,
            "number": employee.number,
            "position": employee.position,
            "type": employee.type,
            "org_unit_id": employee.org_unit_id,
            "supervisor_id": employee.supervisor_id,
            "is_active": employee.is_active,
        }
        # Include user profile data if loaded
        if employee.user:
            data["user"] = {
                "id": employee.user.id,
                "sso_id": employee.user.sso_id,
                "name": employee.user.name,
                "email": employee.user.email,
                "phone": employee.user.phone,
                "gender": employee.user.gender,
            }
        return data

    async def _publish_event(self, event_type: str, employee: Employee) -> None:
        """Publish employee event if publisher available"""
        if not self.event_publisher:
            return
        
        try:
            data = self._employee_to_event_data(employee)
            if event_type == "created":
                await self.event_publisher.publish_employee_created(employee.id, data)
            elif event_type == "updated":
                await self.event_publisher.publish_employee_updated(employee.id, data)
            elif event_type == "deleted":
                await self.event_publisher.publish_employee_deleted(employee.id, data)
        except Exception as e:
            logger.warning(f"Failed to publish employee.{event_type} event: {e}")

    async def get_employee(self, employee_id: int) -> EmployeeResponse:
        """Get employee by ID"""
        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee:
            raise NotFoundException(f"Employee with ID {employee_id} not found")
        
        return EmployeeResponse.model_validate(employee)

    async def get_employee_by_user_id(self, user_id: int) -> Optional[EmployeeResponse]:
        """Get employee by user ID"""
        employee = await self.employee_repo.get_by_user_id(user_id)
        if not employee:
            return None
        
        return EmployeeResponse.model_validate(employee)

    async def get_employee_by_email(self, email: str) -> Optional[EmployeeResponse]:
        """Get employee by email (via user)"""
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
        
        if org_unit.head_id:
            return org_unit.head_id
        
        if org_unit.parent_id:
            parent = await self.org_unit_repo.get_by_id(org_unit.parent_id)
            if parent and parent.head_id:
                return parent.head_id
        
        return None

    async def create_employee(
        self,
        user_id: int,
        number: str,
        position: Optional[str],
        org_unit_id: Optional[int],
        created_by: int,
        supervisor_id: Optional[int] = None,
        employee_type: Optional[str] = None,
    ) -> EmployeeResponse:
        """
        Create new employee linked to a user.
        
        User must already exist (created via SSO sync).
        Profile data (name, email, phone, gender) comes from User.
        """
        # Check if user exists
        if self.user_repo:
            user = await self.user_repo.get(user_id)
            if not user:
                raise BadRequestException(f"User with ID {user_id} not found")
        
        # Check if employee already exists for this user
        existing_user_emp = await self.employee_repo.get_by_user_id(user_id)
        if existing_user_emp:
            raise ConflictException(f"Employee already exists for user ID {user_id}")
        
        # Check if number already exists
        existing = await self.employee_repo.get_by_number(number)
        if existing:
            raise ConflictException(f"Employee number '{number}' already exists")
        
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
            supervisor_id = await self._auto_assign_supervisor(org_unit_id)
        
        # Create employee (linked to user)
        employee = Employee(
            user_id=user_id,
            number=number,
            position=position,
            type=employee_type,
            org_unit_id=org_unit_id,
            supervisor_id=supervisor_id,
            is_active=True
        )
        employee.set_created_by(created_by)
        
        created = await self.employee_repo.create(employee)
        created = await self.employee_repo.get_by_id(created.id)
        
        # Publish event
        await self._publish_event("created", created)
        
        return EmployeeResponse.model_validate(created)

    async def update_employee(
        self,
        employee_id: int,
        updated_by: int,
        position: Optional[str] = None,
        employee_type: Optional[str] = None,
        org_unit_id: Optional[int] = None,
        supervisor_id: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> EmployeeResponse:
        """
        Update employee employment data.
        
        Profile updates (name, email, phone, gender) should go through User/SSO.
        """
        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee:
            raise NotFoundException(f"Employee with ID {employee_id} not found")
        
        old_org_unit_id = employee.org_unit_id
        new_org_unit_id = org_unit_id if org_unit_id is not None else old_org_unit_id
        org_unit_changed = new_org_unit_id != old_org_unit_id
        
        if org_unit_id is not None:
            org_unit = await self.org_unit_repo.get_by_id(org_unit_id)
            if not org_unit:
                raise BadRequestException(f"Organization unit with ID {org_unit_id} not found")
        
        new_supervisor_id = supervisor_id
        if supervisor_id is not None:
            if supervisor_id == employee_id:
                raise BadRequestException("Employee cannot be their own supervisor")
            
            sup = await self.employee_repo.get_by_id(supervisor_id)
            if not sup:
                raise BadRequestException(f"Supervisor with ID {supervisor_id} not found")
        elif org_unit_changed and new_org_unit_id:
            new_supervisor_id = await self._auto_assign_supervisor(new_org_unit_id)
        
        # Update employment fields only
        if position is not None:
            employee.position = position
        if employee_type is not None:
            employee.type = employee_type
        if org_unit_id is not None:
            employee.org_unit_id = org_unit_id
        if new_supervisor_id is not None or (org_unit_changed and supervisor_id is None):
            employee.supervisor_id = new_supervisor_id
        if is_active is not None:
            employee.is_active = is_active
        
        employee.set_updated_by(updated_by)
        
        await self.employee_repo.update(employee)
        updated = await self.employee_repo.get_by_id(employee_id)
        
        # Publish event
        await self._publish_event("updated", updated)
        
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
        
        is_head = await self.org_unit_repo.is_head_of_any_unit(employee_id)
        if is_head:
            raise BadRequestException(
                "Cannot delete employee: employee is org unit head. "
                "Reassign unit head first"
            )
        
        subordinates = await self.employee_repo.get_all_by_supervisor(employee_id)
        if subordinates:
            subordinate_ids = [s.id for s in subordinates]
            await self.employee_repo.bulk_update_supervisor(
                subordinate_ids,
                employee.supervisor_id,
                deleted_by_user_id
            )
        
        await self.employee_repo.delete(employee_id, deleted_by_user_id)
        deleted_emp = await self.employee_repo.get_by_id_with_deleted(employee_id)
        
        # Publish event
        await self._publish_event("deleted", deleted_emp)
        
        return EmployeeResponse.model_validate(deleted_emp)

    async def restore_employee(self, employee_id: int) -> EmployeeResponse:
        """Restore soft-deleted employee"""
        employee = await self.employee_repo.get_by_id_with_deleted(employee_id)
        if not employee:
            raise NotFoundException(f"Employee with ID {employee_id} not found")
        
        if not employee.is_deleted():
            raise BadRequestException("Employee is not deleted")
        
        restored = await self.employee_repo.restore(employee_id)
        
        # Publish as updated (restored)
        await self._publish_event("updated", restored)
        
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
