import grpc
from typing import Optional, List, Dict, Any
from app.external_clients.grpc.base_client import BaseGRPCClient
from proto.org_unit import org_unit_pb2, org_unit_pb2_grpc
from proto.common import common_pb2
from app.modules.org_units.schemas.responses import (
    OrgUnitResponse,
)

class OrgUnitGRPCClient(BaseGRPCClient):
    def __init__(self):
        super().__init__("OrgUnitService")

    async def get_stub(self) -> org_unit_pb2_grpc.OrgUnitServiceStub:
        channel = await self.get_channel()
        return org_unit_pb2_grpc.OrgUnitServiceStub(channel)

    async def get_org_unit(self, org_unit_id: int) -> Dict[str, Any]:
        try:
            stub = await self.get_stub()
            request = org_unit_pb2.GetOrgUnitRequest(org_unit_id=org_unit_id)
            response = await stub.GetOrgUnit(request)
            return self._org_unit_to_dict(response)
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    async def get_org_unit_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        try:
            stub = await self.get_stub()
            request = org_unit_pb2.GetOrgUnitByCodeRequest(org_unit_code=code)
            response = await stub.GetOrgUnitByCode(request)
            return self._org_unit_to_dict(response)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            await self.handle_grpc_error(e)

    async def list_org_units(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        parent_id: Optional[int] = None,
        type_filter: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Dict[str, Any]:
        try:
            stub = await self.get_stub()
            pagination = common_pb2.Pagination(page=page, limit=limit)

            request = org_unit_pb2.ListOrgUnitsRequest(
                pagination=pagination,
                search=search,
                org_unit_parent_id=parent_id,
                org_unit_type=type_filter,
                is_active=is_active
            )

            response = await stub.ListOrgUnits(request)
            return {
                "org_units": [
                    self._org_unit_to_dict(org) for org in response.org_units
                ],
                "pagination": {
                    "page": response.pagination_info.page,
                    "limit": response.pagination_info.limit,
                    "total_items": response.pagination_info.total_items,
                    "total_pages": response.pagination_info.total_pages,
                },
            }
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    async def get_org_unit_children(
        self, org_unit_id: int, page: int = 1, limit: int = 10, recursive: bool = False
    ) -> Dict[str, Any]:
        try:
            stub = await self.get_stub()
            pagination = common_pb2.Pagination(page=page, limit=limit)

            request = org_unit_pb2.GetOrgUnitChildrenRequest(
                org_unit_parent_id=org_unit_id,
                recursive=recursive,
                pagination=pagination
            )

            response = await stub.GetOrgUnitChildren(request)
            return {
                "org_units": [
                    self._org_unit_to_dict(org) for org in response.org_units
                ],
                "pagination": {
                    "page": response.pagination_info.page,
                    "limit": response.pagination_info.limit,
                    "total_items": response.pagination_info.total_items,
                    "total_pages": response.pagination_info.total_pages,
                },
            }
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    async def get_org_unit_hierarchy(self, org_unit_id: Optional[int] = None, max_depth: int = 10) -> Dict[str, Any]:
        try:
            stub = await self.get_stub()
            request_params = {"max_depth": max_depth}
            if org_unit_id is not None:
                request_params["root_org_unit_id"] = org_unit_id

            request = org_unit_pb2.GetOrgUnitHierarchyRequest(**request_params)
            response = await stub.GetOrgUnitHierarchy(request)

            return {
                "root": self._org_unit_to_dict(response.root) if response.HasField("root") else None,
                "hierarchy": self._build_hierarchy(response.hierarchy)
            }
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    def _build_hierarchy(self, hierarchy_items) -> List[Dict[str, Any]]:
        result = []
        for item in hierarchy_items:
            result.append({
                "org_unit": self._org_unit_to_dict(item.org_unit),
                "children": self._build_hierarchy(item.children) if item.children else []
            })
        return result

    async def create_org_unit(
        self,
        org_unit_code: str,
        org_unit_name: str,
        org_unit_type: str,
        org_unit_level: int,
        org_unit_path: str,
        created_by: int,
        org_unit_parent_id: Optional[int] = None,
        org_unit_head_id: Optional[int] = None,
        org_unit_description: Optional[str] = None,
        org_unit_metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        try:
            stub = await self.get_stub()

            request_params = {
                "org_unit_code": org_unit_code,
                "org_unit_name": org_unit_name,
                "org_unit_type": org_unit_type,
                "org_unit_level": org_unit_level,
                "org_unit_path": org_unit_path,
                "created_by": created_by,
            }

            if org_unit_parent_id is not None:
                request_params["org_unit_parent_id"] = org_unit_parent_id
            if org_unit_head_id is not None:
                request_params["org_unit_head_id"] = org_unit_head_id
            if org_unit_description is not None:
                request_params["org_unit_description"] = org_unit_description
            if org_unit_metadata is not None:
                request_params["org_unit_metadata"] = org_unit_metadata

            request = org_unit_pb2.CreateOrgUnitRequest(**request_params)
            response = await stub.CreateOrgUnit(request)
            return self._org_unit_to_dict(response)
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    async def update_org_unit(
        self,
        org_unit_id: int,
        updated_by: int,
        org_unit_name: Optional[str] = None,
        org_unit_type: Optional[str] = None,
        org_unit_parent_id: Optional[int] = None,
        org_unit_level: Optional[int] = None,
        org_unit_path: Optional[str] = None,
        org_unit_head_id: Optional[int] = None,
        org_unit_description: Optional[str] = None,
        org_unit_metadata: Optional[Dict[str, str]] = None,
        is_active: Optional[bool] = None,
    ) -> Dict[str, Any]:
        try:
            stub = await self.get_stub()

            request = org_unit_pb2.UpdateOrgUnitRequest(
                org_unit_id=org_unit_id,
                updated_by=updated_by,
                org_unit_name=org_unit_name,
                org_unit_type=org_unit_type,
                org_unit_parent_id=org_unit_parent_id,
                org_unit_level=org_unit_level,
                org_unit_path=org_unit_path,
                org_unit_head_id=org_unit_head_id,
                org_unit_description=org_unit_description,
                org_unit_metadata=org_unit_metadata,
                is_active=is_active
            )
            response = await stub.UpdateOrgUnit(request)
            return self._org_unit_to_dict(response)
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    async def delete_org_unit(
        self,
        org_unit_id: int,
        deleted_by: int,
        soft_delete: bool = True,
    ) -> Dict[str, Any]:
        try:
            stub = await self.get_stub()
            request = org_unit_pb2.DeleteOrgUnitRequest(
                org_unit_id=org_unit_id,
                soft_delete=soft_delete,
                deleted_by=deleted_by,
            )
            response = await stub.DeleteOrgUnit(request)
            return {
                "success": response.success,
                "message": response.message,
            }
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    async def get_org_unit_types(self) -> List[str]:
        """
        Get all available org unit types from the backend

        Returns:
            List of org unit type strings
        """
        try:
            stub = await self.get_stub()
            request = org_unit_pb2.GetOrgUnitTypesRequest()
            response = await stub.GetOrgUnitTypes(request)
            return list(response.types)
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    async def soft_delete_org_unit(
        self,
        org_unit_id: int,
        deleted_by_user_id: int
    ) -> Dict[str, Any]:
        """Soft delete org unit via gRPC"""
        try:
            stub = await self.get_stub()
            request = org_unit_pb2.SoftDeleteOrgUnitRequest(
                org_unit_id=org_unit_id,
                deleted_by_user_id=deleted_by_user_id
            )
            response = await stub.SoftDeleteOrgUnit(request)
            return self._org_unit_to_dict(response)
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    async def restore_org_unit(self, org_unit_id: int) -> Dict[str, Any]:
        """Restore soft-deleted org unit via gRPC"""
        try:
            stub = await self.get_stub()
            request = org_unit_pb2.RestoreOrgUnitRequest(
                org_unit_id=org_unit_id
            )
            response = await stub.RestoreOrgUnit(request)
            return self._org_unit_to_dict(response)
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    async def list_deleted_org_units(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List deleted org units via gRPC"""
        try:
            stub = await self.get_stub()
            pagination = common_pb2.Pagination(page=page, limit=limit)
            request = org_unit_pb2.ListDeletedOrgUnitsRequest(
                pagination=pagination,
                search=search,
            )
            response = await stub.ListDeletedOrgUnits(request)
            return {
                "org_units": [
                    self._org_unit_to_dict(org) for org in response.org_units
                ],
                "pagination": {
                    "page": response.pagination_info.page,
                    "limit": response.pagination_info.limit,
                    "total_items": response.pagination_info.total_items,
                    "total_pages": response.pagination_info.total_pages,
                },
            }
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    def _org_unit_to_dict(self, org_unit: org_unit_pb2.OrgUnit) -> Dict[str, Any]:
        """Convert gRPC OrgUnit message to dict using Pydantic schema for validation"""
        data = {
            "id": org_unit.org_unit_id,
            "code": org_unit.org_unit_code,
            "name": org_unit.org_unit_name,
            "type": org_unit.org_unit_type,
            "parent_id": org_unit.org_unit_parent_id or None,
            "head_id": org_unit.org_unit_head_id or None,
            "level": org_unit.org_unit_level,
            "path": org_unit.org_unit_path,
            "description": org_unit.org_unit_description or None,
            "org_unit_metadata": dict(org_unit.org_unit_metadata) if org_unit.org_unit_metadata else None,
            "is_active": org_unit.is_active,
            "employee_count": org_unit.employee_count,
            "total_employee_count": org_unit.total_employee_count,
            "created_at": org_unit.created_at.ToJsonString() if org_unit.HasField("created_at") else None,
            "updated_at": org_unit.updated_at.ToJsonString() if org_unit.HasField("updated_at") else None,
            "created_by": org_unit.created_by if org_unit.created_by else None,
            "updated_by": org_unit.updated_by if org_unit.updated_by else None,
            "deleted_at": org_unit.deleted_at.ToJsonString() if org_unit.HasField("deleted_at") else None,
            "deleted_by": org_unit.deleted_by if org_unit.deleted_by else None,
        }

        if org_unit.HasField("parent"):
            data["parent"] = {
                "id": org_unit.parent.org_unit_id,
                "code": org_unit.parent.org_unit_code,
                "name": org_unit.parent.org_unit_name,
                "type": org_unit.parent.org_unit_type,
            }

        if org_unit.HasField("head"):
            data["head"] = {
                "id": org_unit.head.employee_id,
                "employee_number": org_unit.head.employee_number,
                "name": org_unit.head.employee_name,
                "position": org_unit.head.employee_position or None,
            }

        # Validate using Pydantic schema and return as dict
        validated = OrgUnitResponse.model_validate(data)
        return validated.model_dump()
