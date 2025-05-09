from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ReportBase(BaseModel):
    report_type: str
    parameters: Optional[Dict[str, Any]] = None


class ReportRequest(ReportBase):
    run_async: bool = Field(True, description="Run the report generation in the background as a Celery task")


class ReportResponse(ReportBase):
    id: int
    status: str
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    file_path: Optional[str] = None
    user_id: int
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        orm_mode = True