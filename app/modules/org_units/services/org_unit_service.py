"""
OrgUnit Service - Business logic for Organization Unit operations
"""

from typing import Optional, List, Tuple, Dict, Any
import logging

from app.modules.org_units.models.org_unit import OrgUnit
from app.modules.org_units.repositories import OrgUnitQueries, OrgUnitCommands
from app.modules.employees.repositories import EmployeeQueries, EmployeeCommands
from app.modules.org_units.schemas.responses import (
    OrgUnitResponse,
    OrgUnitTypesResponse,
    OrgUnitHierarchyResponse,
    OrgUnitHierarchyItem,
    BulkInsertResult,
)
from app.modules.org_units.schemas.requests import OrgUnitBulkItem
from app.core.exceptions import (
    NotFoundException,
    ConflictException,
    BadRequestException,
)
from app.core.messaging.event_publisher import EventPublisher

logger = logging.getLogger(__name__)


class OrgUnitService:
    """Service for org unit business logic"""

    def __init__(
        self,
        queries: OrgUnitQueries,
        commands: OrgUnitCommands,
        employee_queries: Optional[EmployeeQueries] = None,
        employee_commands: Optional[EmployeeCommands] = None,
        event_publisher: Optional[EventPublisher] = None,
    ):
        self.queries = queries
        self.commands = commands
        self.employee_queries = employee_queries
        self.employee_commands = employee_commands
        self.event_publisher = event_publisher

    def _org_unit_to_event_data(self, org_unit: OrgUnit) -> Dict[str, Any]:
        """Convert org unit to event data dict"""
        return {
            "id": org_unit.id,
            "code": org_unit.code,
            "name": org_unit.name,
            "type": org_unit.type,
            "parent_id": org_unit.parent_id,
            "head_id": org_unit.head_id,
            "level": org_unit.level,
            "path": org_unit.path,
            "is_active": org_unit.is_active,
        }

    async def _publish_event(self, event_type: str, org_unit: OrgUnit) -> None:
        """Publish org unit event if publisher available"""
        if not self.event_publisher:
            return

        try:
            data = self._org_unit_to_event_data(org_unit)
            if event_type == "created":
                await self.event_publisher.publish_org_unit_created(org_unit.id, data)
            elif event_type == "updated":
                await self.event_publisher.publish_org_unit_updated(org_unit.id, data)
            elif event_type == "deleted":
                await self.event_publisher.publish_org_unit_deleted(org_unit.id, data)
        except Exception as e:
            logger.warning(f"Failed to publish org_unit.{event_type} event: {e}")

    async def get_org_unit(self, org_unit_id: int) -> OrgUnitResponse:
        """Get organization unit by ID"""
        org_unit = await self.queries.get_by_id(org_unit_id)
        if not org_unit:
            raise NotFoundException(
                f"Organization unit with ID {org_unit_id} not found"
            )

        return OrgUnitResponse.from_orm_with_head(org_unit)

    async def get_org_unit_by_code(self, code: str) -> Optional[OrgUnitResponse]:
        """Get organization unit by code"""
        org_unit = await self.queries.get_by_code(code)
        if not org_unit:
            return None

        return OrgUnitResponse.from_orm_with_head(org_unit)

    async def list_org_units(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        parent_id: Optional[int] = None,
        type_filter: Optional[str] = None,
    ) -> Tuple[List[OrgUnitResponse], Dict[str, Any]]:
        """List organization units with filters and pagination"""
        skip = (page - 1) * limit

        org_units = await self.queries.list(
            parent_id=parent_id,
            type_filter=type_filter,
            search=search,
            skip=skip,
            limit=limit,
        )
        total = await self.queries.count(
            parent_id=parent_id,
            type_filter=type_filter,
            search=search,
        )

        items = [OrgUnitResponse.from_orm_with_head(ou) for ou in org_units]
        pagination = {"page": page, "limit": limit, "total_items": total}
        return items, pagination

    async def get_org_unit_children(
        self, org_unit_id: int, page: int = 1, limit: int = 10
    ) -> Tuple[List[OrgUnitResponse], Dict[str, Any]]:
        """Get children organization units"""
        skip = (page - 1) * limit

        org_units = await self.queries.get_children(
            parent_id=org_unit_id,
            recursive=False,
            skip=skip,
            limit=limit,
        )
        total = await self.queries.count_children(org_unit_id, recursive=False)

        items = [OrgUnitResponse.from_orm_with_head(ou) for ou in org_units]
        pagination = {"page": page, "limit": limit, "total_items": total}
        return items, pagination

    async def get_org_unit_hierarchy(
        self, org_unit_id: Optional[int] = None
    ) -> OrgUnitHierarchyResponse:
        """Get organization unit hierarchy as tree"""
        tree = await self.queries.get_tree(org_unit_id, max_depth=10)

        root = None
        if org_unit_id:
            root_unit = await self.queries.get_by_id(org_unit_id)
            if root_unit:
                root = OrgUnitResponse.from_orm_with_head(root_unit)

        hierarchy = self._build_hierarchy(tree, org_unit_id)
        return OrgUnitHierarchyResponse(root=root, hierarchy=hierarchy)

    def _build_hierarchy(
        self, units: List[OrgUnit], parent_id: Optional[int] = None
    ) -> List[OrgUnitHierarchyItem]:
        """Build hierarchical tree structure from flat list"""
        result = []

        for unit in units:
            if unit.parent_id == parent_id:
                children = self._build_hierarchy(units, unit.id)
                item = OrgUnitHierarchyItem(
                    org_unit=OrgUnitResponse.from_orm_with_head(unit), children=children
                )
                result.append(item)

        return result

    async def _resolve_supervisor_for_unit(
        self, org_unit_id: int, exclude_employee_id: Optional[int] = None
    ) -> Optional[int]:
        """
        Internal helper to resolve effective supervisor for a unit.
        Simulates the upstream lookup.
        If exclude_employee_id is provided, it skips that employee if found as head.
        """
        current_unit = await self.queries.get_by_id(org_unit_id)
        while current_unit:
            logger.info(
                f"Resolving sup for Unit {org_unit_id}. Checking Unit {current_unit.id}. Head: {current_unit.head_id}. Exclude: {exclude_employee_id}"
            )
            if current_unit.head_id:
                if (
                    exclude_employee_id is None
                    or current_unit.head_id != exclude_employee_id
                ):
                    return current_unit.head_id
                else:
                    logger.info("Skipping head because matches exclude_employee_id")

            if not current_unit.parent_id:
                break
            current_unit = await self.queries.get_by_id(current_unit.parent_id)
        return None

    async def _handle_head_change(
        self,
        org_unit_id: int,
        old_head_id: Optional[int],
        new_head_id: Optional[int],
        updated_by: str,
    ) -> None:
        """
        Handle Org Unit Head change:
        - If Head changed, update direct subordinates' supervisor_id.
        - If Head cleared, resolve effective supervisor (from parent).
        - Propagate to child Org Units that do not have their own Head (inherit).
        """
        # 1. Resolve who the supervisor should be for this unit (Generic)
        effective_supervisor_id = new_head_id
        if not effective_supervisor_id:
            # If head was cleared, look upstream
            effective_supervisor_id = await self._resolve_supervisor_for_unit(
                org_unit_id
            )

        # 2. Update Direct Members of this Unit
        members = await self.employee_queries.list(org_unit_id=org_unit_id, limit=1000)
        logger.info(
            f"Updating {len(members)} members for OrgUnit {org_unit_id}. Effective Sup: {effective_supervisor_id}"
        )

        for emp in members:
            target_sup = effective_supervisor_id

            # If the resolved supervisor is the employee themselves, look up further
            if target_sup == emp.id:
                logger.info(
                    f"Employee {emp.id} is the generic supervisor. Re-resolving excluding self."
                )
                # Re-resolve excluding self
                target_sup = await self._resolve_supervisor_for_unit(
                    org_unit_id, exclude_employee_id=emp.id
                )
                logger.info(f"Re-resolved supervisor for {emp.id}: {target_sup}")

            if emp.supervisor_id != target_sup:
                logger.info(
                    f"Updating Employee {emp.id}: supervisor {emp.supervisor_id} -> {target_sup}"
                )
                emp.supervisor_id = target_sup
                emp.set_updated_by(updated_by)
                await self.employee_commands.update(emp)

        # 3. Propagate to Child Units
        children = await self.queries.get_children(org_unit_id, recursive=False)
        for child in children:
            # Only propagate if child unit does NOT have its own head
            # If it has a head, that head blocks inheritance (it's a new supervisor node)
            if not child.head_id:
                await self._handle_head_change(child.id, None, None, updated_by)

    async def create_org_unit(
        self,
        code: str,
        name: str,
        type: str,
        created_by: str,
        parent_id: Optional[int] = None,
        head_id: Optional[int] = None,
        description: Optional[str] = None,
    ) -> OrgUnitResponse:
        """Create new organization unit"""
        # Check if code already exists
        existing = await self.queries.get_by_code(code)
        if existing:
            raise ConflictException(f"Organization unit code '{code}' already exists")

        # Calculate level and path based on parent
        level = 1
        path = "0"  # Temporary, will be updated after insert

        if parent_id:
            parent = await self.queries.get_by_id(parent_id)
            if not parent:
                raise BadRequestException(
                    f"Parent organization unit with ID {parent_id} not found"
                )
            level = parent.level + 1

        # Check if head exists if provided
        if head_id and self.employee_queries:
            head = await self.employee_queries.get_by_id(head_id)
            if not head:
                raise BadRequestException(f"Head employee with ID {head_id} not found")

        # Create org unit
        org_unit = OrgUnit(
            code=code,
            name=name,
            type=type,
            parent_id=parent_id,
            level=level,
            path=path,
            head_id=head_id,
            description=description,
            is_active=True,
        )
        org_unit.set_created_by(created_by)

        created = await self.commands.create(org_unit)

        # Update path with actual ID
        if parent_id:
            parent = await self.queries.get_by_id(parent_id)
            created.path = f"{parent.path}.{created.id}"
        else:
            created.path = str(created.id)

        await self.commands.update(created)

        # Reload with relationships
        created = await self.queries.get_by_id(created.id)

        # Publish event
        await self._publish_event("created", created)

        # Trigger head change logic to set initial supervisors?
        # Likely not needed for CREATE unless we want to "steal" employees into this unit immediately?
        # Assuming new unit is empty, so no subordinates to update.

        return OrgUnitResponse.from_orm_with_head(created)

    async def update_org_unit(
        self,
        org_unit_id: int,
        updated_by: str,
        update_data: Dict[str, Any],
    ) -> OrgUnitResponse:
        """Update organization unit"""
        org_unit = await self.queries.get_by_id(org_unit_id)
        if not org_unit:
            raise NotFoundException(
                f"Organization unit with ID {org_unit_id} not found"
            )

        old_head_id = org_unit.head_id
        parent_changed = False

        # Validate parent change
        if "parent_id" in update_data:
            parent_id = update_data["parent_id"]
            if parent_id != org_unit.parent_id:
                if parent_id is not None and parent_id == org_unit_id:
                    raise BadRequestException(
                        "Organization unit cannot be its own parent"
                    )

                if parent_id is not None:
                    parent = await self.queries.get_by_id(parent_id)
                    if not parent:
                        raise BadRequestException(
                            f"Parent organization unit with ID {parent_id} not found"
                        )

                    # Check for circular hierarchy
                    if parent.path and str(org_unit_id) in parent.path.split("."):
                        raise BadRequestException("Circular hierarchy detected")

                parent_changed = True

        # Check head existence
        if "head_id" in update_data:
            head_id = update_data["head_id"]
            if head_id is not None and self.employee_queries:
                head = await self.employee_queries.get_by_id(head_id)
                if not head:
                    raise BadRequestException(
                        f"Head employee with ID {head_id} not found"
                    )

        # Update fields
        if "name" in update_data:
            org_unit.name = update_data["name"]
        if "type" in update_data:
            org_unit.type = update_data["type"]
        if "parent_id" in update_data:
            org_unit.parent_id = update_data["parent_id"]
        if "head_id" in update_data:
            org_unit.head_id = update_data["head_id"]
        if "description" in update_data:
            org_unit.description = update_data["description"]
        if "is_active" in update_data:
            org_unit.is_active = update_data["is_active"]

        org_unit.set_updated_by(updated_by)

        await self.commands.update(org_unit)

        # Handle head change - update supervisor relationships
        # We also trigger this if parent_id changed? (Since effective supervisor might come from parent)
        # Yes! Changing parent connects us to a new hierarchy.
        if "head_id" in update_data or parent_changed:
            new_head_id = org_unit.head_id  # Could be None
            await self._handle_head_change(
                org_unit_id, old_head_id, new_head_id, updated_by
            )

        # Recalculate path if parent changed
        if parent_changed:
            await self._recalculate_path(org_unit)

        # Reload with relationships
        updated = await self.queries.get_by_id(org_unit_id)

        # Publish event
        await self._publish_event("updated", updated)

        return OrgUnitResponse.from_orm_with_head(updated)

    async def _recalculate_path(self, org_unit: OrgUnit) -> None:
        """Recalculate path for org unit and all descendants"""
        if org_unit.parent_id:
            parent = await self.queries.get_by_id(org_unit.parent_id)
            if parent:
                old_path = org_unit.path
                org_unit.path = f"{parent.path}.{org_unit.id}"
                org_unit.level = parent.level + 1
                await self.commands.update(org_unit)

                # Update all descendants
                children = await self.queries.get_children(
                    org_unit.id, recursive=True, skip=0, limit=1000
                )
                for child in children:
                    child.path = child.path.replace(old_path, org_unit.path, 1)
                    parts = child.path.split(".")
                    child.level = len(parts)
                    await self.commands.update(child)
        else:
            org_unit.path = str(org_unit.id)
            org_unit.level = 1
            await self.commands.update(org_unit)

    async def get_org_unit_types(self) -> OrgUnitTypesResponse:
        """Get all available org unit types"""
        types = await self.queries.get_unique_types()
        return OrgUnitTypesResponse(types=types)

    async def soft_delete_org_unit(
        self, org_unit_id: int, deleted_by_user_id: str
    ) -> OrgUnitResponse:
        """Soft delete organization unit with validation"""
        org_unit = await self.queries.get_by_id(org_unit_id)
        if not org_unit:
            raise NotFoundException(
                f"Organization unit with ID {org_unit_id} not found"
            )

        if org_unit.is_deleted():
            raise BadRequestException("Organization unit is already deleted")

        # Check for active employees
        active_count = await self.queries.count_active_employees(org_unit_id)
        if active_count > 0:
            raise BadRequestException(
                f"Cannot delete org unit: has {active_count} active employees. "
                "Move or deactivate employees first"
            )

        # Check for child units
        child_count = await self.queries.count_active_children(org_unit_id)
        if child_count > 0:
            raise BadRequestException(
                f"Cannot delete org unit: has {child_count} child units. "
                "Delete or move child units first"
            )

        # Soft delete
        await self.commands.delete(org_unit_id, deleted_by_user_id)

        # Get updated org unit
        deleted_ou = await self.queries.get_by_id_with_deleted(org_unit_id)

        # Publish event
        await self._publish_event("deleted", deleted_ou)

        return OrgUnitResponse.from_orm_with_head(deleted_ou)

    async def restore_org_unit(self, org_unit_id: int) -> OrgUnitResponse:
        """Restore soft-deleted organization unit"""
        org_unit = await self.queries.get_by_id_with_deleted(org_unit_id)
        if not org_unit:
            raise NotFoundException(
                f"Organization unit with ID {org_unit_id} not found"
            )

        if not org_unit.is_deleted():
            raise BadRequestException("Organization unit is not deleted")

        # Check if parent is deleted
        if org_unit.parent_id:
            parent = await self.queries.get_by_id_with_deleted(org_unit.parent_id)
            if parent and parent.is_deleted():
                raise BadRequestException(
                    "Cannot restore: parent unit is still deleted"
                )

        restored = await self.commands.restore(org_unit_id)

        # Publish event (restored = updated)
        await self._publish_event("updated", restored)

        return OrgUnitResponse.from_orm_with_head(restored)

    async def list_deleted_org_units(
        self, page: int = 1, limit: int = 10, search: Optional[str] = None
    ) -> Tuple[List[OrgUnitResponse], Dict[str, Any]]:
        """List soft-deleted organization units"""
        skip = (page - 1) * limit

        org_units = await self.queries.list_deleted(
            search=search, skip=skip, limit=limit
        )
        total = await self.queries.count_deleted(search=search)

        items = [OrgUnitResponse.from_orm_with_head(ou) for ou in org_units]
        pagination = {"page": page, "limit": limit, "total_items": total}
        return items, pagination

    async def bulk_insert_org_units(
        self, items: List[OrgUnitBulkItem], created_by: str, skip_errors: bool = False
    ) -> BulkInsertResult:
        """Bulk insert org units from Excel data"""
        result = BulkInsertResult(
            total_items=len(items),
            success_count=0,
            error_count=0,
            errors=[],
            warnings=[],
            created_ids=[],
        )

        code_to_id_map = {}
        email_to_employee_map = {}

        # Resolve head emails to employee IDs
        if self.employee_queries:
            for item in items:
                if item.head_email and item.head_email not in email_to_employee_map:
                    try:
                        employee = await self.employee_queries.get_by_email(
                            item.head_email
                        )
                        if employee:
                            email_to_employee_map[item.head_email] = employee.id
                    except Exception:
                        pass

        # Phase 1: Insert root units
        root_items = [item for item in items if not item.parent_code]
        for item in root_items:
            try:
                existing = await self.get_org_unit_by_code(item.code)
                if existing:
                    result.error_count += 1
                    result.errors.append(
                        {
                            "row_number": item.row_number,
                            "code": item.code,
                            "error": f"Code '{item.code}' already exists",
                        }
                    )
                    continue

                head_id = None
                if item.head_email:
                    head_id = email_to_employee_map.get(item.head_email)
                    if not head_id:
                        result.warnings.append(
                            f"Head email '{item.head_email}' not found for {item.code}"
                        )

                created = await self.create_org_unit(
                    code=item.code,
                    name=item.name,
                    type=item.type,
                    created_by=created_by,
                    parent_id=None,
                    head_id=head_id,
                    description=item.description,
                )

                result.success_count += 1
                result.created_ids.append(created.id)
                code_to_id_map[item.code] = created.id

            except Exception as e:
                result.error_count += 1
                result.errors.append(
                    {"row_number": item.row_number, "code": item.code, "error": str(e)}
                )
                if not skip_errors:
                    break

        # Phase 2: Insert child units
        child_items = [item for item in items if item.parent_code]

        max_retries = 3
        for retry in range(max_retries):
            remaining_items = []

            for item in child_items:
                try:
                    existing = await self.get_org_unit_by_code(item.code)
                    if existing:
                        result.error_count += 1
                        result.errors.append(
                            {
                                "row_number": item.row_number,
                                "code": item.code,
                                "error": f"Code '{item.code}' already exists",
                            }
                        )
                        continue

                    parent_id = code_to_id_map.get(item.parent_code)
                    if not parent_id:
                        parent = await self.get_org_unit_by_code(item.parent_code)
                        if parent:
                            parent_id = parent.id
                            code_to_id_map[item.parent_code] = parent_id
                        else:
                            if retry < max_retries - 1:
                                remaining_items.append(item)
                                continue
                            else:
                                result.error_count += 1
                                result.errors.append(
                                    {
                                        "row_number": item.row_number,
                                        "code": item.code,
                                        "error": f"Parent code '{item.parent_code}' not found",
                                    }
                                )
                                continue

                    head_id = None
                    if item.head_email:
                        head_id = email_to_employee_map.get(item.head_email)
                        if not head_id:
                            result.warnings.append(
                                f"Head email '{item.head_email}' not found for {item.code}"
                            )

                    created = await self.create_org_unit(
                        code=item.code,
                        name=item.name,
                        type=item.type,
                        created_by=created_by,
                        parent_id=parent_id,
                        head_id=head_id,
                        description=item.description,
                    )

                    result.success_count += 1
                    result.created_ids.append(created.id)
                    code_to_id_map[item.code] = created.id

                except Exception as e:
                    result.error_count += 1
                    result.errors.append(
                        {
                            "row_number": item.row_number,
                            "code": item.code,
                            "error": str(e),
                        }
                    )
                    if not skip_errors:
                        break

            child_items = remaining_items
            if not child_items:
                break

        return result
