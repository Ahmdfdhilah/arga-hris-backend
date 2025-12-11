from typing import Annotated
from fastapi import Depends
from app.external_clients.grpc.org_unit_client import OrgUnitGRPCClient
from app.modules.org_units.services.org_unit_service import OrgUnitService


def get_org_unit_grpc_client() -> OrgUnitGRPCClient:
    return OrgUnitGRPCClient()


OrgUnitGRPCClientDep = Annotated[OrgUnitGRPCClient, Depends(get_org_unit_grpc_client)]


def get_org_unit_service(client: OrgUnitGRPCClientDep) -> OrgUnitService:
    return OrgUnitService(client)


OrgUnitServiceDep = Annotated[OrgUnitService, Depends(get_org_unit_service)]
