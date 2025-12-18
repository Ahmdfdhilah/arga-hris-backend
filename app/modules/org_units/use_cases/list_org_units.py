from typing import Optional, List, Tuple
from app.modules.org_units.models.org_unit import OrgUnit
from app.modules.org_units.repositories import OrgUnitQueries


class ListOrgUnitsUseCase:
    def __init__(self, queries: OrgUnitQueries):
        self.queries = queries

    async def execute(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        parent_id: Optional[int] = None,
        type_filter: Optional[str] = None,
    ) -> Tuple[List[OrgUnit], int]:
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
        return org_units, total


class ListDeletedOrgUnitsUseCase:
    def __init__(self, queries: OrgUnitQueries):
        self.queries = queries

    async def execute(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
    ) -> Tuple[List[OrgUnit], int]:
        skip = (page - 1) * limit
        org_units = await self.queries.list_deleted(
            search=search, skip=skip, limit=limit
        )
        total = await self.queries.count_deleted(search=search)
        return org_units, total


class GetOrgUnitChildrenUseCase:
    def __init__(self, queries: OrgUnitQueries):
        self.queries = queries

    async def execute(
        self, org_unit_id: int, page: int = 1, limit: int = 10
    ) -> Tuple[List[OrgUnit], int]:
        skip = (page - 1) * limit
        org_units = await self.queries.get_children(
            parent_id=org_unit_id,
            recursive=False,
            skip=skip,
            limit=limit,
        )
        total = await self.queries.count_children(org_unit_id, recursive=False)
        return org_units, total


class GetOrgUnitTypesUseCase:
    def __init__(self, queries: OrgUnitQueries):
        self.queries = queries

    async def execute(self) -> List[str]:
        return await self.queries.get_unique_types()
