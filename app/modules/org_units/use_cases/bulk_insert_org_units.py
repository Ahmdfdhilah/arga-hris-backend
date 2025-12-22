from typing import List, Optional
from app.modules.org_units.repositories import OrgUnitQueries, OrgUnitCommands
from app.modules.employees.repositories import EmployeeQueries
from app.modules.org_units.schemas.requests import OrgUnitBulkItem
from app.modules.org_units.schemas.responses import BulkInsertResult
from app.core.messaging.event_publisher import EventPublisher
from app.modules.org_units.use_cases.create_org_unit import CreateOrgUnitUseCase


class BulkInsertOrgUnitsUseCase:
    def __init__(
        self,
        queries: OrgUnitQueries,
        commands: OrgUnitCommands,
        employee_queries: Optional[EmployeeQueries] = None,
        event_publisher: Optional[EventPublisher] = None,
    ):
        self.queries = queries
        self.commands = commands
        self.employee_queries = employee_queries
        self.event_publisher = event_publisher
        self.create_uc = CreateOrgUnitUseCase(
            queries, commands, employee_queries, event_publisher
        )

    async def execute(
        self, items: List[OrgUnitBulkItem], created_by: str, skip_errors: bool = False
    ) -> BulkInsertResult:
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

        root_items = [item for item in items if not item.parent_code]
        for item in root_items:
            try:
                existing = await self.queries.get_by_code(item.code)
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

                created = await self.create_uc.execute(
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
                
        if not skip_errors and result.error_count > 0:
            return result
        
        child_items = [item for item in items if item.parent_code]

        max_retries = 3
        for retry in range(max_retries):
            remaining_items = []

            for item in child_items:
                try:
                    existing = await self.queries.get_by_code(item.code)
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
                        parent = await self.queries.get_by_code(item.parent_code)
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

                    created = await self.create_uc.execute(
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

            if not skip_errors and result.error_count > 0:
                break

            child_items = remaining_items
            if not child_items:
                break

        return result
