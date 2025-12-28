"""
OrgUnit gRPC Handler

Implements OrgUnitService gRPC interface for HRIS master data.
"""

import logging

import grpc

from proto.org_unit import org_unit_pb2, org_unit_pb2_grpc
from proto.common import common_pb2
from app.config.database import AsyncSessionLocal
from app.modules.org_units.repositories import OrgUnitQueries, OrgUnitCommands
from app.modules.employees.repositories import EmployeeQueries, EmployeeCommands
from app.modules.org_units.services.org_unit_service import OrgUnitService
from app.core.messaging import event_publisher
from app.grpc.converters import org_unit_to_proto
from app.core.exceptions import BadRequestException, NotFoundException

logger = logging.getLogger(__name__)


class OrgUnitHandler(org_unit_pb2_grpc.OrgUnitServiceServicer):
    """gRPC Handler for OrgUnit master data operations."""

    async def _get_service(self):
        """Create OrgUnitService with all dependencies."""
        session = AsyncSessionLocal()

        org_unit_queries = OrgUnitQueries(session)
        org_unit_commands = OrgUnitCommands(session)
        employee_queries = EmployeeQueries(session)
        employee_commands = EmployeeCommands(session)

        return OrgUnitService(
            queries=org_unit_queries,
            commands=org_unit_commands,
            employee_queries=employee_queries,
            employee_commands=employee_commands,
            event_publisher=event_publisher,
        ), session

    async def GetOrgUnit(
        self,
        request: org_unit_pb2.GetOrgUnitRequest,
        context: grpc.aio.ServicerContext,
    ) -> org_unit_pb2.OrgUnit:
        """Get org unit by ID."""
        logger.info(f"gRPC GetOrgUnit called: {request.org_unit_id}")

        try:
            service, session = await self._get_service()
            async with session:
                org_unit = await service.get_org_unit(request.org_unit_id)
                if not org_unit:
                    await context.abort(
                        grpc.StatusCode.NOT_FOUND,
                        f"OrgUnit {request.org_unit_id} tidak ditemukan",
                    )

                return org_unit_to_proto(org_unit)
        except BadRequestException as e:
            logger.warning(f"gRPC GetOrgUnit validation failed: {e}")
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except NotFoundException as e:
            logger.warning(f"gRPC GetOrgUnit not found: {e}")
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            logger.error(f"gRPC GetOrgUnit failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def GetOrgUnitByCode(
        self,
        request: org_unit_pb2.GetOrgUnitByCodeRequest,
        context: grpc.aio.ServicerContext,
    ) -> org_unit_pb2.OrgUnit:
        """Get org unit by code."""
        logger.info(f"gRPC GetOrgUnitByCode called: {request.org_unit_code}")

        try:
            service, session = await self._get_service()
            async with session:
                org_unit = await service.get_org_unit_by_code(request.org_unit_code)
                if not org_unit:
                    await context.abort(
                        grpc.StatusCode.NOT_FOUND,
                        f"OrgUnit dengan kode {request.org_unit_code} tidak ditemukan",
                    )

                return org_unit_to_proto(org_unit)
        except BadRequestException as e:
            logger.warning(f"gRPC GetOrgUnitByCode validation failed: {e}")
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except NotFoundException as e:
            logger.warning(f"gRPC GetOrgUnitByCode not found: {e}")
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            logger.error(f"gRPC GetOrgUnitByCode failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def ListOrgUnits(
        self,
        request: org_unit_pb2.ListOrgUnitsRequest,
        context: grpc.aio.ServicerContext,
    ) -> org_unit_pb2.ListOrgUnitsResponse:
        """List org units with pagination."""
        logger.info("gRPC ListOrgUnits called")

        try:
            service, session = await self._get_service()
            async with session:
                page = request.pagination.page if request.pagination.page > 0 else 1
                limit = request.pagination.limit if request.pagination.limit > 0 else 10

                org_units, total = await service.list_org_units(
                    page=page,
                    limit=limit,
                    search=request.search if request.HasField("search") else None,
                    parent_id=request.org_unit_parent_id
                    if request.HasField("org_unit_parent_id")
                    else None,
                    type_filter=request.org_unit_type
                    if request.HasField("org_unit_type")
                    else None,
                )

                return org_unit_pb2.ListOrgUnitsResponse(
                    org_units=[org_unit_to_proto(ou) for ou in org_units],
                    pagination_info=common_pb2.PaginationInfo(
                        page=page,
                        limit=limit,
                        total_items=total,
                        total_pages=(total + limit - 1) // limit,
                    ),
                )
        except BadRequestException as e:
            logger.warning(f"gRPC ListOrgUnits validation failed: {e}")
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except Exception as e:
            logger.error(f"gRPC ListOrgUnits failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def CreateOrgUnit(
        self,
        request: org_unit_pb2.CreateOrgUnitRequest,
        context: grpc.aio.ServicerContext,
    ) -> org_unit_pb2.OrgUnit:
        """Create new org unit."""
        logger.info(f"gRPC CreateOrgUnit called: {request.org_unit_code}")

        try:
            service, session = await self._get_service()
            async with session:
                org_unit = await service.create_org_unit(
                    code=request.org_unit_code,
                    name=request.org_unit_name,
                    type=request.org_unit_type,
                    created_by=request.created_by,
                    parent_id=request.org_unit_parent_id
                    if request.HasField("org_unit_parent_id")
                    else None,
                    head_id=request.org_unit_head_id
                    if request.HasField("org_unit_head_id")
                    else None,
                    description=request.org_unit_description
                    if request.HasField("org_unit_description")
                    else None,
                )

                await session.commit()
                return org_unit_to_proto(org_unit)

        except BadRequestException as e:
            logger.warning(f"gRPC CreateOrgUnit validation failed: {e}")
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except NotFoundException as e:
            logger.warning(f"gRPC CreateOrgUnit not found: {e}")
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            logger.error(f"gRPC CreateOrgUnit failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def UpdateOrgUnit(
        self,
        request: org_unit_pb2.UpdateOrgUnitRequest,
        context: grpc.aio.ServicerContext,
    ) -> org_unit_pb2.OrgUnit:
        """Update org unit."""
        logger.info(f"gRPC UpdateOrgUnit called: {request.org_unit_id}")

        try:
            service, session = await self._get_service()
            async with session:
                org_unit = await service.update_org_unit(
                    org_unit_id=request.org_unit_id,
                    updated_by=request.updated_by,
                    name=request.org_unit_name
                    if request.HasField("org_unit_name")
                    else None,
                    type=request.org_unit_type
                    if request.HasField("org_unit_type")
                    else None,
                    parent_id=request.org_unit_parent_id
                    if request.HasField("org_unit_parent_id")
                    else None,
                    head_id=request.org_unit_head_id
                    if request.HasField("org_unit_head_id")
                    else None,
                    description=request.org_unit_description
                    if request.HasField("org_unit_description")
                    else None,
                    is_active=request.is_active
                    if request.HasField("is_active")
                    else None,
                )

                await session.commit()
                return org_unit_to_proto(org_unit)

        except BadRequestException as e:
            logger.warning(f"gRPC UpdateOrgUnit validation failed: {e}")
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except NotFoundException as e:
            logger.warning(f"gRPC UpdateOrgUnit not found: {e}")
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            logger.error(f"gRPC UpdateOrgUnit failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def DeleteOrgUnit(
        self,
        request: org_unit_pb2.DeleteOrgUnitRequest,
        context: grpc.aio.ServicerContext,
    ) -> common_pb2.StatusResponse:
        """Delete org unit."""
        logger.info(f"gRPC DeleteOrgUnit called: {request.org_unit_id}")

        try:
            service, session = await self._get_service()
            async with session:
                await service.soft_delete_org_unit(
                    request.org_unit_id, request.deleted_by
                )
                await session.commit()

                return common_pb2.StatusResponse(
                    success=True,
                    message=f"OrgUnit {request.org_unit_id} berhasil dihapus",
                )
        except Exception as e:
            logger.error(f"gRPC DeleteOrgUnit failed: {e}")
            return common_pb2.StatusResponse(
                success=False,
                message=str(e),
            )

    async def GetOrgUnitChildren(
        self,
        request: org_unit_pb2.GetOrgUnitChildrenRequest,
        context: grpc.aio.ServicerContext,
    ) -> org_unit_pb2.ListOrgUnitsResponse:
        """Get org unit children."""
        logger.info(f"gRPC GetOrgUnitChildren called: {request.org_unit_parent_id}")

        try:
            service, session = await self._get_service()
            async with session:
                page = request.pagination.page if request.pagination.page > 0 else 1
                limit = request.pagination.limit if request.pagination.limit > 0 else 10

                org_units, total = await service.get_org_unit_children(
                    org_unit_id=request.org_unit_parent_id,
                    page=page,
                    limit=limit,
                )

                return org_unit_pb2.ListOrgUnitsResponse(
                    org_units=[org_unit_to_proto(ou) for ou in org_units],
                    pagination_info=common_pb2.PaginationInfo(
                        page=page,
                        limit=limit,
                        total_items=total,
                        total_pages=(total + limit - 1) // limit,
                    ),
                )
        except NotFoundException as e:
            logger.warning(f"gRPC GetOrgUnitChildren not found: {e}")
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            logger.error(f"gRPC GetOrgUnitChildren failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def GetOrgUnitHierarchy(
        self,
        request: org_unit_pb2.GetOrgUnitHierarchyRequest,
        context: grpc.aio.ServicerContext,
    ) -> org_unit_pb2.OrgUnitHierarchy:
        """Get org unit hierarchy tree."""
        logger.info("gRPC GetOrgUnitHierarchy called")

        try:
            service, session = await self._get_service()
            async with session:
                root_id = (
                    request.root_org_unit_id
                    if request.HasField("root_org_unit_id")
                    else None
                )
                hierarchy = await service.get_org_unit_hierarchy(org_unit_id=root_id)

                # Convert to proto hierarchy
                def convert_to_hierarchy(node) -> org_unit_pb2.OrgUnitHierarchy:
                    proto = org_unit_pb2.OrgUnitHierarchy(
                        org_unit=org_unit_to_proto(node["unit"])
                        if "unit" in node
                        else org_unit_to_proto(node),
                    )
                    if "children" in node:
                        for child in node["children"]:
                            proto.children.append(convert_to_hierarchy(child))
                    return proto

                if hierarchy:
                    return convert_to_hierarchy(hierarchy)
                return org_unit_pb2.OrgUnitHierarchy()

        except NotFoundException as e:
            logger.warning(f"gRPC GetOrgUnitHierarchy not found: {e}")
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            logger.error(f"gRPC GetOrgUnitHierarchy failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def BatchGetOrgUnits(
        self,
        request: org_unit_pb2.BatchGetOrgUnitsRequest,
        context: grpc.aio.ServicerContext,
    ) -> org_unit_pb2.ListOrgUnitsResponse:
        """Batch get org units by IDs."""
        logger.info(f"gRPC BatchGetOrgUnits called: {len(request.org_unit_ids)} IDs")

        try:
            service, session = await self._get_service()
            async with session:
                org_units = []
                for ou_id in request.org_unit_ids:
                    ou = await service.get_org_unit(ou_id)
                    if ou:
                        org_units.append(org_unit_to_proto(ou))

                return org_unit_pb2.ListOrgUnitsResponse(org_units=org_units)
        except Exception as e:
            logger.error(f"gRPC BatchGetOrgUnits failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def GetOrgUnitTypes(
        self,
        request: org_unit_pb2.GetOrgUnitTypesRequest,
        context: grpc.aio.ServicerContext,
    ) -> org_unit_pb2.GetOrgUnitTypesResponse:
        """Get all org unit types."""
        logger.info("gRPC GetOrgUnitTypes called")

        try:
            service, session = await self._get_service()
            async with session:
                types = await service.get_org_unit_types()
                return org_unit_pb2.GetOrgUnitTypesResponse(types=types)
        except Exception as e:
            logger.error(f"gRPC GetOrgUnitTypes failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def GetOrgUnitAncestors(
        self,
        request: org_unit_pb2.GetOrgUnitAncestorsRequest,
        context: grpc.aio.ServicerContext,
    ) -> org_unit_pb2.ListOrgUnitsResponse:
        """Get org unit ancestors (path to root)."""
        logger.info(f"gRPC GetOrgUnitAncestors called: {request.org_unit_id}")

        try:
            service, session = await self._get_service()
            async with session:
                org_unit = await service.get_org_unit(request.org_unit_id)
                if not org_unit:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(
                        f"OrgUnit {request.org_unit_id} tidak ditemukan"
                    )
                    return org_unit_pb2.ListOrgUnitsResponse()

                # Walk up the tree
                ancestors = []
                current = org_unit.parent
                while current:
                    ancestors.append(org_unit_to_proto(current))
                    current = current.parent

                return org_unit_pb2.ListOrgUnitsResponse(org_units=ancestors)
        except NotFoundException as e:
            logger.warning(f"gRPC GetOrgUnitAncestors not found: {e}")
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            logger.error(f"gRPC GetOrgUnitAncestors failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def SoftDeleteOrgUnit(
        self,
        request: org_unit_pb2.SoftDeleteOrgUnitRequest,
        context: grpc.aio.ServicerContext,
    ) -> org_unit_pb2.OrgUnit:
        """Soft delete org unit."""
        logger.info(f"gRPC SoftDeleteOrgUnit called: {request.org_unit_id}")

        try:
            service, session = await self._get_service()
            async with session:
                org_unit = await service.soft_delete_org_unit(
                    request.org_unit_id,
                    request.deleted_by_user_id,
                )
                await session.commit()
                return org_unit_to_proto(org_unit)
        except NotFoundException as e:
            logger.warning(f"gRPC SoftDeleteOrgUnit not found: {e}")
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            logger.error(f"gRPC SoftDeleteOrgUnit failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def RestoreOrgUnit(
        self,
        request: org_unit_pb2.RestoreOrgUnitRequest,
        context: grpc.aio.ServicerContext,
    ) -> org_unit_pb2.OrgUnit:
        """Restore soft-deleted org unit."""
        logger.info(f"gRPC RestoreOrgUnit called: {request.org_unit_id}")

        try:
            service, session = await self._get_service()
            async with session:
                org_unit = await service.restore_org_unit(request.org_unit_id)
                await session.commit()
                return org_unit_to_proto(org_unit)
        except NotFoundException as e:
            logger.warning(f"gRPC RestoreOrgUnit not found: {e}")
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            logger.error(f"gRPC RestoreOrgUnit failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def ListDeletedOrgUnits(
        self,
        request: org_unit_pb2.ListDeletedOrgUnitsRequest,
        context: grpc.aio.ServicerContext,
    ) -> org_unit_pb2.ListOrgUnitsResponse:
        """List soft-deleted org units."""
        logger.info("gRPC ListDeletedOrgUnits called")

        try:
            service, session = await self._get_service()
            async with session:
                page = request.pagination.page if request.pagination.page > 0 else 1
                limit = request.pagination.limit if request.pagination.limit > 0 else 10

                org_units, total = await service.list_deleted_org_units(
                    page=page,
                    limit=limit,
                    search=request.search if request.HasField("search") else None,
                )

                return org_unit_pb2.ListOrgUnitsResponse(
                    org_units=[org_unit_to_proto(ou) for ou in org_units],
                    pagination_info=common_pb2.PaginationInfo(
                        page=page,
                        limit=limit,
                        total_items=total,
                        total_pages=(total + limit - 1) // limit,
                    ),
                )
        except Exception as e:
            logger.error(f"gRPC ListDeletedOrgUnits failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))
