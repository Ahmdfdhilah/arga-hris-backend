"""
Dashboard request schemas
"""
from typing import Optional
from datetime import date
from pydantic import BaseModel, Field


class DashboardSummaryRequest(BaseModel):
    """Request schema untuk dashboard summary dengan optional filters"""

    target_date: Optional[date] = Field(
        None,
        description="Target date untuk dashboard data. Default: hari ini",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "target_date": "2025-12-04",
            }
        }


class DashboardWidgetRequest(BaseModel):
    """Request untuk fetch specific widget type"""

    widget_type: str = Field(
        ...,
        description="Type of widget: employee, hr_admin, org_unit_head, guest",
    )
    target_date: Optional[date] = Field(None, description="Target date for widget data")

    class Config:
        json_schema_extra = {
            "example": {
                "widget_type": "employee",
                "target_date": "2025-12-04",
            }
        }
