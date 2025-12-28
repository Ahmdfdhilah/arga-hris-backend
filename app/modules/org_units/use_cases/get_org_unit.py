from typing import Optional
from app.modules.org_units.models.org_unit import OrgUnit
from app.modules.org_units.repositories import OrgUnitQueries
from app.core.exceptions import NotFoundException


class GetOrgUnitUseCase:
    def __init__(self, queries: OrgUnitQueries):
        self.queries = queries

    async def execute(self, org_unit_id: int) -> OrgUnit:
        org_unit = await self.queries.get_by_id(org_unit_id)
        if not org_unit:
            raise NotFoundException(
                f"Organization unit with ID {org_unit_id} not found"
            )
        return org_unit


class GetOrgUnitByCodeUseCase:
    def __init__(self, queries: OrgUnitQueries):
        self.queries = queries

    async def execute(self, code: str) -> Optional[OrgUnit]:
        return await self.queries.get_by_code(code)
