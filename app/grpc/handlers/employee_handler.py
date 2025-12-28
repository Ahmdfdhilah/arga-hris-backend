"""
Employee gRPC Handler

Implements EmployeeService gRPC interface for HRIS master data.
"""

import logging
from typing import Tuple

import grpc

from proto.employee import employee_pb2, employee_pb2_grpc
from proto.common import common_pb2
from app.config.database import AsyncSessionLocal
from app.modules.employees.repositories import EmployeeQueries, EmployeeCommands
from app.modules.org_units.repositories import OrgUnitQueries
from app.modules.users.users.repositories import UserQueries, UserCommands
from app.modules.users.rbac.repositories.queries import RoleQueries
from app.modules.employees.services.employee_service import EmployeeService
from app.core.messaging import event_publisher
from app.grpc.converters import employee_to_proto
from app.core.exceptions import BadRequestException, NotFoundException

logger = logging.getLogger(__name__)


class EmployeeHandler(employee_pb2_grpc.EmployeeServiceServicer):
    """gRPC Handler for Employee master data operations."""

    async def _get_service(self):
        """Create EmployeeService with all dependencies."""
        session = AsyncSessionLocal()

        employee_queries = EmployeeQueries(session)
        employee_commands = EmployeeCommands(session)
        org_unit_queries = OrgUnitQueries(session)
        user_queries = UserQueries(session)
        user_commands = UserCommands(session)
        role_queries = RoleQueries(session)

        service = EmployeeService(
            queries=employee_queries,
            commands=employee_commands,
            org_unit_queries=org_unit_queries,
            user_queries=user_queries,
            user_commands=user_commands,
            role_queries=role_queries,
            event_publisher=event_publisher,
        )

        return service, session

    async def GetEmployee(
        self,
        request: employee_pb2.GetEmployeeRequest,
        context: grpc.aio.ServicerContext,
    ) -> employee_pb2.Employee:
        """Get employee by ID."""
        logger.info(f"gRPC GetEmployee called: {request.employee_id}")

        try:
            service, session = await self._get_service()
            async with session:
                employee = await service.get(request.employee_id)
                return employee_to_proto(employee)
        except BadRequestException as e:
            logger.warning(f"gRPC GetEmployee validation failed: {e}")
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except NotFoundException as e:
            logger.warning(f"gRPC GetEmployee not found: {e}")
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            logger.error(f"gRPC GetEmployee failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def GetEmployeeByNumber(
        self,
        request: employee_pb2.GetEmployeeByNumberRequest,
        context: grpc.aio.ServicerContext,
    ) -> employee_pb2.Employee:
        """Get employee by number (code)."""
        logger.info(f"gRPC GetEmployeeByNumber called: {request.employee_number}")

        try:
            service, session = await self._get_service()
            async with session:
                employee = await service.get_by_code(request.employee_number)
                if not employee:
                    await context.abort(
                        grpc.StatusCode.NOT_FOUND,
                        f"Employee dengan kode {request.employee_number} tidak ditemukan",
                    )

                return employee_to_proto(employee)
        except BadRequestException as e:
            logger.warning(f"gRPC GetEmployeeByNumber validation failed: {e}")
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except NotFoundException as e:
            logger.warning(f"gRPC GetEmployeeByNumber not found: {e}")
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            logger.error(f"gRPC GetEmployeeByNumber failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def GetEmployeeByEmail(
        self,
        request: employee_pb2.GetEmployeeByEmailRequest,
        context: grpc.aio.ServicerContext,
    ) -> employee_pb2.Employee:
        """Get employee by email."""
        logger.info(f"gRPC GetEmployeeByEmail called: {request.employee_email}")

        try:
            service, session = await self._get_service()
            async with session:
                employee = await service.get_by_email(request.employee_email)
                if not employee:
                    await context.abort(
                        grpc.StatusCode.NOT_FOUND,
                        f"Employee dengan email {request.employee_email} tidak ditemukan",
                    )

                return employee_to_proto(employee)
        except BadRequestException as e:
            logger.warning(f"gRPC GetEmployeeByEmail validation failed: {e}")
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except NotFoundException as e:
            logger.warning(f"gRPC GetEmployeeByEmail not found: {e}")
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            logger.error(f"gRPC GetEmployeeByEmail failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def ListEmployees(
        self,
        request: employee_pb2.ListEmployeesRequest,
        context: grpc.aio.ServicerContext,
    ) -> employee_pb2.ListEmployeesResponse:
        """List employees with pagination."""
        logger.info("gRPC ListEmployees called")

        try:
            service, session = await self._get_service()
            async with session:
                page = request.pagination.page if request.pagination.page > 0 else 1
                limit = request.pagination.limit if request.pagination.limit > 0 else 10

                employees, total_dict = await service.list(
                    page=page,
                    limit=limit,
                    search=request.search if request.HasField("search") else None,
                    org_unit_id=request.employee_org_unit_id
                    if request.HasField("employee_org_unit_id")
                    else None,
                    is_active=request.is_active
                    if request.HasField("is_active")
                    else None,
                )

                total = total_dict["total_items"]

                return employee_pb2.ListEmployeesResponse(
                    employees=[employee_to_proto(e) for e in employees],
                    pagination_info=common_pb2.PaginationInfo(
                        page=page,
                        limit=limit,
                        total_items=total,
                        total_pages=(total + limit - 1) // limit,
                    ),
                )
        except BadRequestException as e:
            logger.warning(f"gRPC ListEmployees validation failed: {e}")
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except Exception as e:
            logger.error(f"gRPC ListEmployees failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def CreateEmployee(
        self,
        request: employee_pb2.CreateEmployeeRequest,
        context: grpc.aio.ServicerContext,
    ) -> employee_pb2.Employee:
        """Create new employee."""
        logger.info(f"gRPC CreateEmployee called: {request.employee_number}")

        try:
            service, session = await self._get_service()
            async with session:
                # Parse name into first/last
                name_parts = request.employee_name.split(" ", 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ""

                employee = await service.create(
                    code=request.employee_number,  # Map employee_number to code
                    first_name=first_name,
                    last_name=last_name,
                    email=request.employee_email
                    if request.HasField("employee_email")
                    else "",
                    created_by=request.created_by,
                    phone=request.employee_phone
                    if request.HasField("employee_phone")
                    else None,
                    position=request.employee_position
                    if request.HasField("employee_position")
                    else None,
                    employee_type=request.employee_type
                    if request.HasField("employee_type")
                    else None,
                    gender=request.employee_gender
                    if request.HasField("employee_gender")
                    else None,
                    org_unit_id=request.employee_org_unit_id
                    if request.HasField("employee_org_unit_id")
                    else None,
                    supervisor_id=request.employee_supervisor_id
                    if request.HasField("employee_supervisor_id")
                    else None,
                )

                await session.commit()
                return employee_to_proto(employee)

        except BadRequestException as e:
            logger.warning(f"gRPC CreateEmployee validation failed: {e}")
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except NotFoundException as e:
            logger.warning(f"gRPC CreateEmployee not found: {e}")
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            logger.error(f"gRPC CreateEmployee failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def UpdateEmployee(
        self,
        request: employee_pb2.UpdateEmployeeRequest,
        context: grpc.aio.ServicerContext,
    ) -> employee_pb2.Employee:
        """Update employee."""
        logger.info(f"gRPC UpdateEmployee called: {request.employee_id}")

        try:
            service, session = await self._get_service()
            async with session:
                update_data = {}
                if request.HasField("employee_name"):
                    name_parts = request.employee_name.split(" ", 1)
                    update_data["first_name"] = name_parts[0]
                    update_data["last_name"] = (
                        name_parts[1] if len(name_parts) > 1 else ""
                    )

                if request.HasField("employee_phone"):
                    update_data["phone"] = request.employee_phone
                if request.HasField("employee_gender"):
                    update_data["gender"] = request.employee_gender
                if request.HasField("employee_position"):
                    update_data["position"] = request.employee_position
                if request.HasField("employee_type"):
                    update_data["type"] = request.employee_type
                if request.HasField("employee_org_unit_id"):
                    update_data["org_unit_id"] = request.employee_org_unit_id
                if request.HasField("employee_supervisor_id"):
                    update_data["supervisor_id"] = request.employee_supervisor_id
                if request.HasField("is_active"):
                    update_data["is_active"] = request.is_active

                employee = await service.update(
                    employee_id=request.employee_id,
                    updated_by=request.updated_by,
                    update_data=update_data,
                )

                await session.commit()
                return employee_to_proto(employee)

        except BadRequestException as e:
            logger.warning(f"gRPC UpdateEmployee validation failed: {e}")
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except NotFoundException as e:
            logger.warning(f"gRPC UpdateEmployee not found: {e}")
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            logger.error(f"gRPC UpdateEmployee failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def DeleteEmployee(
        self,
        request: employee_pb2.DeleteEmployeeRequest,
        context: grpc.aio.ServicerContext,
    ) -> common_pb2.StatusResponse:
        """Delete employee."""
        logger.info(f"gRPC DeleteEmployee called: {request.employee_id}")

        try:
            service, session = await self._get_service()
            async with session:
                await service.delete(request.employee_id, request.deleted_by)
                await session.commit()

                return common_pb2.StatusResponse(
                    success=True,
                    message=f"Employee {request.employee_id} berhasil dihapus",
                )
        except Exception as e:
            logger.error(f"gRPC DeleteEmployee failed: {e}")
            return common_pb2.StatusResponse(
                success=False,
                message=str(e),
            )

    async def BatchGetEmployees(
        self,
        request: employee_pb2.BatchGetEmployeesRequest,
        context: grpc.aio.ServicerContext,
    ) -> employee_pb2.ListEmployeesResponse:
        """Batch get employees by IDs."""
        logger.info(f"gRPC BatchGetEmployees called: {len(request.employee_ids)} IDs")

        try:
            service, session = await self._get_service()
            async with session:
                employees = []
                for emp_id in request.employee_ids:
                    try:
                        emp = await service.get(emp_id)
                        if emp:
                            employees.append(employee_to_proto(emp))
                    except NotFoundException:
                        continue

                return employee_pb2.ListEmployeesResponse(employees=employees)
        except Exception as e:
            logger.error(f"gRPC BatchGetEmployees failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def GetEmployeeSubordinates(
        self,
        request: employee_pb2.GetSubordinatesRequest,
        context: grpc.aio.ServicerContext,
    ) -> employee_pb2.ListEmployeesResponse:
        """Get employee subordinates."""
        logger.info(
            f"gRPC GetEmployeeSubordinates called: {request.employee_supervisor_id}"
        )

        try:
            service, session = await self._get_service()
            async with session:
                page = request.pagination.page if request.pagination.page > 0 else 1
                limit = request.pagination.limit if request.pagination.limit > 0 else 10

                employees, total_dict = await service.list_subordinates(
                    employee_id=request.employee_supervisor_id,
                    page=page,
                    limit=limit,
                    recursive=request.recursive,
                )

                total = total_dict["total_items"]

                return employee_pb2.ListEmployeesResponse(
                    employees=[employee_to_proto(e) for e in employees],
                    pagination_info=common_pb2.PaginationInfo(
                        page=page,
                        limit=limit,
                        total_items=total,
                        total_pages=(total + limit - 1) // limit,
                    ),
                )
        except NotFoundException as e:
            logger.warning(f"gRPC GetEmployeeSubordinates not found: {e}")
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            logger.error(f"gRPC GetEmployeeSubordinates failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def GetEmployeesByOrgUnit(
        self,
        request: employee_pb2.GetEmployeesByOrgUnitRequest,
        context: grpc.aio.ServicerContext,
    ) -> employee_pb2.ListEmployeesResponse:
        """Get employees by org unit."""
        logger.info(
            f"gRPC GetEmployeesByOrgUnit called: {request.employee_org_unit_id}"
        )

        try:
            service, session = await self._get_service()
            async with session:
                page = request.pagination.page if request.pagination.page > 0 else 1
                limit = request.pagination.limit if request.pagination.limit > 0 else 10

                employees, total_dict = await service.list_by_org_unit(
                    org_unit_id=request.employee_org_unit_id,
                    page=page,
                    limit=limit,
                    include_children=request.include_children,
                )

                total = total_dict["total_items"]

                return employee_pb2.ListEmployeesResponse(
                    employees=[employee_to_proto(e) for e in employees],
                    pagination_info=common_pb2.PaginationInfo(
                        page=page,
                        limit=limit,
                        total_items=total,
                        total_pages=(total + limit - 1) // limit,
                    ),
                )
        except NotFoundException as e:
            logger.warning(f"gRPC GetEmployeesByOrgUnit not found: {e}")
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            logger.error(f"gRPC GetEmployeesByOrgUnit failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def SoftDeleteEmployee(
        self,
        request: employee_pb2.SoftDeleteEmployeeRequest,
        context: grpc.aio.ServicerContext,
    ) -> employee_pb2.Employee:
        """Soft delete employee."""
        logger.info(f"gRPC SoftDeleteEmployee called: {request.employee_id}")

        try:
            service, session = await self._get_service()
            async with session:
                # Fetch employee before deletion to return it
                try:
                    emp_before = await service.get(request.employee_id)
                    await service.delete(
                        request.employee_id, request.deleted_by_user_id
                    )
                    await session.commit()
                    return employee_to_proto(emp_before)
                except Exception as e:
                    raise e

        except NotFoundException as e:
            logger.warning(f"gRPC SoftDeleteEmployee not found: {e}")
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            logger.error(f"gRPC SoftDeleteEmployee failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def RestoreEmployee(
        self,
        request: employee_pb2.RestoreEmployeeRequest,
        context: grpc.aio.ServicerContext,
    ) -> employee_pb2.Employee:
        """Restore soft-deleted employee."""
        logger.info(f"gRPC RestoreEmployee called: {request.employee_id}")

        try:
            service, session = await self._get_service()
            async with session:
                employee = await service.restore(request.employee_id)
                await session.commit()
                return employee_to_proto(employee)
        except NotFoundException as e:
            logger.warning(f"gRPC RestoreEmployee not found: {e}")
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            logger.error(f"gRPC RestoreEmployee failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def ListDeletedEmployees(
        self,
        request: employee_pb2.ListDeletedEmployeesRequest,
        context: grpc.aio.ServicerContext,
    ) -> employee_pb2.ListEmployeesResponse:
        """List soft-deleted employees."""
        logger.info("gRPC ListDeletedEmployees called")

        try:
            service, session = await self._get_service()
            async with session:
                page = request.pagination.page if request.pagination.page > 0 else 1
                limit = request.pagination.limit if request.pagination.limit > 0 else 10

                employees, total_dict = await service.list_deleted(
                    page=page,
                    limit=limit,
                    search=request.search if request.HasField("search") else None,
                )

                total = total_dict["total_items"]

                return employee_pb2.ListEmployeesResponse(
                    employees=[employee_to_proto(e) for e in employees],
                    pagination_info=common_pb2.PaginationInfo(
                        page=page,
                        limit=limit,
                        total_items=total,
                        total_pages=(total + limit - 1) // limit,
                    ),
                )
        except Exception as e:
            logger.error(f"gRPC ListDeletedEmployees failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))
