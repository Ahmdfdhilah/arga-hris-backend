from typing import Optional, List, Tuple, Dict, Any
import logging

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
from app.core.messaging.event_publisher import EventPublisher

from app.modules.org_units.use_cases.create_org_unit import CreateOrgUnitUseCase
from app.modules.org_units.use_cases.update_org_unit import UpdateOrgUnitUseCase
from app.modules.org_units.use_cases.delete_org_unit import DeleteOrgUnitUseCase
from app.modules.org_units.use_cases.restore_org_unit import RestoreOrgUnitUseCase
from app.modules.org_units.use_cases.get_org_unit import (
    GetOrgUnitUseCase,
    GetOrgUnitByCodeUseCase,
)
from app.modules.org_units.use_cases.list_org_units import (
    ListOrgUnitsUseCase,
    ListDeletedOrgUnitsUseCase,
    GetOrgUnitChildrenUseCase,
    GetOrgUnitTypesUseCase,
)
from app.modules.org_units.use_cases.bulk_insert_org_units import (
    BulkInsertOrgUnitsUseCase,
)

logger = logging.getLogger(__name__)


class OrgUnitService:
    """Facade Service for OrgUnit Use Cases"""

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

        # Initialize Use Cases
        self.create_uc = CreateOrgUnitUseCase(
            queries, commands, employee_queries, event_publisher
        )
        self.update_uc = UpdateOrgUnitUseCase(
            queries, commands, employee_queries, employee_commands, event_publisher
        )
        self.delete_uc = DeleteOrgUnitUseCase(queries, commands, event_publisher)
        self.restore_uc = RestoreOrgUnitUseCase(queries, commands, event_publisher)
        self.get_uc = GetOrgUnitUseCase(queries)
        self.get_by_code_uc = GetOrgUnitByCodeUseCase(queries)
        self.list_uc = ListOrgUnitsUseCase(queries)
        self.list_deleted_uc = ListDeletedOrgUnitsUseCase(queries)
        self.get_children_uc = GetOrgUnitChildrenUseCase(queries)
        self.get_types_uc = GetOrgUnitTypesUseCase(queries)
        self.bulk_insert_uc = BulkInsertOrgUnitsUseCase(
            queries, commands, employee_queries, event_publisher
        )

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
        org_unit = await self.create_uc.execute(
            code=code,
            name=name,
            type=type,
            created_by=created_by,
            parent_id=parent_id,
            head_id=head_id,
            description=description,
        )
        return OrgUnitResponse.from_orm_with_head(org_unit)

    async def update_org_unit(
        self,
        org_unit_id: int,
        updated_by: str,
        update_data: Dict[str, Any],
    ) -> OrgUnitResponse:
        org_unit = await self.update_uc.execute(org_unit_id, updated_by, update_data)
        return OrgUnitResponse.from_orm_with_head(org_unit)

    async def get_org_unit(self, org_unit_id: int) -> OrgUnitResponse:
        org_unit = await self.get_uc.execute(org_unit_id)
        return OrgUnitResponse.from_orm_with_head(org_unit)

    async def get_org_unit_by_code(self, code: str) -> Optional[OrgUnitResponse]:
        org_unit = await self.get_by_code_uc.execute(code)
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
        org_units, total = await self.list_uc.execute(
            page, limit, search, parent_id, type_filter
        )
        items = [OrgUnitResponse.from_orm_with_head(ou) for ou in org_units]
        pagination = {"page": page, "limit": limit, "total_items": total}
        return items, pagination

    async def get_org_unit_children(
        self, org_unit_id: int, page: int = 1, limit: int = 10
    ) -> Tuple[List[OrgUnitResponse], Dict[str, Any]]:
        org_units, total = await self.get_children_uc.execute(org_unit_id, page, limit)
        items = [OrgUnitResponse.from_orm_with_head(ou) for ou in org_units]
        pagination = {"page": page, "limit": limit, "total_items": total}
        return items, pagination

    async def get_org_unit_hierarchy(
        self, org_unit_id: Optional[int] = None
    ) -> OrgUnitHierarchyResponse:

        # Reuse existing logic via queries directly available here.
        tree = await self.queries.get_tree(org_unit_id, max_depth=10)

        root = None
        if org_unit_id:
            root_unit = await self.queries.get_by_id(org_unit_id)
            if root_unit:
                root = OrgUnitResponse.from_orm_with_head(root_unit)

        hierarchy = self._build_hierarchy(tree, org_unit_id)
        return OrgUnitHierarchyResponse(root=root, hierarchy=hierarchy)

    def _build_hierarchy(
        self, units: List[Any], parent_id: Optional[int] = None
    ) -> List[OrgUnitHierarchyItem]:
        result = []
        for unit in units:
            if unit.parent_id == parent_id:
                children = self._build_hierarchy(units, unit.id)
                item = OrgUnitHierarchyItem(
                    org_unit=OrgUnitResponse.from_orm_with_head(unit), children=children
                )
                result.append(item)
        return result

    async def get_org_unit_types(self) -> OrgUnitTypesResponse:
        types = await self.get_types_uc.execute()
        return OrgUnitTypesResponse(types=types)

    async def soft_delete_org_unit(
        self, org_unit_id: int, deleted_by_user_id: str
    ) -> OrgUnitResponse:
    

        # Execute Delete
        await self.delete_uc.execute(org_unit_id, deleted_by_user_id)

        # Fetch result
        deleted_ou = await self.queries.get_by_id_with_deleted(org_unit_id)
        return OrgUnitResponse.from_orm_with_head(deleted_ou)

    async def restore_org_unit(self, org_unit_id: int) -> OrgUnitResponse:
        restored = await self.restore_uc.execute(org_unit_id)
        return OrgUnitResponse.from_orm_with_head(restored)

    async def list_deleted_org_units(
        self, page: int = 1, limit: int = 10, search: Optional[str] = None
    ) -> Tuple[List[OrgUnitResponse], Dict[str, Any]]:
        org_units, total = await self.list_deleted_uc.execute(page, limit, search)
        items = [OrgUnitResponse.from_orm_with_head(ou) for ou in org_units]
        pagination = {"page": page, "limit": limit, "total_items": total}
        return items, pagination

    async def bulk_insert_org_units(
        self, items: List[OrgUnitBulkItem], created_by: str, skip_errors: bool = False
    ) -> BulkInsertResult:
        result = await self.bulk_insert_uc.execute(items, created_by, skip_errors)
        return result
